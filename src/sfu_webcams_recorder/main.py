from pathlib import Path
from .config import PICTURES_DIR, VIDEOS_DIR
from .loop import run_loop


def main():
    PICTURES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        run_loop()
    except KeyboardInterrupt:
        print("\nShutting down cleanly.")


if __name__ == "__main__":
    main()
