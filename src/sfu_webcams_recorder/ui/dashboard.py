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

            encode_time = "Idle"
            if s['video_start']:
                encode_time = fmt_seconds(now - s["video_start"])

            table.add_row(
                code,
                s['status'],
                fmt_seconds(s['last_elapsed']),
                fmt_seconds(s['next_run']),
                encode_time,
                s['error'] or "-"
            )

    return table


def ui_loop():
    with Live(render_table(), refresh_per_second=4, screen=True) as live:
        while True:
            time.sleep(0.25)
            live.update(render_table())
