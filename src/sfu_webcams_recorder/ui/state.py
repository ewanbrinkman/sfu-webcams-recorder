"""The program state."""

from dataclasses import dataclass, field
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


@dataclass(slots=True)
class ProgramState:
    """Shared program-wide state."""

    webcam_state: dict[WebcamID, WebcamState] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    total_downloaded_bytes: int = 0
    lock: Lock = field(default_factory=Lock)


# Singleton instance of program-wide state
program_state = ProgramState()
