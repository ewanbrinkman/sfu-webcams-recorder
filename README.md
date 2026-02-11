# SFU Webcams

Record the SFU webcams.

## Setup

Run the following:

1. Create a virtual environment: `uv venv`
2. Install project and dependencies: `uv pip install -e .`

## How To Run

After setup, run the following: `uv run sfu-webcams-recorder`

## How To Format

After setup, run the following: `uv run ruff format`

## Output

Stores each day as an `mp4` file. Also, a text file for each `mp4` lists the exact time of every video frame. This is useful if, for example, one wants to programatically extract captures at noon every day.

## Features

- Download webcam images in parallel.
