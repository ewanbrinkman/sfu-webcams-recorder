"""General config."""

from pathlib import Path

# -----------------------------
# Video
# -----------------------------

FPS = 60
FFMPEG_CODEC_ARGS = [
    "-c:v",
    "libx264",
    "-preset",
    "slow",
    "-crf",
    "23",
]

# -----------------------------
# Image Download
# -----------------------------

INTERVAL = 10
DOWNLOAD_TIMEOUT_SECONDS = 60

# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path.cwd()

#  Media.
MEDIA_DIR = BASE_DIR / "media"
PICTURES_DIR = MEDIA_DIR / "pictures"
VIDEOS_DIR = MEDIA_DIR / "videos"

# Logging.
LOG_DIR = BASE_DIR / "log"
SNAPSHOT_DIR = LOG_DIR / "snapshots"

# -----------------------------
# Display
# -----------------------------

USE_24H_CLOCK = False

# -----------------------------
# Debug
# -----------------------------

DEBUG_VIDEO_CREATE = False
DEBUG_VIDEO_CREATE_SLEEP = False
DEBUG_VIDEO_CREATE_SLEEP_SECONDS = 10
DEBUG_DOWNLOAD_DELAY = False
DEBUG_SNAPSHOT_LOG = True
DEBUG_SNAPSHOT_LOG_SECONDS = 10
