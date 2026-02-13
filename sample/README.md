# World of Trucks Progress Display

## Patch notes

**2026-02-13**
- Logo is now larger and more visible
- Event name is dynamically read from a hidden div and displayed as the main title


This project provides a simple web-based progress display for the "Hearts in Bloom" community event from World of Trucks. It consists of a Python backend (FastAPI) and a frontend HTML page designed to be 100% compatible with NZXT Kraken display devices.

## Features
- Fetches real-time progress data from the official World of Trucks event page.
- Displays current and total progress, as well as percentage completed.
- Clean, modern UI with a progress bar and status updates.
- All text and labels are in English.
- The HTML output is fully compatible with NZXT Kraken displays, making it ideal for use as a live event tracker on your device.

## How It Works
- The Python backend (`app.py`) scrapes the World of Trucks event page and exposes a `/progress` API endpoint.
- The frontend (`index.html`) periodically fetches data from this API and updates the display.
- The HTML and CSS are optimized for the NZXT Kraken's screen resolution and color requirements.

## Usage
1. Start the backend server:
   ```bash
   uvicorn app:app --reload
   ```
2. Open `index.html` in a browser or load it onto your NZXT Kraken display.
3. The display will automatically update every 15 seconds with the latest event progress.

## Requirements
- Python 3.8+
- FastAPI
- requests
- Uvicorn (for running the server)

Install dependencies with:
```bash
pip install fastapi requests uvicorn
```

## Customization
- You can adjust the refresh interval in `index.html` by changing the `REFRESH_MS` value.
- The design can be further customized in the `<style>` section of the HTML file.

## License
This project is provided as-is for personal use and event tracking. Not affiliated with SCS Software or NZXT.