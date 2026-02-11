import hashlib
from pathlib import Path
import requests
import time
import random

from ..utils import day_folder_name, now
from ..config.settings import PICTURES_DIR, DOWNLOAD_TIMEOUT_SECONDS, DEBUG_DOWNLOAD_DELAY


def iso_filename_section():
    return now().strftime("%Y%m%dT%H%M%S")


def md5sum(path: Path) -> str:
    """Compute the md5sum of a file."""
    
    with path.open("rb") as f:
        return hashlib.file_digest(f, "md5").hexdigest()


def download_webcam_image(code: str, url: str) -> Path | None:
    """Download a webcam image."""
    
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
