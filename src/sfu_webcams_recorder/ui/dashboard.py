import time
from rich.live import Live
from rich.table import Table
from rich import box

from .state import camera_state, state_lock, CameraState, DownloadState, VideoState, CameraID


def fmt_seconds(value: float):
    """Format seconds as 1 decimal place, or '-' if None or 0."""
    return f"{value:.1f}s"


def render_table() -> Table:
    table = Table(title="Webcam Recorder", box=box.SIMPLE)

    table.add_column("Camera")
    table.add_column("Downloader")
    table.add_column("Last Download")
    table.add_column("Next Download Start")
    table.add_column("Video Encoding")
    table.add_column("Error")

    now = time.time()

    with state_lock:
        for cam_id, state in camera_state.items():
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

    return table


def ui_loop():
    """Continuously update the live Rich table."""
    
    with Live(render_table(), refresh_per_second=20, screen=True) as live:
        while True:
            time.sleep(0.05)
            live.update(render_table())
