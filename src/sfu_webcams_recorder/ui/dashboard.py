import time
from rich.live import Live
from rich.table import Table
from rich import box

from .state import camera_state, state_lock


def fmt_seconds(value: float):
    if not value:
        return "-"
    return f"{value:.1f}s"


def render_table():
    table = Table(title="Webcam Recorder", box=box.SIMPLE)

    table.add_column("Camera")
    table.add_column("Downloader")
    table.add_column("Last Download")
    table.add_column("Next Download")
    table.add_column("Video Encoding")
    table.add_column("Error")

    now = time.time()

    with state_lock:
        for code, s in camera_state.items():
            
            downloader = fmt_seconds(now - s['download_start_time']) if s['status'] == "Downloading" else s['status']
            encode_time = fmt_seconds(now - s["video_start_time"]) if s['video_start_time'] else "Idle"
                
            next_download = "-"
            remaining_download_wait_time = max(0, s["next_run"] - now)
            next_download = "Previous Download Is Hanging" if remaining_download_wait_time == 0 else fmt_seconds(remaining_download_wait_time)
            
            table.add_row(
                code,
                downloader,
                fmt_seconds(s['last_elapsed']),
                next_download,
                encode_time,
                s['error'] or "-"
            )

    return table


def ui_loop():
    with Live(render_table(), refresh_per_second=10, screen=True) as live:
        while True:
            time.sleep(0.1)
            live.update(render_table())
