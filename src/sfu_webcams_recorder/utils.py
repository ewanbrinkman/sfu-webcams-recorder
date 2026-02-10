import time
import datetime
import pytz

from .config import LOG_USE_24H, DEBUG_VIDEO_CREATE, DEBUG_DOWNLOAD_DELAY, DEBUG_VIDEO_CREATE_SLEEP_SECONDS


TZ = pytz.timezone("America/Vancouver")


def now():
    """Return the current datetime in the Vancouver timezone."""
    
    return datetime.datetime.now(TZ)


def timestamp_str():
    """Return a timestamp string formatted for logging."""
    
    dt = now()
    if LOG_USE_24H:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # 12-hour AM/PM.
        return dt.strftime("%Y-%m-%d %I:%M:%S %p")


def iso_filename_section():
    """Return the current datetime formatted for filenames."""
    
    return now().strftime("%Y%m%dT%H%M%S")


def day_folder_name(dt=None):
    """Return a folder name for a given day, including year, month, day, and weekday abbreviation."""
    
    dt = dt or now()
    return f"{dt.year}-{dt.month}-{dt.day}-{dt.strftime('%a').lower()[:3]}"


def log(msg: str, prepend=""):
    """Print a message prefixed with a timestamp and optional string."""
    
    print(f"{prepend}[{timestamp_str()}] {msg}", flush=True)

def debug_enabled():
    """Return `True` if any debug flags (video creation or download delay) are enabled."""
    
    return DEBUG_VIDEO_CREATE or DEBUG_DOWNLOAD_DELAY
