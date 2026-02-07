import time
from threading import Thread

from .config import CAMERAS, INTERVAL, DEBUG_MODE, DEBUG_ITERATIONS, PICTURES_DIR
from .download_image import download_image
from .create_daily_video import create_daily_video
from .timeutils import log, day_folder_name


def combine_day(day: str):
    """Create daily videos for all cameras and clean up empty folders."""
    for code in CAMERAS:
        create_daily_video(code, day)

    day_path = PICTURES_DIR / day
    if day_path.exists() and not any(day_path.iterdir()):
        day_path.rmdir()
        log(f"Day folder deleted: {day}")
    else:
        log(f"Day folder not empty: {day}")

    log(f"Done daily combine + cleanup for {day}")


def camera_loop(code: str, url: str):
    """
    Independent loop for a single camera.
    Downloads every INTERVAL seconds; waits remaining time if download finishes early,
    or starts immediately if download takes longer than INTERVAL.
    """
    next_run = time.time()

    while True:
        now = time.time()
        if now < next_run:
            time.sleep(next_run - now)

        start = time.time() 
        log(f"Downloading {code}...")
        try:
            download_image(code, url)
        except Exception as e:
            log(f"Error downloading {code}: {e}")
        log(f"Done downloading {code}")

        # Schedule next run
        next_run += INTERVAL
        elapsed = time.time() - start
        if elapsed > INTERVAL:
            # Download took longer than interval → next run immediately
            next_run = time.time()


def run_loop():
    """
    Start independent loops for all cameras.
    Handles daily combine for completed days in the background.
    """
    log("====== Starting Independent Recorder ======")
    log(f"Interval per camera: {INTERVAL}s")

    current_day = day_folder_name()
    loop_counter = 0

    # Start independent threads for each camera
    threads = []
    for code, url in CAMERAS.items():
        t = Thread(target=camera_loop, args=(code, url), daemon=True)
        t.start()
        threads.append(t)

    # Main loop for daily video creation & debug handling
    try:
        while True:
            time.sleep(1)
            today = day_folder_name()

            # Day rollover check
            if today != current_day:
                log(f"New day detected. Combining {current_day}")
                combine_day(current_day)
                current_day = today

            loop_counter += 1

            # Debug mode: trigger combine every DEBUG_ITERATIONS iterations
            if DEBUG_MODE and loop_counter % DEBUG_ITERATIONS == 0:
                log("Debug mode triggered daily combine")
                combine_day(current_day)

    except KeyboardInterrupt:
        log("Shutting down recorder...")
