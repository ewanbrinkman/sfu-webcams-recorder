import time
from threading import Thread

from ..config import PICTURES_DIR, VIDEOS_DIR, CAMERAS, INTERVAL, PICTURES_DIR
from ..downloader.image import download_image
from ..video.create_daily_video import create_daily_video
from ..utils import log, day_folder_name, debug_enabled


def combine_day(day: str, code: str):
    """Create daily videos for a webcam and clean up empty day folders."""
    
    create_daily_video(code, day)

    try:
        day_path = PICTURES_DIR / day
        if day_path.exists() and not any(day_path.iterdir()):
            day_path.rmdir()
            log(f"Day folder deleted: {day}")
        else:
            log(f"Day folder not empty: {day}")
    except FileNotFoundError:
        # Another camera thread already deleted the folder.
        pass


def camera_loop(code: str, url: str):
    """
    Independent thread for continuously downloading images for a single camera.
    
    Downloads every INTERVAL seconds; waits remaining time if download finishes early,
    or starts immediately if download takes longer than INTERVAL.
    """
    
    video_creation_threads = []
    next_run = time.time()
    current_day = day_folder_name()

    while True:
        # Sleep until next webcam image is downloaded.
        now = time.time()
        if now < next_run:
            time.sleep(next_run - now)

        # Download the current webcam image.
        start = time.time() 
        log(f"Downloading {code}...")
        try:
            download_image(code, url)
        except Exception as e:
            log(f"Error downloading {code}: {e}")
        
        # Combine webcam images into a video if its a new day.
        updated_day = day_folder_name()
        if updated_day != current_day:
            # New day detected. `current_day` is still yesterday, so use `current_day` for `combine_day`.
            t = Thread(target=combine_day, args=(current_day, code), daemon=True)
            t.start()
            video_creation_threads.append(t)
            
            current_day = updated_day

        # Schedule the next webcam image download.
        now = time.time()
        elapsed = now - start
        if elapsed > INTERVAL:
            # Download took longer than interval, so next run is immediately.
            next_run = now
        else:
            next_run += INTERVAL
        
        log(f"Downloaded {code} in {elapsed:.1f}s. Waiting {next_run - now:.1f}s...")
        

def init_loop():
    """Initialize directories and log startup information for the recorder."""
    
    PICTURES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    
    log("====== Starting Webcam Recorder ======")
    log(f"Interval per camera: {INTERVAL}s")
    log(f"Debug enabled: {debug_enabled()}")
    log("======================================")


def run_loop():
    """Start camera threads and handle daily video creation and debug tasks."""
    
    init_loop()

    # Start independent threads for each camera.
    threads = []
    for code, url in CAMERAS.items():
        t = Thread(target=camera_loop, args=(code, url), daemon=True)
        t.start()
        threads.append(t)

    # Main loop for daily video creation & debug handling.
    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Prepend a newline so the "^C" from keyboard interrupt is on its own line.
        log("Shutting down recorder...", prepend="\n")
