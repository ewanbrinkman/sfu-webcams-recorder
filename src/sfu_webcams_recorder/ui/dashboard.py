"""The visual dashboard displaying status information of the program."""

import logging
import time
from rich.live import Live
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.console import Group, Console
from rich.align import Align
from rich.text import Text

from sfu_webcams_recorder.ui.state import (
    program_state,
    DownloadState,
    VideoState,
)
from sfu_webcams_recorder.utils import debug_enabled
from sfu_webcams_recorder.config.settings import SNAPSHOT_DIR, USE_24H_CLOCK


logger = logging.getLogger(__name__)


def fmt_filename_timestamp(dt):
    """Replace characters so the time can be used as a filename."""
    formatted = fmt_timestamp(dt)
    return formatted.replace(":", "-").replace(" ", "_")


def save_dashboard_snapshot():
    """Save an exact snapshot of the current dashboard."""
    console = Console(record=True, width=80)
    console.print(render_table())
    text = console.export_text()

    ts = fmt_filename_timestamp(time.localtime())
    filename = SNAPSHOT_DIR / f"{ts}.snapshot"

    filename.write_text(text)

    logger.info("Snapshot saved: %s", filename.name)


def format_bytes(size_bytes: int) -> str:
    """Format bytes to be in GB."""
    return f"{size_bytes / (1024**3):.2f} GB"


def gb_per_day() -> str:
    """Calculate GB per day downloaded."""
    now = time.time()
    with program_state.lock:
        total_bytes = program_state.total_downloaded_bytes
        elapsed_seconds = max(
            1, now - program_state.start_time
        )  # Avoid divide by zero.
    days = elapsed_seconds / 86400
    return f"{format_bytes(total_bytes / days)}/day"


def fmt_seconds(value: float):
    """Format seconds as 1 decimal place, or '-' if None or 0."""
    return f"{value:.1f}s"


def fmt_timestamp(dt):
    """Return a timestamp string formatted for 24-hour or 12-hour clock."""

    if USE_24H_CLOCK:
        # 24-hour.
        return time.strftime("%Y-%m-%d %H:%M:%S", dt)
    else:
        # 12-hour AM/PM.
        return time.strftime("%Y-%m-%d %I:%M:%S %p", dt)


def fmt_duration(seconds: float) -> str:
    """Format duration for how long the program has been running."""
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if days or hours:
        parts.append(f"{hours}h")
    if days or hours or minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")

    return " ".join(parts)


def render_table():
    """Render the UI table."""
    table = Table(box=box.SIMPLE)

    table.add_column("Webcam")
    table.add_column("Downloader")
    table.add_column("Last Download Elapsed")
    table.add_column("Next Download Start")
    table.add_column("Video Encoding")
    table.add_column("Error")

    now = time.time()

    with program_state.lock:
        for cam_id, state in program_state.webcam_state.items():
            # Downloader column: show elapsed time if downloading, else state name.
            if (
                state.download_state == DownloadState.DOWNLOADING
                and state.download_start_time
            ):
                downloader = fmt_seconds(now - state.download_start_time)
            else:
                downloader = state.download_state.name.title()

            # Last download column.
            last_download = (
                fmt_seconds(state.last_download_elapsed_time)
                if state.last_download_elapsed_time is not None
                else "-"
            )

            # Next download column.
            next_download = "-"
            remaining_interval_time = max(0, state.next_run_time - now)
            next_download = (
                "After Current"
                if remaining_interval_time == 0
                and state.download_state == DownloadState.DOWNLOADING
                else fmt_seconds(remaining_interval_time)
            )

            # Video encoding column.
            queue_list = list(program_state.video_queue.queue)
            total_in_queue = len(queue_list)
            if (
                state.video_state == VideoState.ENCODING
                and state.video_create_start_time
            ):
                # Currently processing.
                encode_time = fmt_seconds(now - state.video_create_start_time)
            elif cam_id in [job[1] for job in queue_list]:
                # Waiting in queue.
                position = [job[1] for job in queue_list].index(cam_id) + 1
                encode_time = f"In Queue ({position}/{total_in_queue})"
            else:
                # Nothing happening
                encode_time = state.video_state.name.title()

            # Error column.
            error = state.error if state.error is not None else "-"

            table.add_row(
                cam_id.name.lower(),
                downloader,
                last_download,
                next_download,
                encode_time,
                error,
            )

    # Calculate values for the header panel.
    uptime = time.time() - program_state.start_time

    with program_state.lock:
        total_images = program_state.total_downloaded_images
        total_gb = format_bytes(program_state.total_downloaded_bytes)
    download_rate = gb_per_day()

    # Calculate table width.
    console = Console()
    table_width = console.measure(table).maximum

    # Create the header panel.
    header_text = Text(
        f"Started: {fmt_timestamp(time.localtime(program_state.start_time))}\n"
        f"Uptime: {fmt_duration(uptime)}\n"
        f"Debug Enabled: {debug_enabled()}\n"
        f"Total Downloaded: {total_gb} ({total_images} Images)\n"
        f"Download Rate: {download_rate}"
    )
    header = Panel(
        header_text,
        title="SFU Webcams Recorder",
        width=table_width,
    )

    return Align.center(Group(header, table))


def ui_loop():
    """Continuously update the live Rich table."""

    with Live(render_table(), refresh_per_second=10, screen=True) as live:
        while True:
            time.sleep(0.1)
            live.update(render_table())
