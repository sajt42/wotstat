
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
SCREEN_PROFILE = cfg.getboolean('screen_profile', True)

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
        "screen_profile": SCREEN_PROFILE,
    }

# --- /community_progress endpoint (global event) ---
@app.get("/community_progress", summary="Get global community event progress")
def get_community_progress():
    try:
        resp = requests.get(WOTR_URL, timeout=10)
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        progress_div = soup.find('div', id='progress')
        event_title = None
        cur_val = max_val = percent = None
        if progress_div:
            event_title_div = progress_div.find('div', class_='global-event-title')
            if event_title_div:
                event_title = event_title_div.text.strip()
            cur_span = progress_div.find('span', class_='current-value')
            max_span = progress_div.find('span', class_='max-value')
            if cur_span and max_span:
                try:
                    cur_val = int(cur_span.text.replace(',', '').strip())
                    max_val = int(max_span.text.replace(',', '').strip())
                    percent = min(100.0, cur_val / max_val * 100.0) if max_val else 0.0
                except Exception:
                    pass
        return {
            "success": True,
            "event_name": event_title,
            "current": cur_val,
            "total": max_val,
            "percent": round(percent, 2) if percent is not None else None,
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
        soup = BeautifulSoup(html, 'html.parser')
        # Example: parse user name, avatar, completed events, etc.
        profile = {}
        name_div = soup.find('div', class_='profile-username')
        profile['username'] = name_div.text.strip() if name_div else None
        avatar_img = soup.find('img', class_='profile-avatar')
        profile['avatar_url'] = avatar_img['src'] if avatar_img else None
        # Example: completed events
        completed_events = []
        events_div = soup.find('div', class_='profile-events')
        if events_div:
            for ev in events_div.find_all('div', class_='completed-event'):
                title = ev.find('span', class_='event-title')
                if title:
                    completed_events.append(title.text.strip())
        profile['completed_events'] = completed_events
        return {"success": True, "profile": profile, "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        return {"success": False, "error": str(e), "timestamp": datetime.utcnow().isoformat() + "Z"}

# --- Serve frontend (index.html) ---
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))
import configparser
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- KONFIG BEOLVASÁS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

server_port = config['DEFAULT'].getint('server_port', 8000)
screen_switch_seconds = config['DEFAULT'].getint('screen_switch_seconds', 10)
communitytracker_enabled = config['DEFAULT'].getboolean('communitytracker_enabled', True)
wot_profile_url = config['DEFAULT'].get('wot_profile_url', '').replace('"', '').replace("'", '')
screen_global = config['DEFAULT'].getboolean('screen_global', True)
screen_ets2 = config['DEFAULT'].getboolean('screen_ets2', False)
screen_ats = config['DEFAULT'].getboolean('screen_ats', False)

# --- FASTAPI APP ---
app = FastAPI(title="World of Trucks Progress API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statikus fájlok (képek, logók)
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

# index.html kiszolgálása a gyökéren
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# --- /config végpont ---
@app.get("/config", summary="Get frontend config")
async def get_frontend_config():
    return {
        "screen_switch_seconds": screen_switch_seconds,
        "screen_global": screen_global,
        "screen_ets2": screen_ets2,
        "screen_ats": screen_ats,
        "communitytracker_enabled": communitytracker_enabled,
        "server_port": server_port
    }

# --- /profile_stats végpont ---
def parse_profile_stats(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Global summary (job-stats-global)
    summary = {}
    global_div = soup.find('div', class_='job-stats-global')
    if global_div:
        stats_map = {
            'Jobs accomplished': 'jobs_accomplished',
            'Total mass transported': 'total_mass_transported',
            'Time on duty': 'time_on_duty',
            'Average delivery distance': 'average_delivery_distance',
            'Total distance': 'total_distance',
        }
        for stat_div in global_div.find_all('div', class_='stat'):
            name = stat_div.find('div', class_='name')
            value = stat_div.find('span', class_='value')
            if name and value:
                key = stats_map.get(name.text.strip())
                if key:
                    summary[key] = value.text.strip()

    # Részletes táblázat (job-stats-detail)
    stats = {'ets2': {}, 'ats': {}, 'global': {}}
    detail_div = soup.find('div', class_='job-stats-detail')
    if detail_div:
        rows = detail_div.find_all('div', class_='row')
        if rows:
            headers = [h.text.strip().lower() for h in rows[0].find_all('div', class_='title')]
            for row in rows[1:]:
                cols = row.find_all('div', class_='value')
                name_div = row.find('div', class_='name')
                if name_div and len(cols) == 3:
                    stat_name = name_div.text.strip().lower().replace(' ', '_')
                    stats['ets2'][stat_name] = cols[0].text.strip()
                    stats['ats'][stat_name] = cols[1].text.strip()
                    stats['global'][stat_name] = cols[2].text.strip()

    result = {}
    if screen_global:
        result['global'] = {**summary, **stats['global']}
    if screen_ets2:
        result['ets2'] = stats['ets2']
    if screen_ats:
        result['ats'] = stats['ats']
    return result


@app.get("/profile_stats", summary="Get Profile Statistics")
async def get_profile_stats():
    url = PROFILE_URL if PROFILE_URL else "https://www.worldoftrucks.com/en/"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        html = resp.text
        # You may want to call a real parse_profile_stats(html) here if implemented
        # For now, just return dummy data for demonstration
        return {"success": True, "profile": {"username": "demo", "avatar_url": None, "completed_events": []}, "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        return {"success": False, "error": str(e), "timestamp": datetime.utcnow().isoformat() + "Z"}

# --- Serve frontend (index.html) ---
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))
