"""Shared helpers for the Bermuda Deals collector.

Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
Version: 1.0
Last Updated: 2026-11-15
"""
import json, os, re, time, datetime as dt
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FLYERS = os.path.join(ROOT, "flyers")
LOG = os.path.join(ROOT, "log.txt")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BermudaDeals/1.0 (personal price tracker)"}
TZ = dt.timezone(dt.timedelta(hours=-4))  # Atlantic/Bermuda standard time; DST is handled by Windows for the schedule


def today():
    return dt.datetime.now().date()


def stamp():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    line = "[%s] %s" % (stamp(), msg)
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def day_dir(d=None):
    d = d or today()
    p = os.path.join(DATA, d.isoformat())
    os.makedirs(p, exist_ok=True)
    return p


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def get(url, retries=3, timeout=30, **kw):
    """GET with retries. Returns the Response or raises the last error."""
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout, **kw)
            if r.status_code < 500:
                return r
            last = RuntimeError("HTTP %s for %s" % (r.status_code, url))
        except requests.RequestException as e:
            last = e
        time.sleep(1.5 * (i + 1))
    raise last


def post_json(url, body, retries=3, timeout=30):
    last = None
    for i in range(retries):
        try:
            r = requests.post(url, json=body, headers=dict(UA, **{"Content-Type": "application/json"}), timeout=timeout)
            if r.status_code < 500:
                return r.json()
            last = RuntimeError("HTTP %s for %s" % (r.status_code, url))
        except (requests.RequestException, ValueError) as e:
            last = e
        time.sleep(1.5 * (i + 1))
    raise last


def download(url, dest):
    """Download a binary file if it is not already there. Returns True when newly saved."""
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return False
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    r = get(url, timeout=90, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    return True


def money(x):
    try:
        return "%.2f" % float(x)
    except (TypeError, ValueError):
        return ""


def words(s):
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
