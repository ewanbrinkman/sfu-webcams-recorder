"""Create a daily video of all the webcam images."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from sfu_webcams_recorder.config.settings import PICTURES_DIR, VIDEOS_DIR, FPS, FFMPEG_CODEC_ARGS


def create_daily_video(code: str, day: str):
    """Create a daily video using all downloaded webcam images for a day."""
    
    camdir = PICTURES_DIR / day / code
    imgs = sorted(camdir.glob("*.jpg"))

    if not imgs:
        return

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
            "-loglevel", "error",
            "-y",
            "-framerate", str(FPS),
            "-start_number", "1",
            "-i", str(tmpdir / "%06d.jpg"),
            *FFMPEG_CODEC_ARGS,
            str(tmp_out),
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            return
        
        if tmp_out.exists():
            tmp_out.rename(outfile)
            shutil.rmtree(camdir)
        else:
            return

        timestamps_file.write_text("\n".join(timestamps))
