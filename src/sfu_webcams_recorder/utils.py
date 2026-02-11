"""Various utils."""

import datetime
import pytz

from sfu_webcams_recorder.config.settings import (
    DEBUG_VIDEO_CREATE,
    DEBUG_VIDEO_CREATE_SLEEP,
    DEBUG_DOWNLOAD_DELAY,
)


TZ = pytz.timezone("America/Vancouver")


def now():
    """Get the current time in the "America/Vancouver" timezone."""
    return datetime.datetime.now(TZ)


def day_folder_name(dt=None):
    """Generate the name of a day folder given a time."""
    dt = dt or now()
    return f"{dt.year}-{dt.month}-{dt.day}-{dt.strftime('%a').lower()[:3]}"


def debug_enabled():
    """Check if any debug option is enabled."""
    return DEBUG_VIDEO_CREATE or DEBUG_VIDEO_CREATE_SLEEP or DEBUG_DOWNLOAD_DELAY
