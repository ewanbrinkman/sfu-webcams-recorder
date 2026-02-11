"""The main program loops."""

import time
from threading import Thread

import requests

from sfu_webcams_recorder.config.settings import PICTURES_DIR, VIDEOS_DIR, INTERVAL
from sfu_webcams_recorder.config.webcams import WEBCAM_URLS, WebcamID
from sfu_webcams_recorder.io.webcam import download_webcam_image, DuplicateWebcamImageError
from sfu_webcams_recorder.io.video import create_daily_video
from sfu_webcams_recorder.utils import day_folder_name
from sfu_webcams_recorder.ui.state import (
    webcam_state,
    state_lock,
    WebcamState,
    DownloadState,
    VideoState
)
from sfu_webcams_recorder.ui.dashboard import ui_loop


def combine_day(day: str, cam_id: WebcamID):
    """Create daily videos and update UI state."""

    with state_lock:
        webcam_state[cam_id].video_create_start_time = time.time()
        webcam_state[cam_id].video_state = VideoState.ENCODING

    try:
        create_daily_video(cam_id.name.lower(), day)
    finally:
        with state_lock:
            webcam_state[cam_id].video_create_start_time = None
            webcam_state[cam_id].video_state = VideoState.IDLE

    # Cleanup empty day folder.
    day_path = PICTURES_DIR / day
    try:
        if day_path.exists() and not any(day_path.iterdir()):
            day_path.rmdir()
    except FileNotFoundError:
        pass


def webcam_loop(cam_id: WebcamID, url: str):
    next_run = time.time()
    current_day = day_folder_name()

    while True:
        now = time.time()

        # Sleeping phase.
        if now < next_run:
            with state_lock:
                webcam_state[cam_id].download_state = DownloadState.SLEEPING
            time.sleep(next_run - now)

        # Downloading phase.
        start = time.time()
        with state_lock:
            webcam_state[cam_id].download_state = DownloadState.DOWNLOADING
            webcam_state[cam_id].download_start_time = start
            webcam_state[cam_id].next_run_time = start + INTERVAL

        try:
            download_webcam_image(cam_id.name.lower(), url)
            with state_lock:
                webcam_state[cam_id].error = None
        except (requests.RequestException, OSError, DuplicateWebcamImageError) as e:
            with state_lock:
                webcam_state[cam_id].error = f"{type(e).__name__}: {str(e) if str(e) != 'None' else '(No Description)'}"

        elapsed = time.time() - start
        with state_lock:
            webcam_state[cam_id].last_download_elapsed_time = elapsed
            webcam_state[cam_id].download_start_time = None

        # Detect new day.
        updated_day = day_folder_name()
        if updated_day != current_day:
            Thread(target=combine_day, args=(current_day, cam_id), daemon=True).start()
            current_day = updated_day

        # Schedule next run.
        now = time.time()
        if elapsed > INTERVAL:
            next_run = now
        else:
            next_run += INTERVAL


def init_loop():
    PICTURES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def run_loop():
    """Start webcam threads and run UI loop. The UI loop is blocking."""
    
    init_loop()

    # Initialize state and start threads.
    for cam_id, url in WEBCAM_URLS.items():
        with state_lock:
            webcam_state[cam_id] = WebcamState()

        Thread(target=webcam_loop, args=(cam_id, url), daemon=True).start()

    # UI loop (blocking).
    try:
        ui_loop()
    except KeyboardInterrupt:
        pass
