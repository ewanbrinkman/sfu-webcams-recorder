import datetime
import pytz


TZ = pytz.timezone("America/Vancouver")


def now():
    return datetime.datetime.now(TZ)


def day_folder_name(dt=None):
    dt = dt or now()
    return f"{dt.year}-{dt.month}-{dt.day}-{dt.strftime("%a").lower()[:3]}"
