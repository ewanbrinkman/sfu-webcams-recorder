"""Create a daily video of all the webcam images."""

import time
import shutil
import subprocess
import tempfile
from pathlib import Path

from sfu_webcams_recorder.config.settings import (
    PICTURES_DIR,
    VIDEOS_DIR,
    FPS,
    FFMPEG_CODEC_ARGS,
    DEBUG_VIDEO_CREATE_SLEEP,
    DEBUG_VIDEO_CREATE_SLEEP_SECONDS,
)


class VideoCreationError(Exception):
    """Raised when video creation fails."""

    def __init__(self, message: str):
        super().__init__(message)


def create_daily_video(code: str, day: str):
    """Create a daily video using all downloaded webcam images for a day."""

    if DEBUG_VIDEO_CREATE_SLEEP:
        time.sleep(DEBUG_VIDEO_CREATE_SLEEP_SECONDS)

    camdir = PICTURES_DIR / day / code
    imgs = sorted(camdir.glob("*.jpg"))

    if not imgs:
        raise VideoCreationError("No webcam images to process")

    video_dir = VIDEOS_DIR / day / "videos"
    timestamps_dir = VIDEOS_DIR / day / "timestamps"

    video_dir.mkdir(parents=True, exist_ok=True)
    timestamps_dir.mkdir(parents=True, exist_ok=True)

    outfile = video_dir / f"{code}.mp4"
    tmp_out = outfile.with_suffix(".tmp.mp4")
    timestamps_file = timestamps_dir / f"{code}.txt"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        timestamps = []

        for i, src in enumerate(imgs, start=1):
            dst = tmpdir / f"{i:06d}.jpg"
            shutil.copy2(src, dst)

            name = src.stem.split("_", 1)[1]
            timestamps.append(name)

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-framerate",
            str(FPS),
            "-start_number",
            "1",
            "-i",
            str(tmpdir / "%06d.jpg"),
            *FFMPEG_CODEC_ARGS,
            str(tmp_out),
        ]

        subprocess.run(cmd, check=True)

        if tmp_out.exists():
            tmp_out.rename(outfile)
            shutil.rmtree(camdir)
        else:
            raise VideoCreationError("Output video not found")

        timestamps_file.write_text("\n".join(timestamps))
