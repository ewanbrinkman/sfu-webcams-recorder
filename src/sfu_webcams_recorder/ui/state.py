"""The program state."""

from dataclasses import dataclass
from enum import StrEnum, auto
import time
from threading import Lock

from sfu_webcams_recorder.config.webcams import WebcamID


class DownloadState(StrEnum):
    """The webcam image download states."""
    STARTING = auto()
    DOWNLOADING = auto()
    SLEEPING = auto()


class VideoState(StrEnum):
    """The webcam video creation states."""
    IDLE = auto()
    ENCODING = auto()


@dataclass(slots=True)
class WebcamState:
    """State for a webcam thread."""
    download_state: DownloadState = DownloadState.STARTING
    video_state: VideoState = VideoState.IDLE
    download_start_time: float | None = None
    last_download_elapsed_time: float | None = None
    next_run_time: float | None = None
    video_create_start_time: float | None = None
    error: str | None = None


# Shared state dictionary for all webcams, keyed by `WebcamID`.
webcam_state: dict[WebcamID, WebcamState] = {}
# Other state.
program_start_time = time.time()

# Lock to protect access to `webcam_state` from multiple threads.
state_lock = Lock()
