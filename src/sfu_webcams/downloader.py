import hashlib
from pathlib import Path
import requests

from .timeutils import iso_filename, day_folder_name, log
from .config import PICTURES_DIR


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download_image(code: str, url: str) -> Path | None:
    day = day_folder_name()
    camdir = PICTURES_DIR / day / code
    camdir.mkdir(parents=True, exist_ok=True)

    outfile = camdir / f"{code}_{iso_filename()}.jpg"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        outfile.write_bytes(r.content)
    except Exception:
        if outfile.exists():
            outfile.unlink()
        return None

    # Duplicate detection
    files = sorted(camdir.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)

    if len(files) > 1:
        last_file = files[1]
        if md5sum(last_file) == md5sum(outfile):
            log(f"Removing duplicate image for {outfile}")
            outfile.unlink()
            return None

    return outfile
