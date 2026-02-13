
# WOTStat – Development Requirements, Directions, Goals

## 1. General Goal
- A World of Trucks statistics/profile/event display system with frontend and backend, fully automatic, responsive, with multiple screens.

## 2. Functional Requirements
- Global community event progress (progress bar, current/total, percent, status)
- User event progress (on a separate screen, progress bar, current/total, percent)
- Profile statistics (basic data, e.g. completed events, user name, avatar, etc.)
- Screen switching (automatic or manual, unified design on all screens)
- All screens styled after sample/index.html, max-width: 800px, modern, clean
- All data auto-refreshes (interval configurable from config)

## 3. Backend Requirements
- FastAPI-based, CORS enabled
- Configuration: config.ini (port, WOTR URL, refresh_ms, user ID, etc.)
- Endpoints:
  - /config (frontend config)
  - /community_progress (global event)
  - /user_progress (user event progress)
  - /profile_stats (profile stats)
- Static file serving (index.html, images, etc.)
- All endpoints return JSON with error handling

## 4. Frontend Requirements
- Responsive, styled after sample/index.html
- Progress bar, current/total, percent, status on every event/progress screen
- Screen switching (e.g. by button or automatically)
- API_BASE and refresh_ms from config
- Error handling, status display
- Unified color scheme, typography

## 5. Development Directions
- First implement global event progress, then user event, finally profile stats
- Each screen as a separate component/function, but unified design
- Clean, readable, maintainable, extensible code

## 6. Goals
- Fully automatic, user-friendly stat/event/profile display
- Easily configurable, quickly adaptable to new events
- Modern, clean UI matching the sample
- Stable, error-free operation

## 7. Other
- Only read from the sample folder, all development in the main project
- Documentation, README, requirements file always up to date
