import time
from concurrent.futures import ThreadPoolExecutor

from .config import CAMERAS, INTERVAL, DEBUG_MODE, DEBUG_ITERATIONS, PICTURES_DIR
from .downloader import download_image
from .video import create_daily_video
from .timeutils import log, day_folder_name


def combine_day(day: str):
    for code in CAMERAS:
        create_daily_video(code, day)

    day_path = PICTURES_DIR / day
    if day_path.exists() and not any(day_path.iterdir()):
        day_path.rmdir()
        log(f"Day folder deleted: {day}")
    else:
        log(f"Day folder not empty: {day}")

    log(f"Done daily combine + cleanup for {day}")


def run_loop():
    log("====== Starting Recorder ======")
    log(f"Interval: {INTERVAL}s")

    current_day = None
    loop_counter = 0

    while True:
        loop_start = time.time()
        today = day_folder_name()

        if current_day and today != current_day:
            log(f"New day detected. Combining {current_day}")
            combine_day(current_day)
            current_day = today
        elif current_day is None:
            current_day = today

        log("Downloading webcam images...")

        with ThreadPoolExecutor(max_workers=8) as pool:
            for code, url in CAMERAS.items():
                pool.submit(download_image, code, url)

        log("Downloaded webcam images")

        loop_counter += 1

        if DEBUG_MODE and loop_counter % DEBUG_ITERATIONS == 0:
            log("Debug mode triggered video creation")
            combine_day(current_day)

        elapsed = time.time() - loop_start
        sleep_time = INTERVAL - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
