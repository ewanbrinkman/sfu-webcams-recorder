import hashlib
from pathlib import Path
import requests
import time
import random

from ..utils import iso_filename_section, day_folder_name
from ..config import PICTURES_DIR, DOWNLOAD_TIMEOUT_SECONDS, DEBUG_DOWNLOAD_DELAY


def md5sum(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "md5").hexdigest()


def download_image(code: str, url: str) -> Path | None:
    day = day_folder_name()
    camdir = PICTURES_DIR / day / code
    camdir.mkdir(parents=True, exist_ok=True)

    outfile = camdir / f"{code}_{iso_filename_section()}.jpg"

    try:
        r = requests.get(url, timeout=DOWNLOAD_TIMEOUT_SECONDS)
        if DEBUG_DOWNLOAD_DELAY:
            time.sleep(random.uniform(1, 30))
        r.raise_for_status()
        outfile.write_bytes(r.content)
    except Exception:
        if outfile.exists():
            outfile.unlink()
        return None

    files = sorted(camdir.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)

    if len(files) > 1:
        last_file = files[1]
        if md5sum(last_file) == md5sum(outfile):
            outfile.unlink()
            return None

    return outfile
