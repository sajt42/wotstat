
# WOTStat – World of Trucks Community Progress

WOTStat is a universal web-based stats dashboard for World of Trucks, ETS2, ATS, and community events. The UI is optimized for NZXT Kraken/AIO and other round/circular displays, but works perfectly on any web browser, display, or dashboard (PC, tablet, phone, overlay, etc). The app is fully responsive and device-independent.

## Features
- Real-time global community event progress display
- User event progress and profile statistics screens (with username shown above last update on all stat screens)
- Progress bar, percent, current/total values on all event screens
- Fully responsive, styled after sample/index.html (max-width: 800px)
- All parameters configurable (port, URLs, refresh interval, screen toggles)
- Automatic or manual screen switching
- Optimized for round/circular displays (Kraken, AIO), but works on any browser or dashboard
- ETS2, ATS, WOTR, and community stats supported

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

## Style and Layout
Frontend matches the sample/index.html: max-width 800px, modern colors, typography, unified look. Screens are visually centered and fit well on circular Kraken displays, but also work on any device.


## Troubleshooting
- If data does not refresh, check the config.ini port and server status!
- The /config endpoint returns JSON config for the frontend.
- The /community_progress, /user_progress, /profile_stats endpoints parse World of Trucks pages.

## Known Issues
- **Black screen on config load failure**: If the `/config` endpoint fails (e.g., backend not running), the catch block in `loadConfig()` does not call `buildScreens()` and `showScreen()`, resulting in a black screen. Workaround: Ensure the backend is running before opening the frontend.
