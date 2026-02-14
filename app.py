
# WOTStat Backend - All endpoints, config, and comments in English
import configparser
import os
import requests
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from bs4 import BeautifulSoup

# --- Read configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'), encoding='utf-8')
cfg = config['DEFAULT']

SERVER_PORT = int(cfg.get('server_port', 8001))
WOTR_URL = cfg.get('wotr_url', 'https://www.worldoftrucks.com/en/')
PROFILE_URL = cfg.get('profile_url', '')
REFRESH_MS = int(cfg.get('refresh_ms', 15000))
SCREEN_SWITCH_SECONDS = int(cfg.get('screen_switch_seconds', 10))
SCREEN_COMMUNITY = cfg.getboolean('screen_community', True)
SCREEN_USER = cfg.getboolean('screen_user', True)

app = FastAPI(title="WOTStat API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

# --- /config endpoint ---
@app.get("/config", summary="Get frontend configuration")
def get_config():
    return {
        "server_port": SERVER_PORT,
        "wotr_url": WOTR_URL,
        "profile_url": PROFILE_URL,
        "refresh_ms": REFRESH_MS,
        "screen_switch_seconds": SCREEN_SWITCH_SECONDS,
        "screen_community": SCREEN_COMMUNITY,
        "screen_user": SCREEN_USER,
        "screen_profile_global": cfg.getboolean('screen_profile_global', True),
        "screen_profile_ets2": cfg.getboolean('screen_profile_ets2', True),
        "screen_profile_ats": cfg.getboolean('screen_profile_ats', True),
    }

# --- /community_progress endpoint (global event) ---
@app.get("/community_progress", summary="Get global community event progress")
def get_community_progress():
    try:
        resp = requests.get(WOTR_URL, timeout=10)
        resp.raise_for_status()
        html = resp.text
        import re
        m_cur = re.search(r'<span class="current-value">\s*([\d,]+)\s*</span>', html)
        m_max = re.search(r'<span class="max-value">\s*([\d,]+)\s*</span>', html)
        if not m_cur or not m_max:
            return {
                "success": False,
                "error": "progress_not_found",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        cur_str = m_cur.group(1).replace(",", "")
        max_str = m_max.group(1).replace(",", "")
        try:
            current = int(cur_str)
            total = int(max_str)
        except ValueError:
            return {
                "success": False,
                "error": "parse_error",
                "raw_current": m_cur.group(1),
                "raw_total": m_max.group(1),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        percent = min(100.0, current / total * 100.0)
        return {
            "success": True,
            "event_name": "Community Event",
            "current": current,
            "total": total,
            "percent": round(percent, 2),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "event_name": None,
            "current": None,
            "total": None,
            "percent": None,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

# --- /user_progress endpoint (user event progress) ---
@app.get("/user_progress", summary="Get user event progress")
def get_user_progress():
    if not PROFILE_URL:
        return {"success": False, "error": "profile_url_not_set", "timestamp": datetime.utcnow().isoformat() + "Z"}
    try:
        resp = requests.get(PROFILE_URL, timeout=10)
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        # Extract username from <title>
        title = soup.title.text if soup.title else ''
        import re
        m = re.search(r'Profile of ([^<|]+)', title)
        username = m.group(1).strip() if m else None
        event_div = soup.find('div', class_='profile-events')
        if not event_div:
            return {"success": False, "error": "no_event_section", "timestamp": datetime.utcnow().isoformat() + "Z"}
        delivery_event = event_div.find('div', class_='delivery-event')
        if not delivery_event:
            return {"success": False, "error": "no_delivery_event", "timestamp": datetime.utcnow().isoformat() + "Z"}
        event_name = delivery_event.find('span', class_='header')
        event_name = event_name.text.strip() if event_name else None
        progress_span = delivery_event.find('span', class_='delivery-event-progress')
        if not progress_span or not event_name:
            return {"success": False, "error": "no_progress_found", "timestamp": datetime.utcnow().isoformat() + "Z", "event_name": event_name}
        progress_text = progress_span.text.strip()
        try:
            current, total = [int(x.strip()) for x in progress_text.split('/')]
            percent = min(100.0, current / total * 100.0) if total else 0.0
        except Exception:
            current = total = percent = None
        return {
            "success": True,
            "event_name": event_name,
            "current": current,
            "total": total,
            "percent": round(percent, 2) if percent is not None else None,
            "username": username,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "event_name": None,
            "current": None,
            "total": None,
            "percent": None,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

# --- /profile_stats endpoint (profile statistics) ---
@app.get("/profile_stats", summary="Get profile statistics")
def get_profile_stats():
    if not PROFILE_URL:
        return {"success": False, "error": "profile_url_not_set", "timestamp": datetime.utcnow().isoformat() + "Z"}
    try:
        resp = requests.get(PROFILE_URL, timeout=10)
        resp.raise_for_status()
        html = resp.text
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        # Extract username from <title>
        title = soup.title.text if soup.title else ''
        import re
        m = re.search(r'Profile of ([^<|]+)', title)
        username = m.group(1).strip() if m else None
        cfg = config['DEFAULT']
        enable_global = cfg.getboolean('screen_profile_global', True)
        enable_ets2 = cfg.getboolean('screen_profile_ets2', True)
        enable_ats = cfg.getboolean('screen_profile_ats', True)
        result = {}
        # Global statistics
        global_stats = soup.find('div', class_='job-stats-global')
        if global_stats and enable_global:
            for stat in global_stats.find_all('div', class_='stat'):
                name = stat.find('div', class_='name')
                value = stat.find('span', class_='value')
                if name and value:
                    stat_name = name.text.strip().lower().replace(' ', '_')
                    result.setdefault('global', {})[stat_name] = value.text.strip()
        # Full statistics (ETS2, ATS, Global)
        detail_div = soup.find('div', class_='job-stats-detail')
        if detail_div:
            rows = detail_div.find_all('div', class_='row')
            for row in rows[1:]:
                name_div = row.find('div', class_='name')
                values = row.find_all('div', class_='value')
                if name_div and len(values) == 3:
                    stat_name = name_div.text.strip().lower().replace(' ', '_')
                    if enable_ets2:
                        result.setdefault('ets2', {})[stat_name] = values[0].text.strip()
                    if enable_ats:
                        result.setdefault('ats', {})[stat_name] = values[1].text.strip()
                    if enable_global:
                        result.setdefault('global', {})[stat_name] = values[2].text.strip()
        return {
            "success": True,
            "profile": result,
            "username": username,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "timestamp": datetime.utcnow().isoformat() + "Z"}

    # ...existing code...

# --- Serve frontend (index.html) ---
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))
