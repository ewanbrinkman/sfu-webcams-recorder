from pathlib import Path
from .config import PICTURES_DIR, VIDEOS_DIR
from .scheduler.loop import run_loop


def main():
    run_loop()


if __name__ == "__main__":
    main()
