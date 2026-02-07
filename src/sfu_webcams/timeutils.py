from datetime import datetime
import pytz

TZ = pytz.timezone("America/Vancouver")


def now():
    return datetime.now(TZ)


def timestamp_str():
    return now().strftime("%Y-%m-%d %H:%M:%S")


def iso_filename():
    return now().strftime("%Y%m%dT%H%M%S")


def day_folder_name(dt=None):
    dt = dt or now()
    return f"{dt.year}-{dt.month}-{dt.day}-{dt.strftime('%a').lower()[:3]}"


def log(msg: str):
    print(f"[{timestamp_str()}] {msg}", flush=True)
