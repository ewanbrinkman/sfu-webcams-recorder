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
DEBUG_DOWNLOAD_DELAY = True

# -----------------------------
# Logging
# -----------------------------

LOG_USE_24H = False

# -----------------------------
# Camera
# -----------------------------

CAMERAS = {
    "aqn": "https://ns-webcams.its.sfu.ca/public/images/aqn-current.jpg",
    "aqsw": "https://ns-webcams.its.sfu.ca/public/images/aqsw-current.jpg",
    "aqse": "https://ns-webcams.its.sfu.ca/public/images/aqse-current.jpg",
    "gaglardi": "https://ns-webcams.its.sfu.ca/public/images/gaglardi-current.jpg",
    "towern": "https://ns-webcams.its.sfu.ca/public/images/towern-current.jpg",
    "towers": "https://ns-webcams.its.sfu.ca/public/images/towers-current.jpg",
    "udn": "https://ns-webcams.its.sfu.ca/public/images/udn-current.jpg",
    "wmcroof": "https://ns-webcams.its.sfu.ca/public/images/wmcroof-current.jpg",
    "brh": "https://ns-webcams.its.sfu.ca/public/images/brh-current.jpg",
}
