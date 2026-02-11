import time
from rich.live import Live
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.console import Group, Console
from rich.align import Align
from rich.text import Text

from .state import webcam_state, state_lock, DownloadState, VideoState, program_start_time


def fmt_seconds(value: float):
    """Format seconds as 1 decimal place, or '-' if None or 0."""
    return f"{value:.1f}s"


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
    table = Table(box=box.SIMPLE)

    table.add_column("Webcam")
    table.add_column("Downloader")
    table.add_column("Last Download")
    table.add_column("Next Download Start")
    table.add_column("Video Encoding")
    table.add_column("Error")

    now = time.time()

    with state_lock:
        for cam_id, state in webcam_state.items():
            # Downloader column: show elapsed time if downloading, else state name.
            if state.download_state == DownloadState.DOWNLOADING and state.download_start_time:
                downloader = fmt_seconds(now - state.download_start_time)
            else:
                downloader = state.download_state.name.title()
                
            # Last download column.
            last_download = fmt_seconds(state.last_download_elapsed_time) if state.last_download_elapsed_time is not None else "-"
                
            # Next download column.
            next_download = "-"
            remaining_interval_time = max(0, state.next_run_time - now)
            next_download = "After Current" if remaining_interval_time == 0 and state.download_state == DownloadState.DOWNLOADING else fmt_seconds(remaining_interval_time)

            # Video encoding column.
            if state.video_state == VideoState.ENCODING and state.video_create_start_time:
                encode_time = fmt_seconds(now - state.video_create_start_time)
            else:
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

    # Header panel
    uptime = time.time() - program_start_time
    
    console = Console()
    table_width = console.measure(table).maximum

    header_text = Text(
        f"Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(program_start_time))}\n"
        f"Uptime: {fmt_duration(uptime)}")
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
