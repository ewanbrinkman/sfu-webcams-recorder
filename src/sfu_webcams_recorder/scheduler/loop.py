import time
from threading import Thread

from ..config import PICTURES_DIR, VIDEOS_DIR, CAMERAS, INTERVAL
from ..downloader.image import download_image
from ..video.create_daily_video import create_daily_video
from ..utils import day_folder_name
from ..ui.state import camera_state, state_lock
from ..ui.dashboard import ui_loop


def combine_day(day: str, code: str):
    """Create daily videos and update UI state."""

    with state_lock:
        camera_state[code]["video_start"] = time.time()

    try:
        create_daily_video(code, day)
    finally:
        with state_lock:
            camera_state[code]["video_start"] = None

    # cleanup empty day folder
    day_path = PICTURES_DIR / day
    try:
        if day_path.exists() and not any(day_path.iterdir()):
            day_path.rmdir()
    except FileNotFoundError:
        pass


def camera_loop(code: str, url: str):

    next_run = time.time()
    current_day = day_folder_name()

    while True:
        now = time.time()

        # sleeping phase
        if now < next_run:
            with state_lock:
                camera_state[code]["status"] = "Sleeping"
                camera_state[code]["next_run"] = next_run
            time.sleep(next_run - now)

        # downloading phase
        start = time.time()
        with state_lock:
            camera_state[code]["status"] = "Downloading"
            camera_state[code]['download_start_time'] = start
            camera_state[code]["next_run"] = 0

        try:
            download_image(code, url)
            # raise TabError
            with state_lock:
                camera_state[code]["error"] = None
        except Exception as e:
            with state_lock:
                camera_state[code]["error"] = f"{type(e).__name__}: {str(e) if str(e) != "None" else "(No Description)"}"

        elapsed = time.time() - start

        with state_lock:
            camera_state[code]["last_elapsed"] = elapsed
            camera_state[code]['download_start_time'] = None

        # detect new day
        updated_day = day_folder_name()
        if updated_day != current_day:
            Thread(
                target=combine_day,
                args=(current_day, code),
                daemon=True,
            ).start()
            current_day = updated_day

        # schedule next run
        now = time.time()
        if elapsed > INTERVAL:
            next_run = now
        else:
            next_run += INTERVAL


def init_loop():
    PICTURES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def run_loop():
    init_loop()

    # initialize state + threads
    for code, url in CAMERAS.items():
        with state_lock:
            camera_state[code] = {
                "status": "Starting",
                "download_start_time": None,
                "last_elapsed": None,
                "next_run": None,
                "video_start": None,
                "error": None,
            }

        Thread(target=camera_loop, args=(code, url), daemon=True).start()

    # UI loop (blocking)
    ui_loop()
