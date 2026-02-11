import datetime
import pytz


TZ = pytz.timezone("America/Vancouver")


def now():
    return datetime.datetime.now(TZ)


def day_folder_name(dt=None):
    dt = dt or now()
    return f"{dt.year}-{dt.month}-{dt.day}-{dt.strftime("%a").lower()[:3]}"


def fmt_duration(seconds: float) -> str:
    seconds = int(seconds)

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if days or hours:
        parts.append(f"{hours}h")
    if days or hours or minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")

    return " ".join(parts)
