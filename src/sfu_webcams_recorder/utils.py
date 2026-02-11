import datetime
import pytz

from .config.settings import LOG_USE_24H

TZ = pytz.timezone("America/Vancouver")


def now():
    return datetime.datetime.now(TZ)


def timestamp_str():
    dt = now()
    if LOG_USE_24H:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.strftime("%Y-%m-%d %I:%M:%S %p")


def iso_filename_section():
    return now().strftime("%Y%m%dT%H%M%S")


def day_folder_name(dt=None):
    dt = dt or now()
    return f"{dt.year}-{dt.month}-{dt.day}-{dt.strftime("%a").lower()[:3]}"
