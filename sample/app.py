from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import re
from datetime import datetime

app = FastAPI(title="World of Trucks Progress API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/progress", summary="Get Progress")
def get_progress():
    url = "https://www.worldoftrucks.com/en/"
    resp = requests.get(url, timeout=10)
    html = resp.text

    # 1) current-value
    m_cur = re.search(
        r'<span class="current-value">\s*([\d,]+)\s*</span>',
        html
    )
    # 2) max-value
    m_max = re.search(
        r'<span class="max-value">\s*([\d,]+)\s*</span>',
        html
    )

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
        "current": current,
        "total": total,
        "percent": round(percent, 2),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
