import time
from threading import Thread

from ..config.settings import PICTURES_DIR, VIDEOS_DIR, INTERVAL
from ..config.webcams import CAMERA_URLS, CameraID
from ..io.webcam import download_webcam_image
from ..io.video import create_daily_video
from ..utils import day_folder_name
from ..ui.state import camera_state, state_lock, CameraState, DownloadState, VideoState
from ..ui.dashboard import ui_loop


def combine_day(day: str, cam_id: CameraID):
    """Create daily videos and update UI state."""

    with state_lock:
        camera_state[cam_id].video_create_start_time = time.time()
        camera_state[cam_id].video_state = VideoState.ENCODING

    try:
        create_daily_video(cam_id.name.lower(), day)
    finally:
        with state_lock:
            camera_state[cam_id].video_create_start_time = None
            camera_state[cam_id].video_state = VideoState.IDLE

    # Cleanup empty day folder.
    day_path = PICTURES_DIR / day
    try:
        if day_path.exists() and not any(day_path.iterdir()):
            day_path.rmdir()
    except FileNotFoundError:
        pass


def camera_loop(cam_id: CameraID, url: str):
    next_run = time.time()
    current_day = day_folder_name()

    while True:
        now = time.time()

        # Sleeping phase.
        if now < next_run:
            with state_lock:
                camera_state[cam_id].download_state = DownloadState.SLEEPING
            time.sleep(next_run - now)

        # Downloading phase.
        start = time.time()
        with state_lock:
            camera_state[cam_id].download_state = DownloadState.DOWNLOADING
            camera_state[cam_id].download_start_time = start
            camera_state[cam_id].next_run_time = start + INTERVAL

        try:
            download_webcam_image(cam_id.name.lower(), url)
            with state_lock:
                camera_state[cam_id].error = None
        except Exception as e:
            with state_lock:
                camera_state[cam_id].error = f"{type(e).__name__}: {str(e) if str(e) != 'None' else '(No Description)'}"

        elapsed = time.time() - start
        with state_lock:
            camera_state[cam_id].last_download_elapsed_time = elapsed
            camera_state[cam_id].download_start_time = None

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
    """Start camera threads and run UI loop. The UI loop is blocking."""
    
    init_loop()

    # Initialize state and start threads.
    for cam_id, url in CAMERA_URLS.items():
        with state_lock:
            camera_state[cam_id] = CameraState()

        Thread(target=camera_loop, args=(cam_id, url), daemon=True).start()

    # UI loop (blocking).
    try:
        ui_loop()
    except KeyboardInterrupt:
        pass
