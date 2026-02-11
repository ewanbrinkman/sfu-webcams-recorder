from pathlib import Path

# -----------------------------
# Video
# -----------------------------

FPS = 60
FFMPEG_CODEC_ARGS = [
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "23",
]

# -----------------------------
# Image Download
# -----------------------------

INTERVAL = 10
DOWNLOAD_TIMEOUT_SECONDS = 60

# -----------------------------
# Path
# -----------------------------

BASE_DIR = Path.cwd() / "media"
PICTURES_DIR = BASE_DIR / "pictures"
VIDEOS_DIR = BASE_DIR / "videos"

# -----------------------------
# Debug
# -----------------------------

DEBUG_VIDEO_CREATE = False
DEBUG_VIDEO_CREATE_SLEEP_SECONDS = 33
DEBUG_DOWNLOAD_DELAY = False

# -----------------------------
# Logging
# -----------------------------

USE_24H = False
