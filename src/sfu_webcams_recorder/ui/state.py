from dataclasses import dataclass
from enum import StrEnum, auto
import time
from threading import Lock

from ..config.webcams import CameraID


class DownloadState(StrEnum):
    STARTING = auto()
    DOWNLOADING = auto()
    SLEEPING = auto()


class VideoState(StrEnum):
    IDLE = auto()
    ENCODING = auto()


@dataclass(slots=True)
class CameraState:
    download_state: DownloadState = DownloadState.STARTING
    video_state: VideoState = VideoState.IDLE
    download_start_time: float | None = None
    last_download_elapsed_time: float | None = None
    next_run_time: float | None = None
    video_create_start_time: float | None = None
    error: str | None = None


# Shared state dictionary for all cameras, keyed by `CameraID`.
camera_state: dict[CameraID, CameraState] = {}
# Other state.
program_start_time = time.time()

# Lock to protect access to `camera_state` from multiple threads.
state_lock = Lock()
