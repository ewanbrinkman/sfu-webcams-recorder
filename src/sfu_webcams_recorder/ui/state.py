"""The program state."""

from dataclasses import dataclass, field
from enum import StrEnum, auto
import time
from threading import Lock, Condition
from queue import Queue

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

    # State for each webcam thread.
    webcam_state: dict[WebcamID, WebcamState] = field(default_factory=dict)

    # State for UI panel information.
    start_time: float = field(default_factory=time.time)
    total_downloaded_bytes: int = 0
    total_downloaded_images: int = 0

    # Video worker queue and condition.
    video_queue: Queue = field(default_factory=Queue)
    video_condition: Condition = field(default_factory=Condition)

    # The program lock.
    lock: Lock = field(default_factory=Lock)


# Singleton instance of program-wide state
program_state = ProgramState()
