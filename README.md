## NZXT CAM Web Integration & Kraken Display

### How to use with NZXT CAM Web Integration
1. Start the WOTStat server as usual (see above).
2. In NZXT CAM, go to the Web Integration settings.
3. Add a new web widget and set the URL to your WOTStat server (e.g. http://127.0.0.1:8001/).
4. Choose the screen you want to display (the app auto-switches screens, or you can set a default in config.ini).
5. The widget will show the WOTStat stats live on your Kraken display.

### Kraken Display Optimization
- All screens are optimized for round Kraken displays (NZXT, AIO, etc).
- Main stats are large, centered, and readable even on small/circular screens.
- Profile stat screens are split: main stats (jobs, time, mass, total distance) and secondary stats (average distance, longest job, others) for best visibility.
- No unnecessary UI elements, only essential stats and logos.
- Colors and font sizes are tuned for high contrast and readability.

## Screen Layouts
- Community progress, user progress, and profile stats screens auto-switch.
- Profile stats screens are split for optimal fit: main stats and secondary stats.
- All screens are visually centered and fit well on circular Kraken displays.


# WOTStat – World of Trucks Community Progress

## Installation and Usage

1. Copy the repository contents to a folder.
2. Install the required packages:
   pip install fastapi uvicorn requests beautifulsoup4
3. Edit config.ini as needed (port, URLs, refresh interval, etc).
4. Start the server:
   uvicorn app:app --host 127.0.0.1 --port 8001 --reload
5. Open in your browser: http://127.0.0.1:8001/

## Files
- app.py – FastAPI backend, fully configurable, CORS, all endpoints: /config, /community_progress, /user_progress, /profile_stats
- index.html – Responsive frontend, all screens, progress bars, config fetch, English labels
- config.ini – Configuration (port, URLs, refresh_ms, screen toggles)
- wotr_logo.jpg – Logo (optional)

## Features
- Real-time global community event progress display
- User event progress and profile statistics screens
- Progress bar, percent, current/total values on all event screens
- Fully responsive, styled after sample/index.html (max-width: 800px)
- All parameters configurable (port, URLs, refresh interval, screen toggles)
- Automatic or manual screen switching

## Style and Layout
Frontend matches the sample/index.html: max-width 800px, modern colors, typography, unified look.

## Troubleshooting
- If data does not refresh, check the config.ini port and server status!
- The /config endpoint returns JSON config for the frontend.
- The /community_progress, /user_progress, /profile_stats endpoints parse World of Trucks pages.
