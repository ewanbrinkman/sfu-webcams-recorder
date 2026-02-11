"""The main program loops."""

import time
from threading import Thread
import logging

import requests

from sfu_webcams_recorder.config.settings import (
    PICTURES_DIR,
    VIDEOS_DIR,
    LOG_DIR,
    SNAPSHOT_DIR,
    INTERVAL,
    DEBUG_VIDEO_CREATE,
    DEBUG_SNAPSHOT_LOG,
    DEBUG_SNAPSHOT_LOG_SECONDS,
)
from sfu_webcams_recorder.config.webcams import WEBCAM_URLS, WebcamID
from sfu_webcams_recorder.io.webcam import (
    download_webcam_image,
    DuplicateWebcamImageError,
)
from sfu_webcams_recorder.io.video import create_daily_video
from sfu_webcams_recorder.utils import day_folder_name
from sfu_webcams_recorder.ui.state import (
    program_state,
    WebcamState,
    DownloadState,
    VideoState,
)
from sfu_webcams_recorder.ui.dashboard import ui_loop, save_dashboard_snapshot


logger = logging.getLogger(__name__)


def combine_day(day: str, cam_id: WebcamID):
    """Create daily videos and update UI state."""

    with program_state.lock:
        program_state.webcam_state[cam_id].video_create_start_time = time.time()
        program_state.webcam_state[cam_id].video_state = VideoState.ENCODING

    try:
        create_daily_video(cam_id.name.lower(), day)
    finally:
        with program_state.lock:
            program_state.webcam_state[cam_id].video_create_start_time = None
            program_state.webcam_state[cam_id].video_state = VideoState.IDLE

    # Cleanup empty day folder.
    day_path = PICTURES_DIR / day
    try:
        if day_path.exists() and not any(day_path.iterdir()):
            day_path.rmdir()
    except FileNotFoundError:
        pass


def webcam_loop(cam_id: WebcamID, url: str):
    """The main loop for each webcam."""
    next_run = time.time()
    current_day = day_folder_name()

    debug_video_create_triggered = False

    while True:
        now = time.time()

        # Sleeping phase.
        if now < next_run:
            with program_state.lock:
                program_state.webcam_state[
                    cam_id
                ].download_state = DownloadState.SLEEPING
            time.sleep(next_run - now)

        # Downloading phase.
        start = time.time()
        with program_state.lock:
            program_state.webcam_state[
                cam_id
            ].download_state = DownloadState.DOWNLOADING
            program_state.webcam_state[cam_id].download_start_time = start
            program_state.webcam_state[cam_id].next_run_time = start + INTERVAL

        try:
            download_webcam_image(cam_id.name.lower(), url)
            with program_state.lock:
                program_state.webcam_state[cam_id].error = None
        except (requests.RequestException, OSError, DuplicateWebcamImageError) as e:
            with program_state.lock:
                program_state.webcam_state[
                    cam_id
                ].error = f"{type(e).__name__}: {str(e) if str(e) != 'None' else '(No Description)'}"

        elapsed = time.time() - start
        with program_state.lock:
            program_state.webcam_state[cam_id].last_download_elapsed_time = elapsed
            program_state.webcam_state[cam_id].download_start_time = None

        # Detect new day.
        updated_day = day_folder_name()
        if updated_day != current_day or (
            not debug_video_create_triggered and DEBUG_VIDEO_CREATE
        ):
            # Add job to queue and notify worker
            with program_state.video_condition:
                program_state.video_queue.put((current_day, cam_id))
                program_state.video_condition.notify()

            current_day = updated_day

            debug_video_create_triggered = True

        # Schedule next run.
        now = time.time()
        if elapsed > INTERVAL:
            next_run = now
        else:
            next_run += INTERVAL


def video_worker_loop():
    """Worker that processes video creation jobs one at a time."""
    while True:
        with program_state.video_condition:
            while program_state.video_queue.empty():
                # Wait until a job is added.
                program_state.video_condition.wait()

            day, cam_id = program_state.video_queue.get()

        # Update UI and run encode.
        combine_day(day, cam_id)
        program_state.video_queue.task_done()


def snapshot_loop():
    """Save dashboard snapshot every hour on the hour."""
    while True:
        now = time.time()

        # Seconds until next hour boundary if debug is not enabled.
        sleep_time = (
            DEBUG_SNAPSHOT_LOG_SECONDS
            if DEBUG_SNAPSHOT_LOG
            else 3600 - (int(now) % 3600)
        )
        time.sleep(sleep_time)

        try:
            save_dashboard_snapshot()
        except OSError as e:
            logger.exception("Snapshot failed: %s", e)


def init_loop():
    """Set up logging and needed directories."""
    # For media.
    PICTURES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    # For logging.
    LOG_DIR.mkdir(exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Set up logging.
    logging.basicConfig(
        filename=LOG_DIR / "log.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def run_loop():
    """Start webcam threads and run UI loop. The UI loop is blocking."""

    init_loop()

    logger.info("Program starting")

    # Start video worker.
    Thread(target=video_worker_loop, daemon=True).start()
    # Start logging snapshots.
    Thread(target=snapshot_loop, daemon=True).start()

    # Initialize state and start threads.
    for cam_id, url in WEBCAM_URLS.items():
        with program_state.lock:
            program_state.webcam_state[cam_id] = WebcamState()

        Thread(target=webcam_loop, args=(cam_id, url), daemon=True).start()

    # UI loop (blocking).
    try:
        ui_loop()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Program shutting down")
