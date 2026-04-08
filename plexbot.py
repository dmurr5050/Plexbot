#!/usr/bin/env python3
"""
PlexBot — Plex Media File Renamer
===================================
Renames and moves TV show and movie files to Plex-compatible
filenames using TVmaze (TV) and OMDb (Movies).

Requirements:
    pip install requests

Run:
    python plexbot.py
"""

import os
import re
import sys
import json
import time
import shutil
import threading
import subprocess
import requests
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox

# ── Constants ─────────────────────────────────────────────────────────────────
VIDEO_EXTENSIONS    = {'.mkv', '.mp4', '.avi', '.mov', '.m4v', '.wmv', '.ts', '.m2ts', '.mpg', '.mpeg'}
SUBTITLE_EXTENSIONS = {'.srt', '.sub', '.ass', '.ssa', '.vtt', '.idx', '.sup', '.pgs'}
TVMAZE_BASE   = "https://api.tvmaze.com"
OMDB_BASE     = "http://www.omdbapi.com"
OMDB_API_KEY  = ""          # Paste your free OMDb key here, or enter it in the Movies tab
TVDB_BASE     = "https://api4.thetvdb.com/v4"
_TVDB_API_KEY = "068ef573-b79b-4162-b121-b5af659cdafd"
TMDB_BASE     = "https://api.themoviedb.org/3"
_TMDB_TOKEN   = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1MTQ0ZjRhZGEwYjY3ODRiYWZmMjM2MjUxNjU5NDZjZSIsIm5iZiI6MTc3NDQwMzM2Mi42OTEsInN1YiI6IjY5YzMzZjIyNDIxNDlkMTc2MjM1MzAxMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lSsMvJgiSPaTBolm9lQCHw8B5kG48bVPW6Nd68W2xZ8"
APP_TITLE     = "PlexBot"
VERSION       = "1.08"

# ── GitHub auto-update settings ───────────────────────────────────────────────
GITHUB_USER    = "dmurr5050"
GITHUB_REPO    = "Plexbot"
GITHUB_BRANCH  = "main"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/plexbot.py"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES_PAGE = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"

# ── Data-source options shown in the UI dropdowns ──────────────────────────
TV_SOURCES    = ["TVmaze", "TheTVDB"]
MOVIE_SOURCES = ["OMDb", "TheTVDB", "TMDb"]

# ── Brand icons for lookup sources (16x16 PNG, base64-encoded) ───────────────
SOURCE_ICONS_B64 = {
    "TVmaze":  "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAZUlEQVR42s2VUQ8AEAiE7z/7/8srobpic5un8nUjAZSkQZgFSyzMhGZhW2gVNkGXACsNXWCsM7UHIZhXaIjHgcGCHPCUUwLu8v5xSJ2hBSU64HFjZy6EAgZd+e/5h4nzfsDe+gI6g1LU7C2I5mkAAAAASUVORK5CYII=",
    "TheTVDB": "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAcUlEQVR42mNgQAMZ2wz/k4IZ8AFSDcNrKEySVIDVUGTbyDUQbii689EVIVtClPfxGYhsELo41Q3EZShZBuJz6eBwIc3CkGQvUy3ZkJuwsRpIiqFEuZBYQ4n2MjGGEix5SDGU6GKMGEPJLhMHtNRG1w8A87Hv6rm7Oj0AAAAASUVORK5CYII=",
    "OMDb":    "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAZElEQVR42mNgQANSUlL/ScEM+ACphuE1lFzDsBpKqWEohhKj8OtRCTAmylC6GwgzjFhDGYg1iFiDGUg1iJDBDOS4Dp8rae9lYgwlO5apaiDVvYxLI0VhSNP8TPcSh/YFLLWqAADLRT5/x64M+AAAAABJRU5ErkJggg==",
    "TMDb":    "iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAgElEQVR42mNgQAO8qvb/ScEM+ACphuE1FCSBDmBiyJrR+VgNxacB3XBcBsINRRfE5SJcLsYwlFgDCXl5CBvIuOUJSRivgaQahs1QBkoNQzeUdi6kSRjiwoRilmCyIZSfyTIQPbsRysc48zMuA4nxPtYSh1wDSS4T8XmZqqU2un4AXpXbO2nQIxoAAAAASUVORK5CYII=",
}
_source_icon_cache: dict = {}   # name -> PhotoImage (kept alive here)

def get_source_icon(name: str):
    """Return a Tkinter PhotoImage for the given source name, or None."""
    if name in _source_icon_cache:
        return _source_icon_cache[name]
    b64 = SOURCE_ICONS_B64.get(name)
    if not b64:
        return None
    try:
        from tkinter import PhotoImage as _PI
        img = _PI(data=b64)
        _source_icon_cache[name] = img
        return img
    except Exception:
        return None

# ── Embedded header icon (40x40 PNG, base64) ─────────────────────────────────
HEADER_ICON_B64 = """iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAHI0lEQVR4nM2Ya4hV1xXH/2vtfV9z753XnTE2GhQ1TJoGDdzYxCaNDW2JoW3AUApFbWkInUqblpAPrbZhEJpPbT8JocWWtFKk+VAoQUwwylCisQzVPpgo7WhmRqNxnDtzn+c+ztl7r364j5k4UWe8o/QPh3PPPufu/Ttrr7X2PovQkAyBcW9a4cppS/vgGs0EgBtnwvJKGodrnJcstaw4tx7rEw1AMgSmfXBXX1/z2D0r9baLl9zxNd8dP0mAE0AnEn2fI0KaCJ0AICJtW5KIxDmpMPO/IhGcnJ6eLjVv4Tpr6tP3phVw2gnoa+gK7U1mKjEA7/anUt+r+PQiET14Xeft8gEAmOv9VKsykUj0HSiVMr8AEKDuUk0Xg27+EFAZeWMKFbFA72vGqd2AQETc/D8ssxigtcz0ajLZvw2obi8WizOYZ8kWYGBcCGB98K/mh2COi3MWc0HCdwgQgIiIBET8eeciR4DercBkgEbwLBg4sIgB4lB33DsI1hIBCIs4n5k/m0x6+wDY5tgLAJjmbt5lhUScE5Hvx+Mr7kEDcgGILH++W6wIgGPmuNbuq422hYD/BxLnZEvzQt/syVuJ+ebmboaiXVoOIKCec4E2AYsVQSvWr1djIWMFJGJUn7/FL2i2LUAiwFjgla9HsWEloxrIAkbfCC7PCkbGLN49ZyEAoqFFQ7a6u20LOgGeflhjy4CCV5G6N8v8+yKKiQILnDhn8KPXq7iYkaVAAmgznRTKglxJkPUE2ZIgXxEUquIKFREnRLmyIF8WfHmjxsEfRINYyJWtW1qaaMsHFQNMAq0A58T9+A+zb05ekyAcEvXo/dGVu5+Jp6MhDl/JOaTXa7XrSTq3/4gb6E5yZLGB0xZgUwSACebEOVP7YCr6lWiU9Tv/dDVWAfY8F6WKL84K8dbPKLP/cO0Skd7QmOhbGnNZ82BvgiPxuOrojnOUlOoan0akRSBAPEwMmJm5lltrWSzY1EdZU/VKzno14kSM5LlHNfmNhMFMuJIzRQD6rvkgUN8figgA0q8NprZcmiGlFOHhtUwPrGIUKuIiIULVF/z5pHeeVeRJJwIsMlaWxYICgAn8pU3RNUQCCFAzAt8QujuIw5rw23eyw0fO1IKursRaWye8e4BNedW50HQCF1hXvXjNXD04XBjZf6Q0nUz2fFOEFCCLzoRtA4oIiADrxP3sT9nDH067GkF0yRd7KWNrE1MCILS6M9m7HcQRkcVbb1kAgbk0c/zfQWX8amybDkMLQCFFoa4uDjERjHXAEuGWDbCprhiFox3cGQsTOanzOCfi0AJb8l6zLUDr6lNrHQARZwXinFjnoOett2199LcF2B0n9HQqjvsE30hUMfi2SgQ30e0CimLQ747X/NFJM2ItDCDBVNYUQopoOSFvC1AExAQcOBbwgbeDfjQ2mLFYxwMhDbX4JHKHAJvqjpNmig40r42TRqC2rdvbsHLjG8s5B2aGdQ52bvvZilQiai2B84GbZZNbvQQRVVtjLhZORFAsFlEqFQEIPK9e71FKUV3MzEzMjFqtikKhgCAIQERQSkEpBWstgiBoveiNx8KZJuuiAEUE4XAETzzxBWze/BiIGI8/vtWKiM3lsqjVaqhWyyiXPRSLRaxffz+eeuqL6OvrhzEB8vkccrksEokE+vtXuErF+yRIAcAiEjCrNxtt9kZT7NAsPTDD80ry0EMbae/efflisaBHRk6pdevW1y5f/lCl0+no6Oio7uzsEmaG79cqu3Y9rzdufLB89ux5fumlweiOHd/hsbH/YGDg03rnzp2FF174ls5kZhJa6/nTbYgo5Jz7Yz4/NY566WUhoAi4YdlmCYSAut/FYh16cvKDwsTEBfT19XXt2TNkN2xYN/P++2dDhw4dTB469Bfs2LE9W6v5n8rlZsRa4wYHX5RVq+6b2bQp3a0UV8bGxoJMZlppHW7CSRNORCaB8MuNcQWY54MhzQFA5tlH9K/h3FvE3Kh6igFgAAQXLvx3Zvfub+tjx97u1zpUPHXqhD8xMWFHRt7LrF59X254+OhUf/+KRLlc9sLhWNmYoHD27KhHxBHfr04dPXq4HInEqbc3JcYYQ0QGABFxSETGRWRbqfRRZt4sgv7+m3TokcHTwdTv1/58xYboT8tXqq/GvzHxSqo39Us/oOeJqBsAiLi+a7EOSjGYGaVSET09vTDGQmuNbHYWPT29CAIfyWQSmUwGvl9DKtWParWCctlDKlX3y0qlCmaGiKuI4A0R/onnXZvC9QXMdM86B5yGs/Q3FM0bs3k5A0Cy2ZmXI9HUr5TCM0TY7JzpAoSJlBhj4JxwLNbhCoU811MKEIvFpFDIg4jJ80oUDkeloyPu8vkcMyuKxTpsLjdLRApaswfIP4jorWJx+nyD52NwNxPh7hbRW75+Q8kQWIa3ahn6WG5k1JP5nTxumur+B/kLcXiVegI/AAAAAElFTkSuQmCC"""

# ── Config (saved to Documents/PlexBot/) ─────────────────────────────────────
def _config_path() -> Path:
    """Return path to config file in the user's Documents/PlexBot folder."""
    docs = Path.home() / "Documents"
    # On Windows, also try USERPROFILE\Documents
    if not docs.exists():
        docs = Path(os.environ.get("USERPROFILE", Path.home())) / "Documents"
    config_dir = docs / "PlexBot"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "plexbot_config.json"

CONFIG_FILE = _config_path()

def load_config() -> dict:
    """Load config from Documents/PlexBot/plexbot_config.json."""
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def save_config(data: dict):
    """Save config to Documents/PlexBot/plexbot_config.json."""
    try:
        existing = load_config()
        existing.update(data)
        CONFIG_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    except Exception:
        pass

# ── Color Palette ─────────────────────────────────────────────────────────────
BG_DARK     = "#0d0d14"
BG_PANEL    = "#13131e"
BG_SURFACE  = "#1a1a28"
BG_ROW      = "#1e1e2e"
BG_ROW_ALT  = "#181826"
BG_HOVER    = "#252538"
BORDER      = "#2a2a42"
ACCENT      = "#e8a020"
ACCENT2     = "#f0c060"
ACCENT_BLUE = "#4488dd"
SUCCESS     = "#3dcc78"
ERROR       = "#e05555"
WARNING     = "#e8a020"
MUTED       = "#6060a0"
TEXT        = "#ddddf0"
TEXT_DIM    = "#9090b8"
WHITE       = "#ffffff"
BLUE        = "#5090e0"

# ── Font Definitions ──────────────────────────────────────────────────────────
FONT_BOLD    = ("Segoe UI", 10, "bold")
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 9)
FONT_MONO_SM = ("Consolas", 8)

# ── TVmaze API ────────────────────────────────────────────────────────────────
_tv_show_cache: dict = {}

def tvmaze_search_shows(query: str) -> list:
    """Return up to 10 show matches [{id, name, premiered, network, summary}]."""
    r = requests.get(f"{TVMAZE_BASE}/search/shows", params={"q": query}, timeout=10)
    r.raise_for_status()
    results = []
    for item in r.json():
        show = item.get("show", {})
        net  = (show.get("network") or show.get("webChannel") or {}).get("name", "")
        results.append({
            "id":        show["id"],
            "name":      show.get("name", ""),
            "premiered": (show.get("premiered") or "")[:4],
            "network":   net,
            "summary":   re.sub(r"<[^>]+>", "", show.get("summary") or "").strip()[:120],
        })
    return results

def tvmaze_get_show_id(show_name: str) -> int:
    key = show_name.lower().strip()
    if key in _tv_show_cache:
        return _tv_show_cache[key]
    results = tvmaze_search_shows(show_name)
    if not results:
        raise ValueError(f"Show not found: '{show_name}'")
    _tv_show_cache[key] = results[0]["id"]
    return _tv_show_cache[key]

def tvmaze_get_episode_by_id(show_id: int, season: int, episode: int) -> dict:
    r = requests.get(f"{TVMAZE_BASE}/shows/{show_id}/episodebynumber",
                     params={"season": season, "number": episode}, timeout=10)
    if r.status_code == 404:
        raise ValueError(f"S{season:02d}E{episode:02d} not found")
    r.raise_for_status()
    return r.json()

def tvmaze_get_episode(show_name: str, season: int, episode: int) -> dict:
    show_id = tvmaze_get_show_id(show_name)
    return tvmaze_get_episode_by_id(show_id, season, episode)

# ── OMDb API ──────────────────────────────────────────────────────────────────
def omdb_search_movies(title: str, year, api_key: str) -> list:
    """Search OMDb, return up to 10 matches [{imdbID, title, year, overview}]."""
    if not api_key:
        raise ValueError("No OMDb API key. Enter it in the Movies tab.")
    params = {"apikey": api_key, "s": title, "type": "movie"}
    if year:
        params["y"] = year
    r = requests.get(OMDB_BASE, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("Response") == "False":
        return []
    results = []
    for item in (data.get("Search") or [])[:10]:
        results.append({
            "id":       item.get("imdbID", ""),
            "title":    item.get("Title", ""),
            "year":     item.get("Year", "????")[:4],
            "overview": f"IMDb: {item.get('imdbID','')}",
        })
    return results

def omdb_get_movie(imdb_id: str, api_key: str) -> dict:
    """Fetch full movie details by IMDb ID."""
    params = {"apikey": api_key, "i": imdb_id, "plot": "short"}
    r = requests.get(OMDB_BASE, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("Response") == "False":
        raise ValueError(data.get("Error", "Movie not found"))
    return {
        "id":       data.get("imdbID", ""),
        "title":    data.get("Title", ""),
        "year":     data.get("Year", "????")[:4],
        "overview": data.get("Plot", "")[:120],
    }

# ── TMDb API ──────────────────────────────────────────────────────────────────
def _tmdb_headers() -> dict:
    return {"Authorization": f"Bearer {_TMDB_TOKEN}",
            "Accept": "application/json"}

def tmdb_search_movies(title: str, year=None) -> list:
    """Search TMDb, return up to 10 matches [{id, title, year, overview}]."""
    params = {"query": title, "include_adult": "false", "language": "en-US", "page": 1}
    if year:
        params["primary_release_year"] = year
    r = requests.get(f"{TMDB_BASE}/search/movie",
                     params=params, headers=_tmdb_headers(), timeout=10)
    r.raise_for_status()
    results = []
    for item in (r.json().get("results") or [])[:10]:
        yr = (item.get("release_date") or "????")[:4]
        results.append({
            "id":       item.get("id"),
            "title":    item.get("title", ""),
            "year":     yr,
            "overview": (item.get("overview") or "")[:120],
        })
    return results

def tmdb_get_movie(movie_id) -> dict:
    """Fetch full movie details from TMDb by ID."""
    r = requests.get(f"{TMDB_BASE}/movie/{movie_id}",
                     params={"language": "en-US"},
                     headers=_tmdb_headers(), timeout=10)
    if r.status_code == 404:
        raise ValueError("Movie not found on TMDb")
    r.raise_for_status()
    data = r.json()
    yr = (data.get("release_date") or "????")[:4]
    return {
        "id":       data.get("id"),
        "title":    data.get("title", ""),
        "year":     yr,
        "overview": (data.get("overview") or "")[:120],
    }

# ── TheTVDB API ──────────────────────────────────────────────────────────────
_tvdb_token: dict = {"token": None, "expires": 0}

def _tvdb_auth_token() -> str:
    """Return a valid TheTVDB JWT token, refreshing if needed."""
    import time as _time
    if _tvdb_token["token"] and _time.time() < _tvdb_token["expires"]:
        return _tvdb_token["token"]
    r = requests.post(f"{TVDB_BASE}/login",
                      json={"apikey": _TVDB_API_KEY}, timeout=10)
    r.raise_for_status()
    data = r.json()
    token = data.get("data", {}).get("token") or data.get("token", "")
    if not token:
        raise ValueError("TheTVDB login failed — no token returned")
    _tvdb_token["token"]   = token
    _tvdb_token["expires"] = _time.time() + 3600 * 23  # ~24-hour TTL
    return token

def _tvdb_headers() -> dict:
    return {"Authorization": f"Bearer {_tvdb_auth_token()}",
            "Accept": "application/json"}

def tvdb_search_shows(query: str) -> list:
    """Search TheTVDB for TV series, return [{id, name, premiered, network, summary}]."""
    r = requests.get(f"{TVDB_BASE}/search",
                     params={"query": query, "type": "series", "limit": 10},
                     headers=_tvdb_headers(), timeout=10)
    r.raise_for_status()
    results = []
    for item in (r.json().get("data") or [])[:10]:
        year = (item.get("first_air_time") or item.get("year") or "")[:4]
        net  = item.get("network") or item.get("primaryLanguage") or ""
        desc = re.sub(r"<[^>]+>", "", item.get("overview") or "").strip()[:120]
        results.append({
            "id":        item.get("tvdb_id") or item.get("id"),
            "name":      item.get("name") or item.get("seriesName", ""),
            "premiered": year,
            "network":   net,
            "summary":   desc,
        })
    return results

def tvdb_get_episode(show_id, season: int, episode: int) -> dict:
    """Fetch a single episode from TheTVDB by show ID, season, and episode number."""
    time.sleep(0.2)
    r = requests.get(f"{TVDB_BASE}/series/{show_id}/episodes/default",
                     params={"season": season, "episodeNumber": episode, "page": 0},
                     headers=_tvdb_headers(), timeout=10)
    if r.status_code == 404:
        raise ValueError(f"S{season:02d}E{episode:02d} not found on TheTVDB")
    r.raise_for_status()
    episodes = (r.json().get("data") or {}).get("episodes") or []
    for ep in episodes:
        if ep.get("seasonNumber") == season and ep.get("number") == episode:
            return {"name": ep.get("name") or ep.get("episodeName") or f"Episode {episode}"}
    raise ValueError(f"S{season:02d}E{episode:02d} not found on TheTVDB")

def tvdb_search_movies(query: str, year=None) -> list:
    """Search TheTVDB for movies, return [{id, title, year, overview}]."""
    params = {"query": query, "type": "movie", "limit": 10}
    if year:
        params["year"] = year
    r = requests.get(f"{TVDB_BASE}/search",
                     params=params, headers=_tvdb_headers(), timeout=10)
    r.raise_for_status()
    results = []
    for item in (r.json().get("data") or [])[:10]:
        y    = (item.get("first_air_time") or item.get("year") or "????")[:4]
        desc = re.sub(r"<[^>]+>", "", item.get("overview") or "").strip()[:120]
        results.append({
            "id":       item.get("tvdb_id") or item.get("id"),
            "title":    item.get("name") or item.get("title", ""),
            "year":     y,
            "overview": desc,
        })
    return results

def tvdb_get_movie(movie_id) -> dict:
    """Fetch full movie details from TheTVDB by ID."""
    r = requests.get(f"{TVDB_BASE}/movies/{movie_id}/extended",
                     headers=_tvdb_headers(), timeout=10)
    if r.status_code == 404:
        raise ValueError("Movie not found on TheTVDB")
    r.raise_for_status()
    data = r.json().get("data") or {}
    year = ""
    for rel in (data.get("releases") or []):
        if rel.get("date"):
            year = rel["date"][:4]
            break
    if not year:
        year = (data.get("year") or "????")
    title = data.get("name") or data.get("title") or ""
    desc  = re.sub(r"<[^>]+>", "", data.get("overview") or "").strip()[:120]
    return {"id": movie_id, "title": title, "year": str(year)[:4], "overview": desc}

# ── Filename Parsing ──────────────────────────────────────────────────────────
def parse_tv_filename(filename: str):
    stem = Path(filename).stem
    ext  = Path(filename).suffix.lower() or ".mkv"
    m = re.search(r'^(.+?)[.\s_\-]+[Ss](\d{1,2})[Ee](\d{1,2})', stem)
    if not m:
        return None
    raw  = m.group(1)
    show = re.sub(r'[._]+', ' ', raw).strip()
    show = re.sub(r'\s+', ' ', show).title()
    show = re.sub(r"\b'S\b", "'s", show)
    return {"show_name": show, "season": int(m.group(2)),
            "episode": int(m.group(3)), "ext": ext}

def parse_movie_filename(filename: str):
    stem = Path(filename).stem
    ext  = Path(filename).suffix.lower() or ".mkv"
    year_match = re.search(r'[\s._\-\(]((19|20)\d{2})[\s._\-\)]', stem)
    year = int(year_match.group(1)) if year_match else None
    if year_match:
        raw = stem[:year_match.start()]
    else:
        raw = re.sub(
            r'[\s._\-]+(1080p|720p|2160p|4k|bluray|bdrip|webrip|web-dl|'
            r'hdtv|dvdrip|hevc|x265|x264|h264|aac|ac3|dts|remux|proper).*$',
            '', stem, flags=re.IGNORECASE)
    title = re.sub(r'[._]+', ' ', raw).strip()
    title = re.sub(r'[\(\)]+', '', title).strip()
    title = re.sub(r'\s+', ' ', title).strip()
    if not title:
        return None
    return {"raw_title": title, "year": year, "ext": ext}

def safe_name(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '', s).strip()

def strip_year_from_query(name: str) -> str:
    """Remove a trailing or parenthesised year from a show/movie name."""
    # Remove (YYYY) or [YYYY] anywhere
    name = re.sub(r'[\(\[]\s*(19|20)\d{2}\s*[\)\]]', '', name)
    # Remove bare year at end:  "Show Name 2005" → "Show Name"
    name = re.sub(r'\s+(19|20)\d{2}\s*$', '', name)
    return name.strip()

# ── Media Info via ffprobe ────────────────────────────────────────────────────
_VIDEO_CODEC_MAP = {
    "hevc": "HEVC", "h265": "HEVC", "h264": "H.264", "avc": "H.264",
    "avc1": "H.264", "mpeg4": "MPEG-4", "mpeg2video": "MPEG-2",
    "vp9": "VP9", "vp8": "VP8", "av1": "AV1", "xvid": "XviD",
    "divx": "DivX", "theora": "Theora", "wmv3": "WMV3",
}
_AUDIO_CODEC_MAP = {
    "ac3": "AC3", "eac3": "EAC3", "dts": "DTS", "truehd": "TrueHD",
    "aac": "AAC", "mp3": "MP3", "mp2": "MP2", "flac": "FLAC",
    "vorbis": "Vorbis", "opus": "Opus", "pcm_s16le": "PCM", "pcm_s24le": "PCM",
}
_RES_MAP = {
    (3840, 2160): "2160p", (2560, 1440): "1440p",
    (1920, 1080): "1080p", (1280,  720): "720p",
    (854,   480): "480p",  (640,   480): "480p",
}

def get_media_info(filepath: Path) -> dict:
    try:
        # CREATE_NO_WINDOW suppresses the console flash on Windows
        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", str(filepath)],
            capture_output=True, timeout=15, **kwargs)
        if result.returncode != 0:
            return {}
        streams = json.loads(result.stdout).get("streams", [])
        video_codec = audio_codec = resolution = ""
        for s in streams:
            kind = s.get("codec_type", "")
            if kind == "video" and not video_codec:
                raw = s.get("codec_name", "").lower()
                video_codec = _VIDEO_CODEC_MAP.get(raw, raw.upper())
                w, h = s.get("width", 0), s.get("height", 0)
                resolution = _RES_MAP.get((w, h), "")
                if not resolution and h:
                    for (rw, rh), label in _RES_MAP.items():
                        if h >= rh:
                            resolution = label
                            break
            if kind == "audio" and not audio_codec:
                ch = s.get("channels", 0)
                # Map channel count to standard label
                _CH_MAP = {1:"1.0", 2:"2.0", 6:"5.1", 7:"6.1", 8:"7.1"}
                audio_codec = _CH_MAP.get(ch, f"{ch}ch") if ch else ""
        return {"resolution": resolution, "video_codec": video_codec, "audio_codec": audio_codec}
    except Exception:
        return {}

def build_media_tags(media: dict, use_res: bool, use_vcodec: bool, use_acodec: bool) -> str:
    parts = []
    if use_res    and media.get("resolution"):  parts.append(media["resolution"])
    if use_vcodec and media.get("video_codec"): parts.append(media["video_codec"])
    if use_acodec and media.get("audio_codec"): parts.append(media["audio_codec"])
    return (" - " + " - ".join(parts)) if parts else ""

# ── Plex Name Builders ────────────────────────────────────────────────────────
def build_tv_name(parsed: dict, ep_title: str, media: dict,
                  use_res: bool, use_vc: bool, use_ac: bool,
                  show_year: str = "") -> str:
    show  = safe_name(parsed["show_name"])
    if show_year:
        show = f"{show} ({show_year})"
    s, e  = f"S{parsed['season']:02d}", f"E{parsed['episode']:02d}"
    title = safe_name(ep_title)
    tags  = build_media_tags(media, use_res, use_vc, use_ac)
    return f"{show} - {s}{e} - {title}{tags}{parsed['ext']}"

def build_movie_name(movie_title: str, year: str, ext: str, media: dict,
                     use_res: bool, use_vc: bool, use_ac: bool) -> str:
    title = safe_name(movie_title)
    tags  = build_media_tags(media, use_res, use_vc, use_ac)
    return f"{title} ({year}){tags}{ext}"


# ── Recursive video file collector ──────────────────────────────────────────
def collect_video_files(paths) -> list:
    """
    Given a list of Path objects (files or folders), return all video files.
    Folders are scanned recursively.
    """
    found = []
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS:
            found.append(p)
        elif p.is_dir():
            for child in sorted(p.rglob("*")):
                if child.is_file() and child.suffix.lower() in VIDEO_EXTENSIONS:
                    found.append(child)
    return found


def find_subtitle_siblings(video_path: Path) -> list:
    """
    Find subtitle files in the same folder whose stem starts with
    the video stem (e.g. Show.S01E01.en.srt alongside Show.S01E01.mkv).
    Returns list of Path objects.
    """
    subs = []
    stem = video_path.stem.lower()
    try:
        for f in video_path.parent.iterdir():
            if f.suffix.lower() in SUBTITLE_EXTENSIONS:
                # Match if subtitle stem starts with video stem
                # This covers: Show.S01E01.srt, Show.S01E01.en.srt, Show.S01E01.en.sdh.srt
                if f.stem.lower().startswith(stem):
                    subs.append(f)
    except Exception:
        pass
    return subs


def build_subtitle_name(new_video_name: str, sub_path: Path) -> str:
    """
    Derive the new subtitle filename from the new video name.
    Preserves any language/flag suffix after the video stem.
    e.g. Show - S01E01 - Title.mkv  +  Show.S01E01.en.sdh.srt
      -> Show - S01E01 - Title.en.sdh.srt
    """
    video_stem   = Path(new_video_name).stem          # "Show - S01E01 - Title"
    sub_ext      = sub_path.suffix.lower()            # ".srt"

    # Try to extract language suffix from sub stem beyond the video stem
    # e.g. original sub stem = "Show.S01E01.en.sdh", video stem was "Show.S01E01"
    # We want to preserve ".en.sdh"
    # Strategy: strip shared prefix chars, keep remainder as language tag
    orig_video_stem = sub_path.stem  # original sub stem without final ext
    # Remove any dotted suffix shared with any known subtitle lang codes
    # Just preserve everything after the first dot past a base that looks like video
    # Simple approach: if sub stem has more parts than video stem, keep extras
    sub_parts   = sub_path.stem.split(".")
    extra_parts = []
    for part in reversed(sub_parts):
        if part.lower() in SUBTITLE_EXTENSIONS or len(part) <= 5:
            extra_parts.insert(0, part)
        else:
            break
    # Filter to only the "extra" language-style parts (short, like "en", "sdh", "forced")
    lang_parts = [p for p in extra_parts
                  if len(p) <= 8 and p.lower() not in
                  {Path(new_video_name).stem.lower()}]

    if lang_parts:
        return f"{video_stem}.{'.'.join(lang_parts)}{sub_ext}"
    return f"{video_stem}{sub_ext}"


def try_remove_empty_folder(folder: Path):
    """Remove folder if it is now empty (no files or subdirs remain)."""
    try:
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
    except Exception:
        pass


# ── Add Files Dialog (files + folders + subfolders) ──────────────────────────
class AddFilesDialog(Toplevel):
    """
    Custom file picker that lets you select both files AND folders.
    Selected folders are scanned recursively for video files.
    """
    def __init__(self, parent, color):
        super().__init__(parent)
        self.title("Add Files & Folders")
        self.geometry("720x540")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.grab_set()
        self.focus_set()
        self.color   = color
        self.result  = []   # List of Path objects chosen
        self._items  = []   # [{path, kind, var}]
        self._build()
        self.wait_window(self)

    def _build(self):
        # Header
        hdr = Frame(self, bg=BG_PANEL, height=50)
        hdr.pack(fill=X); hdr.pack_propagate(False)
        Frame(hdr, bg=self.color, width=4).pack(side=LEFT, fill=Y)
        Label(hdr, text="Add Files & Folders", font=("Segoe UI",12,"bold"),
              fg=self.color, bg=BG_PANEL).pack(side=LEFT, padx=14)
        Label(hdr, text="Folders are scanned recursively for video files",
              font=FONT_SMALL, fg=MUTED, bg=BG_PANEL).pack(side=LEFT, padx=4)
        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Toolbar
        tb = Frame(self, bg=BG_PANEL, height=38)
        tb.pack(fill=X); tb.pack_propagate(False)
        self._tbtn(tb, "＋ Add Files",   self._browse_files,  self.color)
        self._tbtn(tb, "📁 Add Folder",  self._browse_folder, MUTED)
        self._tbtn(tb, "✕ Remove Selected", self._remove_selected, ERROR)
        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # List area
        lf = Frame(self, bg=BG_DARK)
        lf.pack(fill=BOTH, expand=True, padx=0, pady=0)

        self._canvas = Canvas(lf, bg=BG_DARK, highlightthickness=0, bd=0)
        sb = Scrollbar(lf, orient=VERTICAL, command=self._canvas.yview,
                       bg=BG_SURFACE, troughcolor=BG_DARK)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=RIGHT, fill=Y)
        self._canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self._inner = Frame(self._canvas, bg=BG_DARK)
        self._cwin  = self._canvas.create_window((0,0), window=self._inner, anchor=NW)
        self._inner.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cwin, width=e.width))
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        # Empty label
        self._empty_lbl = Label(self._inner, text="Use the buttons above to add files or folders",
                                 font=FONT_SMALL, fg=MUTED, bg=BG_DARK)
        self._empty_lbl.pack(pady=40)

        # Status / count
        self._count_var = StringVar(value="0 items")
        Frame(self, bg=BORDER, height=1).pack(fill=X)
        bot = Frame(self, bg=BG_PANEL)
        bot.pack(fill=X, pady=8)
        Label(bot, textvariable=self._count_var, font=FONT_SMALL,
              fg=TEXT_DIM, bg=BG_PANEL, padx=16).pack(side=LEFT)
        # Confirm / cancel
        Label(bot, text="Cancel", font=FONT_SMALL, fg=MUTED, bg=BG_PANEL,
              cursor="hand2", padx=16, pady=6).pack(side=RIGHT)
        bot.winfo_children()[-1].bind("<Button-1>", lambda e: self.destroy())
        add_btn = Label(bot, text="✓  Add to List", font=FONT_BOLD,
                        fg="#000", bg=self.color, cursor="hand2", padx=20, pady=6)
        add_btn.pack(side=RIGHT, padx=(0,8))
        add_btn.bind("<Button-1>", lambda e: self._confirm())

    def _tbtn(self, parent, text, cmd, fg):
        b = Label(parent, text=text, font=FONT_SMALL, fg=fg, bg=BG_PANEL,
                  cursor="hand2", padx=12, pady=6)
        b.pack(side=LEFT, padx=2)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(fg=WHITE))
        b.bind("<Leave>", lambda e: b.configure(fg=fg))

    def _browse_files(self):
        paths = filedialog.askopenfilenames(
            title="Select video files",
            parent=self,
            filetypes=[("Video files","*.mkv *.mp4 *.avi *.mov *.m4v *.wmv *.ts *.mpg *.mpeg"),
                       ("All files","*.*")])
        for p in paths:
            self._add_item(Path(p))

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select folder (subfolders included)", parent=self)
        if folder:
            self._add_item(Path(folder))

    def _add_item(self, path: Path):
        # Deduplicate
        existing = {i["path"] for i in self._items}
        if path in existing:
            return
        var = BooleanVar(value=False)
        self._items.append({"path": path, "kind": "folder" if path.is_dir() else "file", "var": var})
        self._render()

    def _remove_selected(self):
        self._items = [i for i in self._items if not i["var"].get()]
        self._render()

    def _render(self):
        for w in self._inner.winfo_children():
            w.destroy()
        if not self._items:
            self._empty_lbl = Label(self._inner,
                text="Use the buttons above to add files or folders",
                font=FONT_SMALL, fg=MUTED, bg=BG_DARK)
            self._empty_lbl.pack(pady=40)
            self._count_var.set("0 items")
            return

        for i, item in enumerate(self._items):
            bg = BG_ROW if i % 2 == 0 else BG_ROW_ALT
            row = Frame(self._inner, bg=bg)
            row.pack(fill=X)

            # Checkbox
            cb = Checkbutton(row, variable=item["var"], bg=bg,
                             selectcolor=BG_DARK, activebackground=bg,
                             highlightthickness=0, bd=0)
            cb.pack(side=LEFT, padx=(8,0))

            # Icon
            icon = "📁" if item["kind"] == "folder" else "🎬"
            Label(row, text=icon, font=FONT_SMALL, bg=bg, padx=4).pack(side=LEFT)

            # Path
            display = str(item["path"])
            Label(row, text=display, font=FONT_MONO_SM, fg=TEXT_DIM,
                  bg=bg, anchor=W).pack(side=LEFT, fill=X, expand=True, padx=(0,8), pady=6)

            # Subfolder note
            if item["kind"] == "folder":
                Label(row, text="recursive", font=("Segoe UI",8),
                      fg=self.color, bg=bg, padx=6).pack(side=RIGHT)

            Frame(self._inner, bg=BORDER, height=1).pack(fill=X)

        total_files = len(collect_video_files([i["path"] for i in self._items]))
        self._count_var.set(
            f"{len(self._items)} item(s) selected  ·  ~{total_files} video file(s) found")
        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _confirm(self):
        if not self._items:
            self.destroy()
            return
        self.result = collect_video_files([i["path"] for i in self._items])
        self.destroy()


# ── Tooltip ───────────────────────────────────────────────────────────────────
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget; self.text = text; self.tip = None
        widget.bind("<Enter>", self.show); widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        Label(self.tip, text=self.text, background="#2a2a42", foreground=TEXT_DIM,
              font=FONT_SMALL, padx=8, pady=4, relief="flat").pack()

    def hide(self, _=None):
        if self.tip: self.tip.destroy(); self.tip = None


# ── Search Picker Dialog ─────────────────────────────────────────────────────
class SearchPickerDialog(Toplevel):
    """
    Modal dialog shown when a show/movie lookup fails or is ambiguous.
    Displays search results as a selectable list with a live search bar.
    Sets self.chosen to the selected result dict, or None if skipped.
    """
    def __init__(self, parent, title: str, filename: str,
                 initial_query: str, search_fn, color):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.grab_set()
        self.focus_set()

        self.search_fn     = search_fn
        self.color         = color
        self.chosen        = None
        self._results      = []
        self._search_after = None

        self._build(filename, initial_query)

        # ── Centre over the parent window ─────────────────────────────────
        self.update_idletasks()
        w, h = 680, 520
        px = parent.winfo_rootx() + (parent.winfo_width()  - w) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{max(0,px)}+{max(0,py)}")

        self.after(100, lambda: self._do_search(initial_query))
        self.wait_window(self)

    def _build(self, filename: str, query: str):
        # ── Header ──
        hdr = Frame(self, bg=BG_PANEL, height=50)
        hdr.pack(fill=X); hdr.pack_propagate(False)
        Frame(hdr, bg=self.color, width=4).pack(side=LEFT, fill=Y)
        Label(hdr, text=self.title(), font=("Segoe UI",12,"bold"),
              fg=self.color, bg=BG_PANEL).pack(side=LEFT, padx=14, pady=0)
        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # ── File label ──
        Label(self, text=f"File:  {filename}", font=FONT_MONO_SM,
              fg=TEXT_DIM, bg=BG_DARK, anchor=W).pack(fill=X, padx=16, pady=(10,2))

        # ── Search bar ──
        sf = Frame(self, bg=BG_SURFACE, bd=0, highlightthickness=1,
                   highlightbackground=self.color)
        sf.pack(fill=X, padx=16, pady=(4,8))
        Label(sf, text="🔍", font=FONT_SMALL, fg=self.color,
              bg=BG_SURFACE, padx=8).pack(side=LEFT)
        self._q_var = StringVar(value=query)
        self._search_entry = Entry(sf, textvariable=self._q_var, font=FONT_MONO_SM,
                                   bg=BG_SURFACE, fg=TEXT, bd=0,
                                   insertbackground=self.color, highlightthickness=0)
        self._search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0,8), pady=7)
        self._search_entry.bind("<Return>", lambda e: self._do_search(self._q_var.get()))
        self._q_var.trace_add("write", self._on_query_change)

        # ── Results list ──
        list_frame = Frame(self, bg=BG_DARK)
        list_frame.pack(fill=BOTH, expand=True, padx=16, pady=(0,8))

        self._listbox_frame = Frame(list_frame, bg=BG_DARK)
        self._listbox_frame.pack(fill=BOTH, expand=True)

        # Scrollable results canvas
        self._res_canvas = Canvas(self._listbox_frame, bg=BG_DARK,
                                  highlightthickness=0, bd=0)
        res_sb = Scrollbar(self._listbox_frame, orient=VERTICAL,
                           command=self._res_canvas.yview,
                           bg=BG_SURFACE, troughcolor=BG_DARK)
        self._res_canvas.configure(yscrollcommand=res_sb.set)
        res_sb.pack(side=RIGHT, fill=Y)
        self._res_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self._res_inner = Frame(self._res_canvas, bg=BG_DARK)
        self._res_cwin  = self._res_canvas.create_window(
            (0,0), window=self._res_inner, anchor=NW)
        self._res_inner.bind("<Configure>",
            lambda e: self._res_canvas.configure(
                scrollregion=self._res_canvas.bbox("all")))
        self._res_canvas.bind("<Configure>",
            lambda e: self._res_canvas.itemconfig(self._res_cwin, width=e.width))
        self._res_canvas.bind_all("<MouseWheel>",
            lambda e: self._res_canvas.yview_scroll(int(-1*(e.delta/120)),"units"))

        self._status_lbl = Label(self._listbox_frame, text="Searching...",
                                  font=FONT_SMALL, fg=MUTED, bg=BG_DARK)

        # ── Buttons ──
        Frame(self, bg=BORDER, height=1).pack(fill=X)
        btn_row = Frame(self, bg=BG_PANEL); btn_row.pack(fill=X, pady=10)
        self._pick_btn = Label(btn_row, text="✓  Use Selected",
                                font=FONT_BOLD, fg="#000", bg=self.color,
                                cursor="hand2", padx=20, pady=8)
        self._pick_btn.pack(side=LEFT, padx=16)
        self._pick_btn.bind("<Button-1>", lambda e: self._confirm())

        Label(btn_row, text="Skip this file", font=FONT_SMALL,
              fg=MUTED, bg=BG_PANEL, cursor="hand2",
              padx=16, pady=8).pack(side=LEFT)
        btn_row.winfo_children()[-1].bind("<Button-1>", lambda e: self.destroy())

    def _on_query_change(self, *_):
        if self._search_after:
            self.after_cancel(self._search_after)
        self._search_after = self.after(500, lambda: self._do_search(self._q_var.get()))

    def _do_search(self, query: str):
        query = query.strip()
        if not query:
            return
        self._clear_results()
        self._status_lbl.pack(pady=20)
        self._status_lbl.config(text="Searching...")
        try:
            results = self.search_fn(query)
            self._results = results
            self._status_lbl.pack_forget()
            if not results:
                self._status_lbl.config(text="No results found — try a different search")
                self._status_lbl.pack(pady=20)
            else:
                self._render_results(results)
        except Exception as ex:
            self._status_lbl.config(text=f"Error: {ex}")
            self._status_lbl.pack(pady=20)

    def _clear_results(self):
        for w in self._res_inner.winfo_children():
            w.destroy()
        self._selected_idx = None

    def _render_results(self, results: list):
        self._selected_idx = None
        self._result_rows  = []
        for i, r in enumerate(results):
            self._make_result_row(i, r)

    def _make_result_row(self, i: int, result: dict):
        bg = BG_ROW if i % 2 == 0 else BG_ROW_ALT
        row = Frame(self._res_inner, bg=bg, cursor="hand2")
        row.pack(fill=X)

        # Top line: title + year
        top = Frame(row, bg=bg)
        top.pack(fill=X, padx=12, pady=(8,2))

        # Build display title
        if "name" in result:
            # TV show
            display = result["name"]
            meta    = f"{result.get('premiered','')}  {result.get('network','')}".strip()
            desc    = result.get("summary","")
        else:
            # Movie
            display = result["title"]
            meta    = result.get("year","")
            desc    = result.get("overview","")

        Label(top, text=display, font=("Segoe UI",10,"bold"),
              fg=TEXT, bg=bg, anchor=W).pack(side=LEFT)
        if meta:
            Label(top, text=f"  {meta}", font=FONT_SMALL,
                  fg=MUTED, bg=bg).pack(side=LEFT)

        if desc:
            Label(row, text=desc, font=FONT_SMALL, fg=TEXT_DIM,
                  bg=bg, anchor=W, wraplength=580, justify=LEFT).pack(
                  fill=X, padx=12, pady=(0,8))

        Frame(self._res_inner, bg=BORDER, height=1).pack(fill=X)
        self._result_rows.append(row)

        # Bind click to select
        def select(e, idx=i, r=row):
            self._select(idx)
        for w in [row] + row.winfo_children() + [
                c for child in row.winfo_children() for c in child.winfo_children()]:
            try: w.bind("<Button-1>", select)
            except Exception: pass

    def _select(self, idx: int):
        # Deselect previous
        if hasattr(self, "_selected_idx") and self._selected_idx is not None:
            prev_row = self._result_rows[self._selected_idx]
            bg = BG_ROW if self._selected_idx%2==0 else BG_ROW_ALT
            prev_row.configure(bg=bg)
            for c in prev_row.winfo_children():
                c.configure(bg=bg)
                for gc in c.winfo_children():
                    try: gc.configure(bg=bg)
                    except Exception: pass
        # Select new
        self._selected_idx = idx
        row = self._result_rows[idx]
        sel_bg = "#1e2a3a" if self.color == ACCENT_BLUE else "#2a1e00"
        row.configure(bg=sel_bg)
        for c in row.winfo_children():
            c.configure(bg=sel_bg)
            for gc in c.winfo_children():
                try: gc.configure(bg=sel_bg)
                except Exception: pass

    def _confirm(self):
        if not hasattr(self, "_selected_idx") or self._selected_idx is None:
            messagebox.showwarning("No Selection",
                "Please click a result to select it first.", parent=self)
            return
        self.chosen = self._results[self._selected_idx]
        self.destroy()


# ── Custom exception for "not found — show picker" ───────────────────────────
class LookupNotFoundError(Exception):
    def __init__(self, message: str, query: str):
        super().__init__(message)
        self.query = query


# ── Base Tab ──────────────────────────────────────────────────────────────────
class BaseTab(Frame):
    def __init__(self, parent, app, dest_var, color):
        super().__init__(parent, bg=BG_DARK)
        self.app          = app
        self.dest_var     = dest_var
        self.color        = color
        self.file_entries = []
        self.lookup_running = False
        self.opt_resolution  = BooleanVar(value=True)
        self.opt_video_codec = BooleanVar(value=True)
        self.opt_audio_codec = BooleanVar(value=True)
        self.file_mode       = StringVar(value="move")   # "move" or "copy"
        self.opt_strip_year  = BooleanVar(value=True)    # strip year from search query
        self.opt_use_year_in_folder  = BooleanVar(value=True)  # TV: include year in show folder/filename
        self.opt_create_movie_folder = BooleanVar(value=True)  # Movie: create per-movie subfolder
        self.opt_threads     = StringVar(value="5")      # concurrent lookup threads
        self._build()

    def _build(self):
        toolbar = Frame(self, bg=BG_PANEL, height=38)
        toolbar.pack(fill=X)
        toolbar.pack_propagate(False)
        self._toolbar(toolbar)
        Frame(self, bg=BORDER, height=1).pack(fill=X)

        body = Frame(self, bg=BG_DARK)
        body.pack(fill=BOTH, expand=True)

        left = Frame(body, bg=BG_DARK)
        left.pack(side=LEFT, fill=BOTH, expand=True)
        self._table(left)

        Frame(body, bg=BORDER, width=1).pack(side=RIGHT, fill=Y)
        right = Frame(body, bg=BG_PANEL, width=280)
        right.pack(side=RIGHT, fill=Y)
        right.pack_propagate(False)
        self._right_panel(right)

    def _toolbar(self, p):
        self._hbtn(p, "＋ Add Files",  self._add_files,  self.color)
        self._hbtn(p, "📁 Add Folder", self._add_folder, MUTED)
        self._hbtn(p, "✕ Clear All",  self._clear_all,  MUTED)

    def _table(self, parent):
        cols = Frame(parent, bg=BG_PANEL, height=34)
        cols.pack(fill=X)
        cols.pack_propagate(False)
        Label(cols, text="  ORIGINAL FILENAME", font=FONT_SMALL,
              fg=MUTED, bg=BG_PANEL, anchor=W).place(x=8,   y=9, width=340)
        Label(cols, text="NEW PLEX NAME",        font=FONT_SMALL,
              fg=MUTED, bg=BG_PANEL, anchor=W).place(x=360, y=9, width=380)
        Label(cols, text="STATUS",               font=FONT_SMALL,
              fg=MUTED, bg=BG_PANEL, anchor=W).place(x=752, y=9, width=100)
        Frame(parent, bg=BORDER, height=1).pack(fill=X)

        tf = Frame(parent, bg=BG_DARK)
        tf.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(tf, bg=BG_DARK, highlightthickness=0, bd=0)
        sb = Scrollbar(tf, orient=VERTICAL, command=self.canvas.yview,
                       bg=BG_SURFACE, troughcolor=BG_DARK)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.rows_frame = Frame(self.canvas, bg=BG_DARK)
        self._cwin = self.canvas.create_window((0, 0), window=self.rows_frame, anchor=NW)
        self.rows_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfig(self._cwin, width=e.width))
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.drop_overlay = Frame(self.canvas, bg=BG_DARK)
        self.drop_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        Label(self.drop_overlay, text="📂", font=("Segoe UI", 48),
              bg=BG_DARK, fg=MUTED).pack(pady=(120, 8))
        Label(self.drop_overlay, text="Drop video files or folders here",
              font=("Segoe UI", 14, "bold"), bg=BG_DARK, fg=TEXT_DIM).pack()
        Label(self.drop_overlay, text="or use Add Files / Add Folder above",
              font=FONT_SMALL, bg=BG_DARK, fg=MUTED).pack(pady=(4, 0))
        # Wire up drag-and-drop (requires tkinterdnd2)
        self.after(200, self._setup_dnd)

    def _right_panel(self, p):
        # ── Destination ───────────────────────────────────────────────────
        Label(p, text="DESTINATION", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(16, 4))
        df = Frame(p, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        df.pack(fill=X, padx=16, pady=(0, 4))
        Entry(df, textvariable=self.dest_var, font=FONT_MONO_SM, bg=BG_SURFACE,
              fg=TEXT, bd=0, insertbackground=self.color,
              highlightthickness=0).pack(side=LEFT, fill=X, expand=True, padx=8, pady=6)
        bb = Label(df, text="…", font=FONT_BOLD, fg=self.color,
                   bg=BG_SURFACE, cursor="hand2", padx=8)
        bb.pack(side=RIGHT)
        bb.bind("<Button-1>", lambda e: self._pick_dest())
        Label(p, text="Leave blank to rename in place",
              font=("Segoe UI", 8), fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(2, 0))

        Frame(p, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(10, 0))

        # ── Collapsible Settings section ──────────────────────────────────
        self._settings_open = BooleanVar(value=False)

        # Header row — click anywhere to toggle
        settings_hdr = Frame(p, bg=BG_PANEL, cursor="hand2")
        settings_hdr.pack(fill=X, padx=16, pady=(6, 0))

        self._settings_arrow = Label(settings_hdr, text="▶", font=("Segoe UI", 8, "bold"),
                                     fg=self.color, bg=BG_PANEL, width=2, anchor=W)
        self._settings_arrow.pack(side=LEFT)
        hdr_lbl = Label(settings_hdr, text="SETTINGS", font=("Segoe UI", 9, "bold"),
                        fg=self.color, bg=BG_PANEL)
        hdr_lbl.pack(side=LEFT)
        Label(settings_hdr, text="  File mode · Filename tags",
              font=("Segoe UI", 8), fg=MUTED, bg=BG_PANEL).pack(side=LEFT)

        for w in (settings_hdr, self._settings_arrow, hdr_lbl,
                  settings_hdr.winfo_children()[-1]):
            w.bind("<Button-1>", lambda e: self._toggle_settings())

        # Collapsible body
        self._settings_body = Frame(p, bg=BG_PANEL)
        # (not packed yet — collapsed by default)

        # ── File Mode inside body ─────────────────────────────────────────
        sb = self._settings_body
        Label(sb, text="FILE MODE", font=("Segoe UI", 8, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(10, 4))
        mode_frame = Frame(sb, bg=BG_SURFACE, bd=0, highlightthickness=1,
                           highlightbackground=BORDER)
        mode_frame.pack(fill=X, padx=16)
        self._mode_btns = {}
        mode_inner = Frame(mode_frame, bg=BG_SURFACE)
        mode_inner.pack(fill=X, padx=6, pady=6)
        for mode, icon, label, tip in [
            ("move", "✂", "Move",
             "Original file is moved and renamed.\nThe source file will no longer exist."),
            ("copy", "⎘", "Copy & Keep Original",
             "A renamed copy is created at the destination.\nThe original file is left untouched."),
        ]:
            is_sel = (mode == self.file_mode.get())
            btn_frame = Frame(mode_inner,
                              bg=self.color if is_sel else BG_ROW,
                              bd=0, highlightthickness=1,
                              highlightbackground=self.color if is_sel else BORDER,
                              cursor="hand2")
            btn_frame.pack(fill=X, pady=(0, 4))
            inner = Frame(btn_frame, bg=btn_frame["bg"])
            inner.pack(fill=X, padx=10, pady=7)
            Label(inner, text=icon, font=("Segoe UI", 13),
                  fg="#000" if is_sel else TEXT_DIM,
                  bg=btn_frame["bg"]).pack(side=LEFT, padx=(0, 8))
            txt_col = Frame(inner, bg=btn_frame["bg"])
            txt_col.pack(side=LEFT, fill=X, expand=True)
            Label(txt_col, text=label,
                  font=("Segoe UI", 9, "bold"),
                  fg="#000" if is_sel else TEXT,
                  bg=btn_frame["bg"], anchor=W).pack(anchor=W)
            Label(txt_col, text=tip.split("\n")[1],
                  font=("Segoe UI", 7),
                  fg="#000" if is_sel else MUTED,
                  bg=btn_frame["bg"], anchor=W, wraplength=190, justify=LEFT).pack(anchor=W)
            self._mode_btns[mode] = (btn_frame, inner,
                                     inner.winfo_children()[0],
                                     *txt_col.winfo_children())
            for w in ([btn_frame, inner, txt_col]
                      + list(inner.winfo_children())
                      + list(txt_col.winfo_children())):
                w.bind("<Button-1>", lambda e, m=mode: self._set_file_mode(m))

        # ── Include in Filename inside body ───────────────────────────────
        Frame(sb, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(10, 0))
        Label(sb, text="INCLUDE IN FILENAME", font=("Segoe UI", 8, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(8, 4))
        cbf = Frame(sb, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        cbf.pack(fill=X, padx=16)
        for txt, var, tip in [
            ("  Video Resolution  (e.g. 1080p)", self.opt_resolution,  "Append resolution tag"),
            ("  Video Codec       (e.g. HEVC)",  self.opt_video_codec, "Append video codec tag"),
            ("  Audio Channels    (e.g. 5.1)",   self.opt_audio_codec, "Append audio channel count"),
        ]:
            row = Frame(cbf, bg=BG_SURFACE)
            row.pack(fill=X, padx=10, pady=3)
            cb = Checkbutton(row, text=txt, variable=var, font=FONT_SMALL,
                             fg=TEXT, bg=BG_SURFACE, selectcolor=BG_DARK,
                             activebackground=BG_SURFACE, activeforeground=TEXT,
                             highlightthickness=0, bd=0, cursor="hand2",
                             command=self._update_preview)
            cb.pack(side=LEFT)
            Tooltip(cb, tip)

        # ── Search options inside body ────────────────────────────────────
        Frame(sb, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(8, 0))
        Label(sb, text="SEARCH OPTIONS", font=("Segoe UI", 8, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(8, 4))
        sof = Frame(sb, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        sof.pack(fill=X, padx=16)
        so_row = Frame(sof, bg=BG_SURFACE)
        so_row.pack(fill=X, padx=10, pady=3)
        so_cb = Checkbutton(so_row,
                            text="  Strip year from search query",
                            variable=self.opt_strip_year, font=FONT_SMALL,
                            fg=TEXT, bg=BG_SURFACE, selectcolor=BG_DARK,
                            activebackground=BG_SURFACE, activeforeground=TEXT,
                            highlightthickness=0, bd=0, cursor="hand2")
        so_cb.pack(side=LEFT)
        Tooltip(so_cb,
                "When a show/movie name contains a year (e.g. 'The Office (2005)')\n"
                "strip it before searching so results are not filtered too narrowly.")

        # Concurrent threads row
        thr_row = Frame(sof, bg=BG_SURFACE)
        thr_row.pack(fill=X, padx=10, pady=(0, 4))
        Label(thr_row, text="  Concurrent lookups", font=FONT_SMALL,
              fg=TEXT, bg=BG_SURFACE).pack(side=LEFT)

        THREAD_OPTIONS = ["5", "10", "15", "20", "25", "30"]
        thr_pill_row = Frame(sof, bg=BG_SURFACE)
        thr_pill_row.pack(fill=X, padx=10, pady=(0, 6))
        self._thread_btns = {}
        for val in THREAD_OPTIONS:
            is_sel = (val == self.opt_threads.get())
            b = Label(thr_pill_row, text=val,
                      font=("Segoe UI", 8, "bold"),
                      fg="#000" if is_sel else TEXT_DIM,
                      bg=self.color if is_sel else BG_DARK,
                      cursor="hand2", padx=8, pady=3)
            b.pack(side=LEFT, padx=2, pady=(0, 2))
            b.bind("<Button-1>", lambda e, v=val: self._set_threads(v))
            b.bind("<Enter>",    lambda e, b=b, v=val: b.configure(
                bg=self.color if v == self.opt_threads.get() else BG_HOVER,
                fg="#000" if v == self.opt_threads.get() else WHITE))
            b.bind("<Leave>",    lambda e, b=b, v=val: b.configure(
                bg=self.color if v == self.opt_threads.get() else BG_DARK,
                fg="#000" if v == self.opt_threads.get() else TEXT_DIM))
            self._thread_btns[val] = b

        # ── Folder structure options (tab-specific) ───────────────────────
        self._build_folder_options(sb)

        # ── Format preview inside body ────────────────────────────────────
        Frame(sb, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(8, 0))
        Label(sb, text="FORMAT PREVIEW", font=("Segoe UI", 8, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(8, 4))
        pbox = Frame(sb, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        pbox.pack(fill=X, padx=16, pady=(0, 10))
        self.preview_label = Label(pbox, text="", font=("Consolas", 8),
                                   fg=SUCCESS, bg=BG_SURFACE, wraplength=220,
                                   justify=LEFT, padx=10, pady=10)
        self.preview_label.pack()
        self._update_preview()

        self._action_divider = Frame(p, bg=BORDER, height=1)
        self._action_divider.pack(fill=X, padx=16, pady=(6, 0))

        # ── Action buttons ────────────────────────────────────────────────
        self.lookup_btn = self._make_lookup_btn(p)
        self.lookup_btn.pack(fill=X, padx=16, pady=(10, 6))

        self.prog_frame = Frame(p, bg=BG_PANEL)
        self.prog_frame.pack(fill=X, padx=16, pady=(0, 6))
        style = ttk.Style()
        style.configure(f"{id(self)}.Horizontal.TProgressbar",
                        troughcolor=BG_SURFACE, background=self.color,
                        borderwidth=0, lightcolor=self.color, darkcolor=self.color)
        self.progress   = ttk.Progressbar(self.prog_frame,
                                           style=f"{id(self)}.Horizontal.TProgressbar",
                                           mode="determinate", length=248)
        self.prog_label = Label(self.prog_frame, text="", font=FONT_SMALL,
                                fg=TEXT_DIM, bg=BG_PANEL)

        self.apply_btn = self._big_btn(p, "✓  Apply & Rename", self._apply_rename,
                                       SUCCESS, "#000", state=DISABLED)
        self.apply_btn.pack(fill=X, padx=16, pady=(0, 8))

        # Keep apply button label in sync with file mode
        def _update_apply_label(*_):
            is_copy = self.file_mode.get() == "copy"
            self.apply_btn.configure(
                text="⎘  Apply & Copy" if is_copy else "✓  Apply & Rename")
        self.file_mode.trace_add("write", _update_apply_label)

        Frame(p, bg=BORDER, height=1).pack(fill=X, padx=16, pady=6)

        # ── Summary ───────────────────────────────────────────────────────
        Label(p, text="SUMMARY", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(0, 6))
        sf = Frame(p, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        sf.pack(fill=X, padx=16)
        self.sum_total = self._srow(sf, "Total files", "0", TEXT_DIM)
        self.sum_ready = self._srow(sf, "Matched",     "0", SUCCESS)
        self.sum_skip  = self._srow(sf, "Unmatched",   "0", MUTED)
        self.sum_error = self._srow(sf, "Errors",      "0", ERROR)

    def _set_threads(self, val: str):
        """Update the concurrent-thread count and repaint the pill buttons."""
        self.opt_threads.set(val)
        for v, b in self._thread_btns.items():
            sel = (v == val)
            b.configure(
                bg=self.color if sel else BG_DARK,
                fg="#000"    if sel else TEXT_DIM,
            )

    def _make_source_pill(self, parent, src: str, is_sel: bool, accent,
                          on_click, on_enter_bg, on_leave_bg):
        """
        Create a pill button Frame with a brand icon + source name label.
        Returns (pill_frame, [all_child_widgets]) so callers can update bg/fg.
        """
        bg  = accent if is_sel else BG_SURFACE
        fg  = "#000" if is_sel else TEXT_DIM

        pill = Frame(parent, bg=bg, cursor="hand2", padx=0, pady=0)
        pill.pack(side=LEFT, padx=2)

        # Icon
        icon_img = get_source_icon(src)
        children = []
        if icon_img:
            ico_lbl = Label(pill, image=icon_img, bg=bg,
                            cursor="hand2", padx=3, pady=3)
            ico_lbl.pack(side=LEFT)
            ico_lbl._img_ref = icon_img   # prevent GC
            children.append(ico_lbl)

        # Text
        txt_lbl = Label(pill, text=src, font=("Segoe UI", 9, "bold"),
                        fg=fg, bg=bg, cursor="hand2", padx=(4 if icon_img else 10), pady=4)
        txt_lbl.pack(side=LEFT, padx=(0, 6))
        children.append(txt_lbl)

        all_widgets = [pill] + children

        def _enter(e, s=src):
            sel_now = (s == self._source_var.get())
            c = accent if sel_now else on_enter_bg
            f = "#000" if sel_now else WHITE
            for w in all_widgets:
                try: w.configure(bg=c)
                except Exception: pass
            txt_lbl.configure(fg=f)

        def _leave(e, s=src):
            sel_now = (s == self._source_var.get())
            c = accent if sel_now else on_leave_bg
            f = "#000" if sel_now else TEXT_DIM
            for w in all_widgets:
                try: w.configure(bg=c)
                except Exception: pass
            txt_lbl.configure(fg=f)

        def _click(e):
            on_click(src)

        for w in all_widgets:
            w.bind("<Button-1>", _click)
            w.bind("<Enter>",    _enter)
            w.bind("<Leave>",    _leave)

        return pill, all_widgets, txt_lbl

    def _build_folder_options(self, parent): pass  # override in subclasses

    def _toggle_settings(self):
        """Expand or collapse the Settings body."""
        if self._settings_open.get():
            self._settings_body.pack_forget()
            self._settings_arrow.configure(text="▶")
            self._settings_open.set(False)
        else:
            # Pack the body just before the divider that precedes the action buttons.
            # We stored a reference to that divider as self._action_divider.
            self._settings_body.pack(fill=X, before=self._action_divider)
            self._settings_arrow.configure(text="▼")
            self._settings_open.set(True)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _set_file_mode(self, mode: str):
        """Switch between 'move' and 'copy' and repaint the toggle buttons."""
        self.file_mode.set(mode)
        for m, widgets in self._mode_btns.items():
            btn_frame, inner, icon_lbl, *txt_lbls = widgets
            sel   = (m == mode)
            col_c = self.color if sel else BG_ROW
            bdr   = self.color if sel else BORDER
            fg_c  = "#000"    if sel else TEXT
            fg_m  = "#000"    if sel else MUTED
            fg_i  = "#000"    if sel else TEXT_DIM
            btn_frame.configure(bg=col_c,
                                highlightbackground=bdr)
            inner.configure(bg=col_c)
            icon_lbl.configure(bg=col_c, fg=fg_i)
            for i, lbl in enumerate(txt_lbls):
                lbl.configure(bg=col_c, fg=fg_c if i == 0 else fg_m)
            for w in [inner] + list(inner.winfo_children()):
                try:
                    w.configure(bg=col_c)
                except Exception:
                    pass

    def _lookup_label(self): return "🔍  Lookup"

    def _hbtn(self, p, text, cmd, fg):
        b = Label(p, text=text, font=FONT_SMALL, fg=fg, bg=BG_PANEL,
                  cursor="hand2", padx=12, pady=6)
        b.pack(side=LEFT, padx=2)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(fg=WHITE))
        b.bind("<Leave>", lambda e: b.configure(fg=fg))
        return b

    def _big_btn(self, p, text, cmd, bg, fg="#fff", state=NORMAL):
        b = Label(p, text=text, font=FONT_BOLD, fg=fg, bg=bg,
                  cursor="hand2" if state==NORMAL else "arrow",
                  padx=0, pady=12, anchor=CENTER)
        if state == NORMAL:
            b.bind("<Button-1>", lambda e: cmd())
            b.bind("<Enter>",    lambda e: b.configure(bg=self._lighten(bg)))
            b.bind("<Leave>",    lambda e: b.configure(bg=bg))
        else:
            b.configure(fg=MUTED, bg=BG_SURFACE)
        b._base_bg = bg; b._base_fg = fg
        return b

    def _make_lookup_btn(self, parent):
        """
        Build the Lookup button as a Frame containing an icon Label + text Label.
        The frame proxies .configure(text=...), .bind(), and .unbind() so that
        the existing _enable_btn/_disable_btn helpers work without changes.
        """
        bg = self.color
        fg = "#000"

        frame = Frame(parent, bg=bg, cursor="hand2")
        frame._base_bg = bg
        frame._base_fg = fg

        # Icon slot — populated by _update_lookup_icon
        self._lookup_icon_lbl = Label(frame, image="", bg=bg,
                                      cursor="hand2", padx=4, pady=12)
        self._lookup_icon_lbl.pack(side=LEFT, padx=(8, 0))

        # Text label
        self._lookup_text_lbl = Label(frame, text=self._lookup_label(),
                                      font=FONT_BOLD, fg=fg, bg=bg,
                                      cursor="hand2", padx=4, pady=12)
        self._lookup_text_lbl.pack(side=LEFT, fill=X, expand=True)

        # ── Proxy interface so _enable_btn / _disable_btn still work ──────
        # Save real Tkinter bind/unbind/configure BEFORE we override them
        _real_bind      = Frame.bind
        _real_unbind    = Frame.unbind
        _real_configure = Frame.configure

        def _frame_configure(**kw):
            if "text" in kw:
                self._lookup_text_lbl.configure(text=kw.pop("text"))
            if "fg" in kw:
                col = kw["fg"]
                self._lookup_text_lbl.configure(fg=col)
                self._lookup_icon_lbl.configure(fg=col)
            if "bg" in kw:
                col = kw["bg"]
                _real_configure(frame, bg=col)
                self._lookup_text_lbl.configure(bg=col)
                self._lookup_icon_lbl.configure(bg=col)
            if "cursor" in kw:
                cur = kw["cursor"]
                _real_configure(frame, cursor=cur)
                self._lookup_text_lbl.configure(cursor=cur)
                self._lookup_icon_lbl.configure(cursor=cur)

        def _frame_bind(event, handler):
            _real_bind(frame, event, handler)
            self._lookup_icon_lbl.bind(event, handler)
            self._lookup_text_lbl.bind(event, handler)

        def _frame_unbind(event):
            _real_unbind(frame, event)
            self._lookup_icon_lbl.unbind(event)
            self._lookup_text_lbl.unbind(event)

        frame.configure = lambda **kw: _frame_configure(**kw)
        frame.bind      = lambda event, handler=None, **kw: (
            _frame_bind(event, handler) if handler else _real_bind(frame, event, **kw))
        frame.unbind    = lambda event, *a: _frame_unbind(event)

        # Hover effect — use real bind directly (proxy not yet needed here,
        # but using _frame_bind ensures icon + text labels also respond)
        def _on_enter(e):
            c = self._lighten(frame._base_bg)
            _real_configure(frame, bg=c)
            self._lookup_text_lbl.configure(bg=c)
            self._lookup_icon_lbl.configure(bg=c)

        def _on_leave(e):
            _real_configure(frame, bg=frame._base_bg)
            self._lookup_text_lbl.configure(bg=frame._base_bg)
            self._lookup_icon_lbl.configure(bg=frame._base_bg)

        for w in [frame, self._lookup_icon_lbl, self._lookup_text_lbl]:
            _real_bind(w, "<Enter>",    _on_enter)
            _real_bind(w, "<Leave>",    _on_leave)
            _real_bind(w, "<Button-1>", lambda e: self._start_lookup())

        # Load icon for the default source
        self._update_lookup_icon()
        return frame

    def _update_lookup_icon(self):
        """Refresh the icon on the lookup button to match the current source."""
        src = getattr(self, "_source_var", None)
        src_name = src.get() if src else None
        img = get_source_icon(src_name) if src_name else None
        if not hasattr(self, "_lookup_icon_lbl"):
            return
        try:
            if img:
                self._lookup_icon_lbl.configure(image=img)
                self._lookup_icon_lbl._img_ref = img
                self._lookup_icon_lbl.pack(side=LEFT, padx=(8, 0))
            else:
                self._lookup_icon_lbl.configure(image="")
                self._lookup_icon_lbl.pack_forget()
        except Exception:
            pass

    def _maybe_enable_apply(self):
        """Enable the Apply button only when no lookup is running and some entries are ready."""
        if not self.lookup_running and any(e["status"] == "done" for e in self.file_entries):
            self._enable_btn(self.apply_btn, self._apply_rename)
        else:
            self._disable_btn(self.apply_btn)

    def _enable_btn(self, btn, cmd):
        btn.configure(fg=btn._base_fg, bg=btn._base_bg, cursor="hand2")
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e: btn.configure(bg=self._lighten(btn._base_bg)))
        btn.bind("<Leave>",    lambda e: btn.configure(bg=btn._base_bg))

    def _disable_btn(self, btn):
        btn.configure(fg=MUTED, bg=BG_SURFACE, cursor="arrow")
        btn.unbind("<Enter>"); btn.unbind("<Leave>"); btn.unbind("<Button-1>")

    def _lighten(self, hc):
        h = hc.lstrip("#")
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        return "#{:02x}{:02x}{:02x}".format(
            min(255,int(r*1.15)),min(255,int(g*1.15)),min(255,int(b*1.15)))

    def _srow(self, p, label, val, vc):
        row = Frame(p, bg=BG_SURFACE); row.pack(fill=X, padx=10, pady=3)
        Label(row, text=label, font=FONT_SMALL, fg=TEXT_DIM,
              bg=BG_SURFACE, anchor=W).pack(side=LEFT)
        lbl = Label(row, text=val, font=("Segoe UI",9,"bold"),
                    fg=vc, bg=BG_SURFACE, anchor=E)
        lbl.pack(side=RIGHT)
        return lbl

    # ── File management ───────────────────────────────────────────────────────
    def _add_files(self):
        dlg = AddFilesDialog(self.app, self.color)
        if dlg.result:
            self._ingest(dlg.result)

    def _add_folder(self):
        folder = filedialog.askdirectory(title="Select folder (subfolders included)")
        if folder:
            self._ingest(collect_video_files([Path(folder)]))

    def _pick_dest(self):
        f = filedialog.askdirectory(title="Select destination folder")
        if f: self.dest_var.set(f)

    def _ingest(self, paths):
        existing = {e["path"] for e in self.file_entries}
        added = 0
        for p in paths:
            if p in existing: continue
            self.file_entries.append({
                "path": p, "parsed": self._parse(p.name),
                "new_name": None, "status": "pending",
                "media_info": None
            })
            existing.add(p); added += 1
        if added:
            # Remember the parent folder of the most recently added file
            last = paths[-1] if paths else None
            if last:
                self.app.last_source_folder = str(Path(last).parent)
            self._refresh()
            self._summary()
            self.drop_overlay.place_forget()
            self.app.set_status(f"Added {added} file(s)")

    def _parse(self, filename): return None   # override

    def _setup_dnd(self):
        """Register drag-and-drop on canvas and overlay using tkinterdnd2."""
        try:
            from tkinterdnd2 import DND_FILES
            for widget in (self.canvas, self.drop_overlay,
                           *self.drop_overlay.winfo_children()):
                try:
                    widget.drop_target_register(DND_FILES)
                    widget.dnd_bind("<<Drop>>", self._on_drop)
                except Exception:
                    pass
        except ImportError:
            pass  # tkinterdnd2 not installed — use buttons instead

    def _on_drop(self, event):
        """Handle files/folders dropped onto the canvas."""
        try:
            # tkinterdnd2 gives a Tcl list string — parse it properly
            raw   = event.data
            paths = self.tk.splitlist(raw)
            found = collect_video_files([Path(p) for p in paths])
            if found:
                self._ingest(found)
        except Exception:
            pass

    def _clear_all(self):
        self.file_entries.clear()
        self._refresh(); self._summary()
        self._disable_btn(self.apply_btn)
        self.drop_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.drop_overlay.lift()
        self.app.set_status("Cleared")

    def _remove(self, idx):
        if 0 <= idx < len(self.file_entries):
            self.file_entries.pop(idx)
            self._refresh(); self._summary()
            if not self.file_entries:
                self.drop_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
                self.drop_overlay.lift()

    # ── Table ─────────────────────────────────────────────────────────────────
    def _refresh(self):
        """
        Full rebuild — only called when the entry list itself changes
        (files added, removed, or count changes).  Status-only changes use
        _update_rows() instead to avoid flicker.
        """
        for w in self.rows_frame.winfo_children():
            w.destroy()
        self._row_widgets    = {}   # entry_id -> (new_name_lbl, badge_lbl)
        self._painted_status = {}   # entry_id -> last painted status
        for i, e in enumerate(self.file_entries):
            self._row(e, i, BG_ROW if i % 2 == 0 else BG_ROW_ALT)
        self.app.file_count_label.config(
            text=f"{len(self.file_entries)} file{'s' if len(self.file_entries) != 1 else ''}")
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _update_rows(self):
        """
        Flicker-free in-place update. Only repaints rows whose status
        actually changed since the last paint. Skips unchanged rows so
        large lists (300+ entries) don't cause lag.
        Falls back to a full _refresh if entry count changed.
        """
        if not hasattr(self, "_row_widgets"):
            self._refresh()
            return
        if len(self._row_widgets) != len(self.file_entries):
            self._refresh()
            return

        if not hasattr(self, "_painted_status"):
            self._painted_status = {}

        fg_map = {"pending": MUTED, "loading": WARNING, "done": SUCCESS,
                  "error": ERROR, "renamed": ACCENT}
        text_map_fn = lambda e: {
            "pending": "— waiting —",
            "loading": "⟳ Looking up...",
            "done":    e.get("new_name") or "—",
            "error":   f"✗ {e.get('error_msg', 'Error')}",
            "renamed": f"✓ {e.get('new_name', '')}",
        }.get(e["status"], "—")
        badge_map = {
            "pending": ("PENDING", MUTED,    BG_SURFACE),
            "loading": ("LOOKUP",  WARNING,  "#2a1f00"),
            "done":    ("READY",   SUCCESS,  "#0d2a1a"),
            "error":   ("ERROR",   ERROR,    "#2a0d0d"),
            "renamed": ("DONE",    ACCENT,   "#2a1f00"),
        }

        for entry in self.file_entries:
            eid = id(entry)
            st  = entry["status"]
            # Skip rows that haven't changed since last paint
            if self._painted_status.get(eid) == st:
                continue
            if eid not in self._row_widgets:
                continue
            new_lbl, badge_lbl = self._row_widgets[eid]
            try:
                new_lbl.configure(text=text_map_fn(entry), fg=fg_map.get(st, MUTED))
                pt, pf, pb = badge_map.get(st, ("—", MUTED, BG_SURFACE))
                badge_lbl.configure(text=pt, fg=pf, bg=pb)
                self._painted_status[eid] = st
            except Exception:
                pass

        self._summary()

    def _row(self, entry, idx, bg):
        if not hasattr(self, "_row_widgets"):
            self._row_widgets = {}

        row = Frame(self.rows_frame, bg=bg, height=38)
        row.pack(fill=X); row.pack_propagate(False)
        on_e = lambda e, r=row: (r.configure(bg=BG_HOVER),
               [c.configure(bg=BG_HOVER) for c in r.winfo_children()])
        on_l = lambda e, r=row, b=bg: (r.configure(bg=b),
               [c.configure(bg=b) for c in r.winfo_children()])
        row.bind("<Enter>", on_e); row.bind("<Leave>", on_l)

        rm = Label(row, text="✕", font=("Segoe UI", 9), fg=MUTED, bg=bg, cursor="hand2", padx=6)
        rm.pack(side=LEFT)
        rm.bind("<Button-1>", lambda e, i=idx: self._remove(i))
        rm.bind("<Enter>",    lambda e, l=rm: l.configure(fg=ERROR))
        rm.bind("<Leave>",    lambda e, l=rm, b=bg: l.configure(fg=MUTED))

        orig = Label(row, text=entry["path"].name, font=FONT_MONO_SM,
                     fg=TEXT_DIM, bg=bg, anchor=W, width=42)
        orig.pack(side=LEFT, padx=(2, 0))
        Tooltip(orig, str(entry["path"]) + "\n\nRight-click for manual search")

        Label(row, text=" → ", font=FONT_SMALL, fg=MUTED, bg=bg).pack(side=LEFT)

        st = entry["status"]
        fg_map   = {"pending": MUTED, "loading": WARNING, "done": SUCCESS,
                    "error": ERROR, "renamed": ACCENT}
        text_map = {
            "pending": "— waiting —",
            "loading": "⟳ Looking up...",
            "done":    entry.get("new_name") or "—",
            "error":   f"✗ {entry.get('error_msg', 'Error')}",
            "renamed": f"✓ {entry.get('new_name', '')}",
        }
        new_lbl = Label(row, text=text_map.get(st, "—"), font=FONT_MONO_SM,
                        fg=fg_map.get(st, MUTED), bg=bg, anchor=W)
        new_lbl.pack(side=LEFT, fill=X, expand=True, padx=(0, 6))

        pt, pf, pb = {"pending": ("PENDING", MUTED,   BG_SURFACE),
                      "loading": ("LOOKUP",  WARNING,  "#2a1f00"),
                      "done":    ("READY",   SUCCESS,  "#0d2a1a"),
                      "error":   ("ERROR",   ERROR,    "#2a0d0d"),
                      "renamed": ("DONE",    ACCENT,   "#2a1f00")}.get(st, ("—", MUTED, BG_SURFACE))
        badge_lbl = Label(row, text=pt, font=("Segoe UI", 8, "bold"),
                          fg=pf, bg=pb, padx=8, pady=2)
        badge_lbl.pack(side=RIGHT, padx=8)

        # Store references to the dynamic labels so _update_rows can patch them
        self._row_widgets[id(entry)] = (new_lbl, badge_lbl)

        Frame(self.rows_frame, bg=BORDER, height=1).pack(fill=X)

        # ── Right-click context menu ───────────────────────────────────────
        def _show_ctx(event, e=entry):
            if e["status"] == "loading":
                return
            menu = Menu(self, tearoff=0, bg=BG_SURFACE, fg=TEXT,
                        activebackground=self.color, activeforeground="#000",
                        font=FONT_SMALL, bd=0, relief="flat")
            menu.add_command(
                label="🔍  Manual Search…",
                command=lambda: self._manual_search(e))
            if e["status"] in ("done", "error"):
                menu.add_command(
                    label="🔄  Re-run Auto Lookup",
                    command=lambda: self._rerun_single(e))
            menu.add_separator()
            menu.add_command(
                label="✕  Remove from list",
                command=lambda: self._remove(idx))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        for w in [row] + list(row.winfo_children()):
            w.bind("<Button-3>", _show_ctx)
            w.bind("<Control-Button-1>", _show_ctx)

        # ── Subtitle sub-rows ──────────────────────────────────────────────
        for sub in entry.get("subtitles", []):
            sub_bg = "#161620"
            srow = Frame(self.rows_frame, bg=sub_bg, height=28)
            srow.pack(fill=X); srow.pack_propagate(False)

            Label(srow, text="   ↳", font=("Segoe UI", 9), fg=MUTED,
                  bg=sub_bg, padx=6).pack(side=LEFT)
            Label(srow, text="SUB", font=("Segoe UI", 7, "bold"),
                  fg="#6688aa", bg=sub_bg, padx=4).pack(side=LEFT)
            Label(srow, text=sub["path"].name, font=FONT_MONO_SM,
                  fg="#5566aa", bg=sub_bg, anchor=W, width=40).pack(side=LEFT, padx=(2, 0))
            Label(srow, text=" → ", font=FONT_SMALL, fg=MUTED,
                  bg=sub_bg).pack(side=LEFT)
            new_sub_fg = SUCCESS if st in ("done", "renamed") else MUTED
            Label(srow, text=sub.get("new_name", "—"), font=FONT_MONO_SM,
                  fg=new_sub_fg, bg=sub_bg, anchor=W).pack(
                  side=LEFT, fill=X, expand=True, padx=(0, 8))
            Frame(self.rows_frame, bg="#1a1a28", height=1).pack(fill=X)


    # ── Manual search (right-click) ───────────────────────────────────────────
    def _manual_search(self, entry):
        """Open the picker dialog pre-filled with the original filename's parsed name."""
        if self.lookup_running:
            messagebox.showinfo("Lookup Running",
                "Please wait for the current lookup to finish.", parent=self.app)
            return
        parsed = entry.get("parsed")
        if parsed:
            query = parsed.get("show_name") or parsed.get("raw_title") or entry["path"].stem
        else:
            query = entry["path"].stem
        dlg = self._show_picker(entry, query)
        if dlg and dlg.chosen:
            entry["status"] = "loading"
            self._update_rows()
            def do_it(e=entry, choice=dlg.chosen):
                try:
                    self._do_lookup_with_choice(e, choice)
                except Exception as ex:
                    e["status"]    = "error"
                    e["error_msg"] = str(ex)
                self.after(0, self._update_rows)
                self.after(0, self._maybe_enable_apply)
            threading.Thread(target=do_it, daemon=True).start()

    def _rerun_single(self, entry):
        """Re-run the auto lookup for a single entry on a background thread."""
        if self.lookup_running:
            messagebox.showinfo("Lookup Running",
                "Please wait for the current lookup to finish.", parent=self.app)
            return
        entry["status"] = "loading"
        self._update_rows()
        def do_it(e=entry):
            try:
                self._do_lookup(e)
            except LookupNotFoundError as ex:
                event  = threading.Event()
                chosen = [None]
                def show_picker(e=e, ex=ex, event=event, chosen=chosen):
                    dlg       = self._show_picker(e, str(ex.query))
                    chosen[0] = dlg.chosen if dlg else None
                    event.set()
                self.after(0, show_picker)
                event.wait()
                if chosen[0]:
                    try:
                        self._do_lookup_with_choice(e, chosen[0])
                    except Exception as ex2:
                        e["status"]    = "error"
                        e["error_msg"] = str(ex2)
                else:
                    e["status"]    = "error"
                    e["error_msg"] = "Skipped by user"
            except Exception as ex:
                e["status"]    = "error"
                e["error_msg"] = str(ex)
            self.after(0, self._update_rows)
            self.after(0, self._maybe_enable_apply)
        threading.Thread(target=do_it, daemon=True).start()

    # ── Lookup ────────────────────────────────────────────────────────────────
    def _start_lookup(self):
        if self.lookup_running: return
        if not self.file_entries:
            messagebox.showwarning("No Files", "Add some video files first."); return
        self.lookup_running = True
        self.lookup_btn.configure(text=self._lookup_label())
        self._disable_btn(self.lookup_btn)
        self._disable_btn(self.apply_btn)
        self.progress.pack(fill=X, pady=(0,4))
        self.prog_label.pack(fill=X)
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        """
        Everything runs on background threads — the UI is never blocked.

        Flow:
          1. Mark error/pending entries as loading  (instant, on this thread)
          2. Call _build_work_batches()              (may do network I/O on this thread for TV show resolution)
          3. Fan out episode/movie fetches in a ThreadPoolExecutor
          4. Picker dialogs are marshalled to the main thread via self.after()
             and a threading.Event; worker threads block only on their own event.
        """
        import queue as _queue
        from concurrent.futures import ThreadPoolExecutor, as_completed

        PARALLELISM  = int(self.opt_threads.get())
        completed    = [0]
        lock         = threading.Lock()
        picker_queue = _queue.Queue()

        # ── Mark only error/pending entries as loading ────────────────────
        for entry in self.file_entries:
            if entry["status"] in ("error", "pending"):
                entry["status"] = "loading"
        self.after(0, self._refresh)

        # ── Build the work list (may resolve shows in parallel internally) ─
        work  = self._build_work_batches()
        total = len(work)

        if total == 0:
            self.after(0, self._lookup_done)
            return

        def tick(name):
            with lock:
                completed[0] += 1
                done = completed[0]
            self._prog(done, total, name)

        def run_entry(entry):
            if entry["status"] == "renamed":
                tick(entry["path"].name)
                return
            try:
                self._do_lookup(entry)
            except LookupNotFoundError as ex:
                ev     = threading.Event()
                chosen = [None]
                picker_queue.put((entry, str(ex.query), ev, chosen))
                ev.wait()
                if chosen[0]:
                    try:
                        self._do_lookup_with_choice(entry, chosen[0])
                    except Exception as ex2:
                        entry["status"]    = "error"
                        entry["error_msg"] = str(ex2)
                else:
                    entry["status"]    = "error"
                    entry["error_msg"] = "Skipped by user"
            except Exception as ex:
                entry["status"]    = "error"
                entry["error_msg"] = str(ex)
            tick(entry["path"].name)

        def drain_pickers():
            try:
                while True:
                    entry, query, ev, chosen = picker_queue.get_nowait()
                    dlg       = self._show_picker(entry, query)
                    chosen[0] = dlg.chosen if dlg else None
                    ev.set()
            except _queue.Empty:
                pass

        def pool_worker():
            with ThreadPoolExecutor(max_workers=PARALLELISM) as executor:
                futures = {executor.submit(run_entry, e): e for e in work}
                for _ in as_completed(futures):
                    pass

        def schedule_drain():
            drain_pickers()
            if self.lookup_running:
                self.after(150, schedule_drain)

        self.after(0, schedule_drain)
        pool_worker()
        self.after(0, drain_pickers)
        self.after(0, self._lookup_done)

    def _build_work_batches(self) -> list:
        """Return entries that still need processing (error or pending/loading)."""
        return [e for e in self.file_entries
                if e["status"] in ("error", "pending", "loading")]

    def _do_lookup(self, entry): pass           # override
    def _show_picker(self, entry, query): return None  # override
    def _do_lookup_with_choice(self, entry, choice): pass  # override

    def _prog(self, done, total, name):
        """
        Thread-safe progress update with debouncing.
        Parallel threads firing rapidly are coalesced into a single
        UI repaint every ~100 ms to avoid flooding the event queue.
        """
        self._prog_done  = done
        self._prog_total = total
        self._prog_name  = name
        if not getattr(self, "_prog_pending", False):
            self._prog_pending = True
            self.after(100, self._flush_prog)

    def _flush_prog(self):
        """Apply the latest progress values to the UI (runs on main thread)."""
        self._prog_pending = False
        done  = getattr(self, "_prog_done",  0)
        total = getattr(self, "_prog_total", 1)
        name  = getattr(self, "_prog_name",  "")
        pct   = int(done / total * 100) if total else 0
        short = name[:50] + "…" if len(name) > 50 else name
        try:
            self.progress.configure(value=pct)
            self.prog_label.configure(text=f"{done}/{total}  {short}")
        except Exception:
            pass
        self._update_rows()
        self._scroll_to_active()

    def _scroll_to_active(self):
        """Scroll the file list so the first 'loading' or most-recently-updated row is visible."""
        active_idx = None
        for i, e in enumerate(self.file_entries):
            if e["status"] == "loading":
                active_idx = i
                break
        if active_idx is None:
            for i, e in enumerate(self.file_entries):
                if e["status"] in ("done", "error", "renamed"):
                    active_idx = i
        if active_idx is None:
            return
        try:
            self.canvas.update_idletasks()
            bbox = self.canvas.bbox("all")
            if not bbox:
                return
            total_height = bbox[3] - bbox[1]
            if total_height <= 0:
                return
            n = len(self.file_entries)
            if n == 0:
                return
            row_fraction = active_idx / n
            scroll_to    = max(0.0, min(1.0, row_fraction - 0.15))
            self.canvas.yview_moveto(scroll_to)
        except Exception:
            pass

    def _lookup_done(self):
        self.lookup_running = False
        has_errors = any(e["status"] == "error" for e in self.file_entries)
        btn_label  = (f"🔄  Retry Errors ({sum(1 for e in self.file_entries if e['status'] == 'error')})"
                      if has_errors else self._lookup_label())
        self.lookup_btn.configure(text=btn_label)
        self._enable_btn(self.lookup_btn, self._start_lookup)
        self._maybe_enable_apply()
        ready  = sum(1 for e in self.file_entries if e["status"] == "done")
        errors = sum(1 for e in self.file_entries if e["status"] == "error")
        self.app.set_status(f"Lookup complete — {ready} ready, {errors} errors")
        self.after(2500, lambda: [self.progress.pack_forget(), self.prog_label.pack_forget()])

    # ── Apply / Dry run ───────────────────────────────────────────────────────
    def _dest_for(self, entry):
        dest = self.dest_var.get().strip()
        if dest:
            sub = self._subfolder(entry)   # may be a multi-part path like "Show (2001)/Season 01"
            if sub:
                # Safe-name each component individually so path separators are preserved
                safe_sub = Path(*[safe_name(part) for part in Path(sub).parts])
                return Path(dest) / safe_sub
            return Path(dest)
        return entry["path"].parent

    def _subfolder(self, entry): return ""  # override

    def _dry_run(self):
        ready = [e for e in self.file_entries if e["status"]=="done"]
        if not ready:
            messagebox.showinfo("Nothing Ready","Run Lookup first."); return
        is_copy = self.file_mode.get() == "copy"
        header  = "PREVIEW — no files will be changed\n"
        header += f"Mode: {'COPY (originals kept)' if is_copy else 'MOVE (originals will be removed)'}\n"
        lines = [header, "="*60]
        for e in ready:
            lines.append(f"\n  FROM:  {e['path'].name}")
            lines.append(f"    TO:  {self._dest_for(e) / e['new_name']}")
        self._log("Preview (Dry Run)", "\n".join(lines))

    def _apply_rename(self):
        ready = [e for e in self.file_entries if e["status"] == "done"]
        if not ready:
            messagebox.showinfo("Nothing Ready", "Run Lookup first.")
            return
        dest_root = self.dest_var.get().strip()
        dest_path = Path(dest_root) if dest_root else None
        is_copy   = (self.file_mode.get() == "copy")

        if dest_path and not dest_path.exists():
            if messagebox.askyesno("Create Folder?",
                    f"Destination doesn't exist:\n{dest_path}\n\nCreate it?"):
                dest_path.mkdir(parents=True)
            else:
                return

        # Disable buttons while running
        self._disable_btn(self.apply_btn)
        self._disable_btn(self.lookup_btn)
        self.app.set_status("Renaming…")

        def _do_rename():
            from concurrent.futures import ThreadPoolExecutor, as_completed as _as_completed
            import datetime

            parallelism = int(self.opt_threads.get())
            lock        = threading.Lock()
            renamed_c   = [0]; errors_c = [0]; sub_c = [0]
            src_folders = set()
            self._rename_flush_pending = False
            self._rename_active        = True

            # ── Debounced UI refresh — fires every 150 ms while renaming ──
            def _rename_tick():
                if self._rename_flush_pending:
                    self._rename_flush_pending = False
                    self._remove_renamed_and_refresh()
                if self._rename_active:
                    self.after(150, _rename_tick)

            self.after(150, _rename_tick)

            def rename_one(e):
                src     = e["path"]
                tgt_dir = self._dest_for(e)
                tgt     = tgt_dir / e["new_name"]
                local_subs = 0
                try:
                    tgt_dir.mkdir(parents=True, exist_ok=True)
                    subs = find_subtitle_siblings(src)

                    e["_orig_name"] = src.name
                    if is_copy:
                        shutil.copy2(str(src), str(tgt))
                    else:
                        shutil.move(str(src), str(tgt)) if dest_path else src.rename(tgt)
                        with lock:
                            src_folders.add(src.parent)

                    e["path"]   = tgt
                    e["status"] = "renamed"
                    with lock:
                        renamed_c[0] += 1

                    for sub in subs:
                        new_sub_name = build_subtitle_name(e["new_name"], sub)
                        sub_tgt      = tgt_dir / new_sub_name
                        try:
                            if is_copy:
                                shutil.copy2(str(sub), str(sub_tgt))
                            else:
                                shutil.move(str(sub), str(sub_tgt)) if dest_path else sub.rename(sub_tgt)
                                with lock:
                                    src_folders.add(sub.parent)
                            local_subs += 1
                        except Exception:
                            pass
                    with lock:
                        sub_c[0] += local_subs

                except Exception as ex:
                    e["status"]    = "error"
                    e["error_msg"] = str(ex)
                    with lock:
                        errors_c[0] += 1

                # Signal that at least one file finished — debounced UI update
                self._rename_flush_pending = True

            with ThreadPoolExecutor(max_workers=parallelism) as executor:
                futures = {executor.submit(rename_one, e): e for e in ready}
                for _ in _as_completed(futures):
                    pass

            # ── Clean up empty source folders (move mode only) ────────────
            removed_folders = []
            if not is_copy and src_folders:
                dest_root_path = Path(dest_root) if dest_root else None
                protected = {f for f in src_folders if f.parent not in src_folders}
                for folder in sorted(src_folders, key=lambda p: len(p.parts), reverse=True):
                    if folder in protected:
                        continue
                    if dest_root_path and folder == dest_root_path:
                        continue
                    try_remove_empty_folder(folder)
                    if not folder.exists():
                        removed_folders.append(folder)

            # ── Save history ──────────────────────────────────────────────
            tab_type    = "TV" if isinstance(self, TVTab) else "Movie"
            new_history = []
            for e in ready:
                if e["status"] == "renamed":
                    new_history.append({
                        "type":      tab_type,
                        "original":  e.get("_orig_name", e["path"].name),
                        "renamed":   e["new_name"],
                        "dest":      str(e["path"].parent),
                        "mode":      "copy" if is_copy else "move",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })
            if new_history:
                cfg     = load_config()
                history = new_history + cfg.get("history", [])
                save_config({"history": history[:2000]})

            # ── Final UI update on main thread ────────────────────────────
            def _finish():
                self._rename_active = False          # stop the tick loop
                self._remove_renamed_and_refresh()   # final flush
                action_done = "copied" if is_copy else "renamed"
                status = f"Done — {renamed_c[0]} {action_done}"
                if sub_c[0]:        status += f", {sub_c[0]} subtitle(s)"
                if errors_c[0]:     status += f", {errors_c[0]} error(s)"
                if removed_folders: status += f", {len(removed_folders)} empty folder(s) deleted"
                self.app.set_status(status)
                self._enable_btn(self.lookup_btn, self._start_lookup)
                if any(e["status"] == "done" for e in self.file_entries):
                    self._maybe_enable_apply()
                if not self.file_entries:
                    self.drop_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
                    self.drop_overlay.lift()

            self.after(0, _finish)

        threading.Thread(target=_do_rename, daemon=True).start()

    def _remove_renamed_and_refresh(self):
        """Remove all 'renamed' entries from the list and refresh the table."""
        self.file_entries = [e for e in self.file_entries if e["status"] != "renamed"]
        self._refresh()
        self._summary()


    def _log(self, title, content):
        win = Toplevel(self); win.title(title)
        win.geometry("700x500"); win.configure(bg=BG_DARK); win.grab_set()
        Label(win, text=title, font=FONT_BOLD, fg=self.color,
              bg=BG_DARK).pack(anchor=W, padx=16, pady=(14,6))
        Frame(win, bg=BORDER, height=1).pack(fill=X, padx=16)
        tf = Frame(win, bg=BG_SURFACE); tf.pack(fill=BOTH, expand=True, padx=16, pady=12)
        sb = Scrollbar(tf); sb.pack(side=RIGHT, fill=Y)
        txt = Text(tf, bg=BG_SURFACE, fg=SUCCESS, font=FONT_MONO, bd=0,
                   padx=12, pady=10, yscrollcommand=sb.set,
                   wrap=WORD, insertbackground=self.color)
        txt.pack(fill=BOTH, expand=True); sb.config(command=txt.yview)
        txt.insert(END, content); txt.configure(state=DISABLED)
        Button(win, text="Close", command=win.destroy, bg=BG_SURFACE, fg=TEXT,
               font=FONT_SMALL, bd=0, padx=20, pady=8, cursor="hand2",
               activebackground=BG_HOVER, activeforeground=WHITE).pack(pady=(0,14))

    def _summary(self):
        total   = len(self.file_entries)
        ready   = sum(1 for e in self.file_entries if e["status"] in ("done","renamed"))
        skipped = sum(1 for e in self.file_entries if e["status"] in ("pending","skipped"))
        errors  = sum(1 for e in self.file_entries if e["status"]=="error")
        self.sum_total.config(text=str(total)); self.sum_ready.config(text=str(ready))
        self.sum_skip.config(text=str(skipped)); self.sum_error.config(text=str(errors))

    def _update_preview(self): pass  # override


# ── TV Shows Tab ──────────────────────────────────────────────────────────────
class TVTab(BaseTab):
    def __init__(self, parent, app):
        _tv_dest = load_config().get("tv_dest", "")
        self._dest_var_ref  = StringVar(value=_tv_dest)
        _saved_src = load_config().get("tv_source", TV_SOURCES[0])
        self._source_var    = StringVar(value=_saved_src if _saved_src in TV_SOURCES else TV_SOURCES[0])
        super().__init__(parent, app, self._dest_var_ref, ACCENT)
        self._dest_var_ref.trace_add("write",
            lambda *_: save_config({"tv_dest": self._dest_var_ref.get().strip()}))

    def _toolbar(self, p):
        super()._toolbar(p)
        # ── Source selector (right side of toolbar) ──────────────────────
        src_frame = Frame(p, bg=BG_PANEL)
        src_frame.pack(side=RIGHT, padx=(0, 14))

        Label(src_frame, text="LOOKUP VIA", font=("Segoe UI", 8, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(side=LEFT, padx=(0, 8))

        self._source_btns  = {}   # src -> pill_frame
        self._source_wgts  = {}   # src -> all_widgets list
        self._source_txts  = {}   # src -> text label
        for src in TV_SOURCES:
            is_sel = (src == self._source_var.get())
            pill, wgts, txt = self._make_source_pill(
                src_frame, src, is_sel, ACCENT,
                on_click=self._set_source,
                on_enter_bg=BG_HOVER, on_leave_bg=BG_SURFACE)
            self._source_btns[src] = pill
            self._source_wgts[src] = wgts
            self._source_txts[src] = txt

    def _set_source(self, src: str):
        """Switch the active lookup source and update pill styles."""
        self._source_var.set(src)
        save_config({"tv_source": src})
        for name in TV_SOURCES:
            sel = (name == src)
            bg  = ACCENT if sel else BG_SURFACE
            fg  = "#000" if sel else TEXT_DIM
            for w in self._source_wgts.get(name, []):
                try: w.configure(bg=bg)
                except Exception: pass
            if name in self._source_txts:
                self._source_txts[name].configure(fg=fg)
        self._update_lookup_icon()

    def _lookup_label(self): return "🔍  Lookup Episodes"
    def _parse(self, f):     return parse_tv_filename(f)

    def _subfolder(self, e):
        if not e.get("parsed"):
            return ""
        show     = safe_name(e["parsed"]["show_name"])
        year     = e["parsed"].get("show_year", "")
        season   = e["parsed"].get("season", 1)
        if self.opt_use_year_in_folder.get() and year:
            show_folder = f"{show} ({year})"
        else:
            show_folder = show
        season_folder = f"Season {season:02d}"
        return str(Path(show_folder) / season_folder)

    def _build_folder_options(self, parent):
        Frame(parent, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(8, 0))
        Label(parent, text="FOLDER STRUCTURE", font=("Segoe UI", 8, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(8, 4))
        fof = Frame(parent, bg=BG_SURFACE, bd=0, highlightthickness=1,
                    highlightbackground=BORDER)
        fof.pack(fill=X, padx=16)
        fo_row = Frame(fof, bg=BG_SURFACE)
        fo_row.pack(fill=X, padx=10, pady=3)
        fo_cb = Checkbutton(fo_row,
                            text="  Include year in show folder & filename",
                            variable=self.opt_use_year_in_folder,
                            font=FONT_SMALL, fg=TEXT, bg=BG_SURFACE,
                            selectcolor=BG_DARK, activebackground=BG_SURFACE,
                            activeforeground=TEXT, highlightthickness=0, bd=0,
                            cursor="hand2", command=self._update_preview)
        fo_cb.pack(side=LEFT)
        Tooltip(fo_cb,
                "Structures folders as:\n"
                "Show Name (YYYY) / Season 01 / Show Name (YYYY) - S01E01 - Title.mkv")

    def _build_work_batches(self) -> list:
        """
        1. Group entries by show name.
        2. Resolve all unique shows IN PARALLEL (one search per show, not per episode).
        3. Stamp the resolved show data onto each entry.
        4. Return the flat list of entries ready for parallel episode fetching.

        Picker dialogs (unmatched shows) are serialised one at a time on the
        main thread via self.after() + threading.Event.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed as _as_completed

        # ── Immediately fail un-parseable entries ─────────────────────────
        for e in self.file_entries:
            if e["status"] in ("error", "pending", "loading") and not e.get("parsed"):
                e["status"]    = "error"
                e["error_msg"] = "Could not parse filename"

        pending = [e for e in self.file_entries
                   if e["status"] in ("error", "pending", "loading")
                   and e.get("parsed")]

        if not pending:
            return []

        # ── Group by normalised show query ────────────────────────────────
        groups: dict = {}
        for e in pending:
            query = e["parsed"]["show_name"]
            if self.opt_strip_year.get():
                query = strip_year_from_query(query)
            key = query.lower().strip()
            groups.setdefault(key, {"query": query, "entries": []})
            groups[key]["entries"].append(e)

        src        = self._source_var.get()
        parallelism = int(self.opt_threads.get())

        # ── Resolve show searches in parallel ─────────────────────────────
        def resolve_show(key_grp):
            key, grp = key_grp
            query = grp["query"]
            try:
                if src == "TheTVDB":
                    results = tvdb_search_shows(query)
                else:
                    results = tvmaze_search_shows(query)

                if not results:
                    raise LookupNotFoundError(f"Show not found: '{query}'", query)

                top = results[0]
                if top["name"].lower().strip() != query.lower().strip() and len(results) > 1:
                    raise LookupNotFoundError(f"Multiple matches for '{query}'", query)

                return key, grp, {"id": top["id"], "name": top["name"],
                                  "premiered": top.get("premiered", "")}, None
            except LookupNotFoundError as ex:
                return key, grp, None, ex
            except Exception as ex:
                return key, grp, None, Exception(str(ex))

        needs_picker  = []   # (grp, query) where picker is required
        show_errors   = []   # (grp, error_msg) for hard failures

        with ThreadPoolExecutor(max_workers=parallelism) as pool:
            futures = {pool.submit(resolve_show, item): item
                       for item in groups.items()}
            for fut in _as_completed(futures):
                key, grp, show_data, exc = fut.result()
                if show_data:
                    for e in grp["entries"]:
                        e["_cached_show"] = show_data
                elif isinstance(exc, LookupNotFoundError):
                    needs_picker.append((grp, exc.query))
                else:
                    show_errors.append((grp, str(exc)))

        # ── Hard failures ─────────────────────────────────────────────────
        for grp, msg in show_errors:
            for e in grp["entries"]:
                e["status"]    = "error"
                e["error_msg"] = msg

        # ── Picker dialogs — serialised one at a time on the main thread ──
        for grp, query in needs_picker:
            ev     = threading.Event()
            chosen = [None]
            def _show_dlg(grp=grp, query=query, ev=ev, chosen=chosen):
                dlg       = self._show_picker(grp["entries"][0], query)
                chosen[0] = dlg.chosen if dlg else None
                ev.set()
            self.after(0, _show_dlg)
            ev.wait()
            if chosen[0]:
                show_data = {"id":        chosen[0]["id"],
                             "name":      chosen[0]["name"],
                             "premiered": chosen[0].get("premiered", "")}
                for e in grp["entries"]:
                    e["_cached_show"] = show_data
            else:
                for e in grp["entries"]:
                    e["status"]    = "error"
                    e["error_msg"] = "Skipped by user"

        # Return entries that have a resolved show and are ready for episode fetch
        return [e for e in self.file_entries
                if e.get("_cached_show") and e["status"] not in ("renamed", "error")]

    def _do_lookup(self, entry):
        """
        Episode fetch only — show search already done in _build_work_batches.
        Falls back to full lookup if cache is missing (e.g. manual re-run).
        """
        p   = entry["parsed"]
        src = self._source_var.get()

        cached = entry.get("_cached_show")
        if not cached:
            # Fallback: full search (used by single-entry re-run / manual search)
            query = p["show_name"]
            if self.opt_strip_year.get():
                query = strip_year_from_query(query)
            if src == "TheTVDB":
                results = tvdb_search_shows(query)
            else:
                results = tvmaze_search_shows(query)
            if not results:
                raise LookupNotFoundError(
                    f"Show not found: '{query}'", query)
            top = results[0]
            if top["name"].lower().strip() != query.lower().strip() and len(results) > 1:
                raise LookupNotFoundError(
                    f"Multiple matches for '{query}'", query)
            cached = {"id": top["id"], "name": top["name"],
                      "premiered": top.get("premiered", "")}

        self._finish_tv_lookup(entry, cached["id"], cached["name"],
                               show_year=cached.get("premiered", ""))

    def _finish_tv_lookup(self, entry, show_id, show_name: str, show_year: str = ""):
        p   = entry["parsed"]
        src = self._source_var.get()

        if src == "TheTVDB":
            ep = tvdb_get_episode(show_id, p["season"], p["episode"])
        else:
            ep = tvmaze_get_episode_by_id(show_id, p["season"], p["episode"])

        media = get_media_info(entry["path"])
        entry["media_info"] = media
        p["show_name"]  = show_name
        p["show_year"]  = show_year    # store for subfolder routing
        yr = show_year if self.opt_use_year_in_folder.get() else ""
        entry["new_name"] = build_tv_name(p, ep["name"], media,
            self.opt_resolution.get(), self.opt_video_codec.get(), self.opt_audio_codec.get(),
            show_year=yr)
        entry["status"] = "done"
        entry.pop("_cached_show", None)   # tidy up temp cache key
        subs = find_subtitle_siblings(entry["path"])
        entry["subtitles"] = [
            {"path": s, "new_name": build_subtitle_name(entry["new_name"], s)}
            for s in subs
        ]

    def _show_picker(self, entry, query: str):
        src = self._source_var.get()
        if src == "TheTVDB":
            search_fn = tvdb_search_shows
        else:
            search_fn = tvmaze_search_shows
        # Apply strip-year to picker's initial query too
        if self.opt_strip_year.get():
            query = strip_year_from_query(query)
        dlg = SearchPickerDialog(
            self.app, "TV Show Not Found — Pick a Match",
            entry["path"].name, query, search_fn, self.color)
        return dlg

    def _do_lookup_with_choice(self, entry, choice: dict):
        self._finish_tv_lookup(entry, choice["id"], choice["name"],
                               show_year=choice.get("premiered", ""))

    def _update_preview(self):
        show = "Show Name (2001)" if self.opt_use_year_in_folder.get() else "Show Name"
        parts = [f"{show} - S01E01 - Episode Title"]
        if self.opt_resolution.get():  parts.append("1080p")
        if self.opt_video_codec.get(): parts.append("HEVC")
        if self.opt_audio_codec.get(): parts.append("5.1")
        self.preview_label.config(text=" - ".join(parts)+".mkv")


# ── Movies Tab ────────────────────────────────────────────────────────────────
class MoviesTab(BaseTab):
    def __init__(self, parent, app):
        _movie_dest = load_config().get("movie_dest", "")
        self._dest_var_ref  = StringVar(value=_movie_dest)
        _saved_src = load_config().get("movie_source", MOVIE_SOURCES[0])
        self._source_var    = StringVar(value=_saved_src if _saved_src in MOVIE_SOURCES else MOVIE_SOURCES[0])
        super().__init__(parent, app, self._dest_var_ref, ACCENT_BLUE)
        self._dest_var_ref.trace_add("write",
            lambda *_: save_config({"movie_dest": self._dest_var_ref.get().strip()}))
        self._inject_api_bar()

    def _toolbar(self, p):
        super()._toolbar(p)
        # ── Source selector (right side of toolbar) ──────────────────────
        src_frame = Frame(p, bg=BG_PANEL)
        src_frame.pack(side=RIGHT, padx=(0, 14))

        Label(src_frame, text="LOOKUP VIA", font=("Segoe UI", 8, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(side=LEFT, padx=(0, 8))

        self._source_btns  = {}
        self._source_wgts  = {}
        self._source_txts  = {}
        for src in MOVIE_SOURCES:
            is_sel = (src == self._source_var.get())
            pill, wgts, txt = self._make_source_pill(
                src_frame, src, is_sel, ACCENT_BLUE,
                on_click=self._set_source,
                on_enter_bg=BG_HOVER, on_leave_bg=BG_SURFACE)
            self._source_btns[src] = pill
            self._source_wgts[src] = wgts
            self._source_txts[src] = txt

    def _set_source(self, src: str):
        """Switch the active lookup source and update pill styles."""
        self._source_var.set(src)
        save_config({"movie_source": src})
        for name in MOVIE_SOURCES:
            sel = (name == src)
            bg  = ACCENT_BLUE if sel else BG_SURFACE
            fg  = "#000"      if sel else TEXT_DIM
            for w in self._source_wgts.get(name, []):
                try: w.configure(bg=bg)
                except Exception: pass
            if name in self._source_txts:
                self._source_txts[name].configure(fg=fg)
        self._update_lookup_icon()
        # Show/hide the OMDb key bar based on selection
        if hasattr(self, "_omdb_bar"):
            if src == "OMDb":
                self._omdb_bar.pack(fill=X, before=self.winfo_children()[1])
            else:
                self._omdb_bar.pack_forget()

    def _inject_api_bar(self):
        """Add OMDb API key bar; hidden when TheTVDB is selected."""
        bar = Frame(self, bg=BG_PANEL)
        # Place it before the second child (toolbar is first, this comes after header)
        bar.pack(fill=X, before=self.winfo_children()[0])
        self._omdb_bar = bar

        Frame(bar, bg=BORDER, height=1).pack(fill=X)
        row = Frame(bar, bg=BG_PANEL)
        row.pack(fill=X, padx=16, pady=7)

        Label(row, text="OMDB API KEY", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(side=LEFT, padx=(0, 10))

        _saved_key = load_config().get("omdb_api_key", OMDB_API_KEY)
        self.api_key_var = StringVar(value=_saved_key)
        ef = Frame(row, bg=BG_SURFACE, bd=0, highlightthickness=1,
                   highlightbackground=BORDER)
        ef.pack(side=LEFT, fill=X, expand=True)
        self._key_entry = Entry(ef, textvariable=self.api_key_var,
                                font=FONT_MONO_SM, bg=BG_SURFACE, fg=TEXT,
                                bd=0, show="•", insertbackground=ACCENT_BLUE,
                                highlightthickness=0)
        self._key_entry.pack(side=LEFT, fill=X, expand=True, padx=8, pady=5)

        eye = Label(ef, text="👁", font=FONT_SMALL, bg=BG_SURFACE,
                    fg=MUTED, cursor="hand2", padx=6)
        eye.pack(side=RIGHT)
        eye.bind("<ButtonPress-1>",   lambda e: self._key_entry.configure(show=""))
        eye.bind("<ButtonRelease-1>", lambda e: self._key_entry.configure(show="•"))

        self.api_key_var.trace_add("write",
            lambda *_: save_config({"omdb_api_key": self.api_key_var.get().strip()}))

        link = Label(row, text="  Get a free key at omdbapi.com/apikey.aspx",
                     font=("Segoe UI", 8), fg=BLUE, bg=BG_PANEL, cursor="hand2")
        link.pack(side=LEFT)
        link.bind("<Button-1>", lambda e: __import__("webbrowser").open(
            "http://www.omdbapi.com/apikey.aspx"))
        link.bind("<Enter>", lambda e: link.configure(fg=WHITE,
            font=("Segoe UI", 8, "underline")))
        link.bind("<Leave>", lambda e: link.configure(fg=BLUE,
            font=("Segoe UI", 8)))

        # Hide immediately if TheTVDB is the saved source
        if self._source_var.get() != "OMDb":
            bar.pack_forget()

    def _lookup_label(self): return "🔍  Lookup Movies"
    def _parse(self, f):     return parse_movie_filename(f)

    def _subfolder(self, e):
        if self.opt_create_movie_folder.get():
            return e.get("movie_folder", "")
        return ""

    def _build_folder_options(self, parent):
        Frame(parent, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(8, 0))
        Label(parent, text="FOLDER STRUCTURE", font=("Segoe UI", 8, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(8, 4))
        fof = Frame(parent, bg=BG_SURFACE, bd=0, highlightthickness=1,
                    highlightbackground=BORDER)
        fof.pack(fill=X, padx=16)
        fo_row = Frame(fof, bg=BG_SURFACE)
        fo_row.pack(fill=X, padx=10, pady=3)
        fo_cb = Checkbutton(fo_row,
                            text="  Create per-movie subfolder",
                            variable=self.opt_create_movie_folder,
                            font=FONT_SMALL, fg=TEXT, bg=BG_SURFACE,
                            selectcolor=BG_DARK, activebackground=BG_SURFACE,
                            activeforeground=TEXT, highlightthickness=0, bd=0,
                            cursor="hand2", command=self._update_preview)
        fo_cb.pack(side=LEFT)
        Tooltip(fo_cb,
                "Creates a subfolder named 'Movie Title (YYYY)' inside\n"
                "your Movies destination for each film.")

    def _build_work_batches(self) -> list:
        """
        Group movies by normalised title, resolve each unique title once
        in parallel (pre-populating the session cache), then return the
        flat list for the episode-fetch pool.  Duplicate titles (e.g.
        multiple files for the same movie) only hit the API once.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed as _as_completed

        if not hasattr(self, "_movie_cache"):
            self._movie_cache = {}

        # Mark un-parseable entries immediately
        for e in self.file_entries:
            if e["status"] in ("error", "pending", "loading") and not e.get("parsed"):
                e["status"]    = "error"
                e["error_msg"] = "Could not parse filename"

        pending = [e for e in self.file_entries
                   if e["status"] in ("error", "pending", "loading")
                   and e.get("parsed")]
        if not pending:
            return []

        src         = self._source_var.get()
        parallelism = int(self.opt_threads.get())

        # Group by cache key so identical titles share one lookup
        groups: dict = {}
        for e in pending:
            p     = e["parsed"]
            query = p["raw_title"]
            if self.opt_strip_year.get():
                query = strip_year_from_query(query)
            search_year = p.get("year") if not self.opt_strip_year.get() else None
            key = self._movie_cache_key(query, search_year)
            groups.setdefault(key, {"query": query, "year": search_year, "entries": []})
            groups[key]["entries"].append(e)

        # Skip groups already in cache
        uncached = {k: v for k, v in groups.items() if k not in self._movie_cache}

        def resolve_movie(item):
            cache_key, grp = item
            query       = grp["query"]
            search_year = grp["year"]
            try:
                if src == "TheTVDB":
                    results = tvdb_search_movies(query, search_year)
                    if not results:
                        raise LookupNotFoundError(f"Movie not found: '{query}'", query)
                    top = results[0]
                    if search_year and top["year"] != str(search_year) and len(results) > 1:
                        raise LookupNotFoundError(f"Multiple matches for '{query}'", query)
                    full = top if (top.get("title") and top.get("year","????") != "????") \
                               else tvdb_get_movie(top["id"])
                elif src == "TMDb":
                    results = tmdb_search_movies(query, search_year)
                    if not results:
                        raise LookupNotFoundError(f"Movie not found: '{query}'", query)
                    top = results[0]
                    if search_year and top["year"] != str(search_year) and len(results) > 1:
                        raise LookupNotFoundError(f"Multiple matches for '{query}'", query)
                    q_norm    = query.lower().strip()
                    t_norm    = top["title"].lower().strip()
                    confident = (q_norm == t_norm or q_norm in t_norm or t_norm in q_norm)
                    full = top if (confident and top.get("title") and top.get("year","????") != "????") \
                               else tmdb_get_movie(top["id"])
                else:
                    key = self.api_key_var.get().strip()
                    if not key:
                        raise ValueError("Enter your OMDb API key at the top of the Movies tab")
                    results = omdb_search_movies(query, search_year, key)
                    if not results:
                        raise LookupNotFoundError(f"Movie not found: '{query}'", query)
                    top = results[0]
                    if search_year and top["year"] != str(search_year) and len(results) > 1:
                        raise LookupNotFoundError(f"Multiple matches for '{query}'", query)
                    q_norm    = query.lower().strip()
                    t_norm    = top["title"].lower().strip()
                    confident = (q_norm == t_norm or q_norm in t_norm or t_norm in q_norm)
                    full = top if (confident and top.get("title") and top.get("year","????") != "????") \
                               else omdb_get_movie(top["id"], key)
                return cache_key, grp, full, None
            except LookupNotFoundError as ex:
                return cache_key, grp, None, ex
            except Exception as ex:
                return cache_key, grp, None, Exception(str(ex))

        needs_picker = []
        hard_errors  = []

        if uncached:
            with ThreadPoolExecutor(max_workers=parallelism) as pool:
                futures = {pool.submit(resolve_movie, item): item
                           for item in uncached.items()}
                for fut in _as_completed(futures):
                    cache_key, grp, full, exc = fut.result()
                    if full:
                        self._movie_cache[cache_key] = full
                    elif isinstance(exc, LookupNotFoundError):
                        needs_picker.append((grp, exc.query))
                    else:
                        hard_errors.append((grp, str(exc)))

        # Hard failures
        for grp, msg in hard_errors:
            for e in grp["entries"]:
                e["status"]    = "error"
                e["error_msg"] = msg

        # Picker dialogs — one at a time on the main thread
        for grp, query in needs_picker:
            ev     = threading.Event()
            chosen = [None]
            def _show_dlg(grp=grp, query=query, ev=ev, chosen=chosen):
                dlg       = self._show_picker(grp["entries"][0], query)
                chosen[0] = dlg.chosen if dlg else None
                ev.set()
            self.after(0, _show_dlg)
            ev.wait()
            if chosen[0]:
                # Fetch full detail for picker choice
                try:
                    if src == "TheTVDB":
                        full = tvdb_get_movie(chosen[0]["id"])
                    elif src == "TMDb":
                        full = tmdb_get_movie(chosen[0]["id"])
                    else:
                        api_key = self.api_key_var.get().strip()
                        full = omdb_get_movie(chosen[0]["id"], api_key) \
                               if chosen[0].get("id") else chosen[0]
                    cache_key = self._movie_cache_key(grp["query"], grp["year"])
                    self._movie_cache[cache_key] = full
                except Exception as ex:
                    for e in grp["entries"]:
                        e["status"]    = "error"
                        e["error_msg"] = str(ex)
                    continue
            else:
                for e in grp["entries"]:
                    e["status"]    = "error"
                    e["error_msg"] = "Skipped by user"

        # Return entries whose title is now cached and ready for _do_lookup
        return [e for e in self.file_entries
                if e["status"] not in ("renamed", "error")
                and e.get("parsed")
                and self._movie_cache_key(
                    strip_year_from_query(e["parsed"]["raw_title"])
                    if self.opt_strip_year.get() else e["parsed"]["raw_title"],
                    None if self.opt_strip_year.get() else e["parsed"].get("year")
                ) in self._movie_cache]

    def _movie_cache_key(self, query: str, year) -> str:
        return f"{query.lower().strip()}|{year or ''}"

    def _do_lookup(self, entry):
        src = self._source_var.get()
        p   = entry["parsed"]

        query = p["raw_title"]
        if self.opt_strip_year.get():
            query = strip_year_from_query(query)
        search_year = p.get("year") if not self.opt_strip_year.get() else None

        # ── Check session cache — skip repeat lookups for same title ─────
        if not hasattr(self, "_movie_cache"):
            self._movie_cache = {}
        cache_key = self._movie_cache_key(query, search_year)
        if cache_key in self._movie_cache:
            self._finish_movie_lookup(entry, self._movie_cache[cache_key])
            return

        if src == "TheTVDB":
            results = tvdb_search_movies(query, search_year)
            if not results:
                raise LookupNotFoundError(
                    f"Movie not found: '{query}'", query)
            top = results[0]
            if search_year and top["year"] != str(search_year) and len(results) > 1:
                raise LookupNotFoundError(
                    f"Multiple matches for '{query}'", query)
            if top.get("title") and top.get("year","????") != "????":
                full = top
            else:
                full = tvdb_get_movie(top["id"])
        elif src == "TMDb":
            results = tmdb_search_movies(query, search_year)
            if not results:
                raise LookupNotFoundError(
                    f"Movie not found: '{query}'", query)
            top = results[0]
            if search_year and top["year"] != str(search_year) and len(results) > 1:
                raise LookupNotFoundError(
                    f"Multiple matches for '{query}'", query)
            q_norm    = query.lower().strip()
            t_norm    = top["title"].lower().strip()
            confident = (q_norm == t_norm or q_norm in t_norm or t_norm in q_norm)
            if confident and top.get("title") and top.get("year","????") != "????":
                full = top
            else:
                full = tmdb_get_movie(top["id"])
        else:
            key = self.api_key_var.get().strip()
            if not key:
                raise ValueError("Enter your OMDb API key at the top of the Movies tab")
            results = omdb_search_movies(query, search_year, key)
            if not results:
                raise LookupNotFoundError(
                    f"Movie not found: '{query}'", query)
            top = results[0]
            if search_year and top["year"] != str(search_year) and len(results) > 1:
                raise LookupNotFoundError(
                    f"Multiple matches for '{query}'", query)
            q_norm    = query.lower().strip()
            t_norm    = top["title"].lower().strip()
            confident = (q_norm == t_norm or q_norm in t_norm or t_norm in q_norm)
            if confident and top.get("title") and top.get("year","????") != "????":
                full = top
            else:
                full = omdb_get_movie(top["id"], key)

        self._movie_cache[cache_key] = full
        self._finish_movie_lookup(entry, full)

    def _finish_movie_lookup(self, entry, result: dict):
        p     = entry["parsed"]
        title = result["title"]
        year  = result.get("year", "????")[:4]
        media = get_media_info(entry["path"])
        entry["media_info"]    = media
        entry["movie_folder"]  = safe_name(f"{title} ({year})")
        entry["new_name"]      = build_movie_name(title, year, p["ext"], media,
            self.opt_resolution.get(), self.opt_video_codec.get(), self.opt_audio_codec.get())
        entry["status"] = "done"
        subs = find_subtitle_siblings(entry["path"])
        entry["subtitles"] = [
            {"path": s, "new_name": build_subtitle_name(entry["new_name"], s)}
            for s in subs
        ]

    def _show_picker(self, entry, query: str):
        src = self._source_var.get()
        if self.opt_strip_year.get():
            query = strip_year_from_query(query)
        if src == "TheTVDB":
            search_fn = lambda q: tvdb_search_movies(q, None)
        elif src == "TMDb":
            search_fn = lambda q: tmdb_search_movies(q, None)
        else:
            key = self.api_key_var.get().strip()
            search_fn = lambda q, k=key: omdb_search_movies(q, None, k)
        dlg = SearchPickerDialog(
            self.app, "Movie Not Found — Pick a Match",
            entry["path"].name, query, search_fn, self.color)
        return dlg

    def _do_lookup_with_choice(self, entry, choice: dict):
        src = self._source_var.get()
        if src == "TheTVDB":
            full = tvdb_get_movie(choice["id"])
        elif src == "TMDb":
            full = tmdb_get_movie(choice["id"])
        else:
            key  = self.api_key_var.get().strip()
            full = omdb_get_movie(choice["id"], key) if choice.get("id") else choice
        self._finish_movie_lookup(entry, full)

    def _update_preview(self):
        parts = ["Movie Title (2024)"]
        if self.opt_resolution.get():  parts.append("1080p")
        if self.opt_video_codec.get(): parts.append("HEVC")
        if self.opt_audio_codec.get(): parts.append("5.1")
        fname = " - ".join(parts) + ".mkv"
        if self.opt_create_movie_folder.get():
            self.preview_label.config(text=f"Movie Title (2024)/\n  {fname}")
        else:
            self.preview_label.config(text=fname)


# ── History Dialog ───────────────────────────────────────────────────────────
class HistoryDialog(Toplevel):
    """Shows all renamed TV and Movie files from the saved history."""

    ROW_H = 34   # pixel height of each row

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Rename History")
        self.geometry("980x620")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.grab_set()
        self._filter_var  = StringVar()
        self._type_var    = StringVar(value="All")
        self._all         = load_config().get("history", [])
        self._filtered    = self._all   # current filtered view
        self._filter_job  = None        # debounce timer id
        self._build()
        self._render(self._all)

    # ── Build chrome (header, filter bar, column headers, status bar) ──────
    def _build(self):
        # Header
        hdr = Frame(self, bg=BG_PANEL, height=52)
        hdr.pack(fill=X); hdr.pack_propagate(False)
        Frame(hdr, bg=ACCENT, width=4).pack(side=LEFT, fill=Y)
        Label(hdr, text="Rename History", font=("Segoe UI", 13, "bold"),
              fg=ACCENT, bg=BG_PANEL).pack(side=LEFT, padx=14)
        self._total_lbl = Label(hdr, text=f"  {len(self._all)} total entries",
                                font=FONT_SMALL, fg=MUTED, bg=BG_PANEL)
        self._total_lbl.pack(side=LEFT, pady=(6, 0))

        clr = Label(hdr, text="🗑 Clear History", font=FONT_SMALL,
                    fg=ERROR, bg=BG_PANEL, cursor="hand2", padx=14)
        clr.pack(side=RIGHT)
        clr.bind("<Button-1>", lambda e: self._clear_history())

        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Filter bar
        fb = Frame(self, bg=BG_PANEL, height=40)
        fb.pack(fill=X); fb.pack_propagate(False)

        sf = Frame(fb, bg=BG_SURFACE, bd=0, highlightthickness=1,
                   highlightbackground=BORDER)
        sf.pack(side=LEFT, padx=12, pady=6, fill=X, expand=True)
        Label(sf, text="🔍", font=FONT_SMALL, fg=MUTED,
              bg=BG_SURFACE, padx=6).pack(side=LEFT)
        Entry(sf, textvariable=self._filter_var, font=FONT_MONO_SM,
              bg=BG_SURFACE, fg=TEXT, bd=0, insertbackground=ACCENT,
              highlightthickness=0).pack(side=LEFT, fill=X, expand=True,
                                         padx=(0, 6), pady=4)
        self._filter_var.trace_add("write", lambda *_: self._debounce_filter())

        for label in ("All", "TV", "Movie"):
            btn = Label(fb, text=label, font=FONT_SMALL,
                        fg=ACCENT if label == "All" else MUTED,
                        bg=BG_PANEL, cursor="hand2", padx=10)
            btn.pack(side=LEFT, pady=8)
            btn.bind("<Button-1>", lambda e, l=label: self._set_type(l))
        self._type_btns = {c.cget("text"): c for c in fb.winfo_children()
                           if isinstance(c, Label)}

        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Column headers
        ch = Frame(self, bg=BG_PANEL, height=30)
        ch.pack(fill=X); ch.pack_propagate(False)
        for text, x, w in [("TYPE", 8, 50), ("ORIGINAL FILENAME", 66, 380),
                            ("RENAMED TO", 454, 380), ("DATE", 842, 100)]:
            Label(ch, text=text, font=FONT_SMALL, fg=MUTED,
                  bg=BG_PANEL, anchor=W).place(x=x, y=7, width=w)
        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Virtual canvas — rows are drawn as canvas text, not widgets
        lf = Frame(self, bg=BG_DARK)
        lf.pack(fill=BOTH, expand=True)

        self._sb = Scrollbar(lf, orient=VERTICAL, bg=BG_SURFACE,
                             troughcolor=BG_DARK)
        self._sb.pack(side=RIGHT, fill=Y)

        self._canvas = Canvas(lf, bg=BG_DARK, highlightthickness=0, bd=0,
                              yscrollcommand=self._on_yscroll)
        self._canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self._sb.config(command=self._on_scrollbar)

        self._canvas.bind("<Configure>",   lambda e: self._on_canvas_resize())
        self._canvas.bind("<MouseWheel>",
                          lambda e: self._scroll_wheel(e.delta))

        # Status bar
        Frame(self, bg=BORDER, height=1).pack(fill=X)
        bot = Frame(self, bg=BG_PANEL, height=30)
        bot.pack(fill=X, side=BOTTOM); bot.pack_propagate(False)
        self._count_lbl = Label(bot, text="", font=FONT_SMALL,
                                fg=TEXT_DIM, bg=BG_PANEL, anchor=W, padx=12)
        self._count_lbl.pack(side=LEFT, fill=Y)
        close = Label(bot, text="Close", font=FONT_SMALL, fg=MUTED,
                      bg=BG_PANEL, cursor="hand2", padx=16)
        close.pack(side=RIGHT)
        close.bind("<Button-1>", lambda e: self.destroy())

        self._top_row   = 0     # index of first visible row
        self._drawn_ids = []    # canvas item ids currently on screen

    # ── Virtual rendering ─────────────────────────────────────────────────
    def _render(self, entries: list):
        """Switch to a new data set and repaint from the top."""
        self._filtered = entries
        self._top_row  = 0
        self._count_lbl.config(
            text=f"  {len(entries)} entr{'y' if len(entries)==1 else 'ies'}")
        self._update_scrollbar()
        self._paint()

    def _update_scrollbar(self):
        n   = len(self._filtered)
        if n == 0:
            self._sb.set(0.0, 1.0)
            return
        ch  = max(1, self._canvas.winfo_height())
        vis = ch / (n * self.ROW_H)
        top = self._top_row / n
        self._sb.set(top, min(1.0, top + vis))

    def _paint(self):
        """Draw only the rows visible in the current viewport."""
        c = self._canvas
        c.delete("all")
        self._drawn_ids = []

        entries = self._filtered
        if not entries:
            c.create_text(c.winfo_width() // 2, 60,
                          text="No history entries found",
                          fill=MUTED, font=FONT_SMALL, anchor=CENTER)
            return

        ch    = max(1, c.winfo_height())
        cw    = max(1, c.winfo_width())
        n     = len(entries)
        first = self._top_row
        last  = min(n, first + ch // self.ROW_H + 2)

        for i in range(first, last):
            h   = entries[i]
            y0  = (i - first) * self.ROW_H
            y1  = y0 + self.ROW_H
            bg  = BG_ROW if i % 2 == 0 else BG_ROW_ALT

            # Row background
            c.create_rectangle(0, y0, cw, y1, fill=bg, outline="", tags="row")

            kind  = h.get("type", "?")
            color = ACCENT if kind == "TV" else ACCENT_BLUE
            cy    = y0 + self.ROW_H // 2

            c.create_text(8,   cy, text=kind,               fill=color,   font=("Segoe UI", 8, "bold"), anchor=W)
            c.create_text(66,  cy, text=h.get("original",""), fill=TEXT_DIM, font=FONT_MONO_SM,          anchor=W)
            c.create_text(454, cy, text=h.get("renamed",""),  fill=SUCCESS,  font=FONT_MONO_SM,          anchor=W)
            c.create_text(842, cy, text=h.get("timestamp",""),fill=MUTED,    font=("Segoe UI", 8),       anchor=W)

            # Divider
            c.create_line(0, y1, cw, y1, fill=BORDER, width=1)

    def _on_canvas_resize(self):
        self._update_scrollbar()
        self._paint()

    def _on_yscroll(self, first, last):
        self._sb.set(first, last)

    def _on_scrollbar(self, *args):
        """Handle scrollbar drag and arrow clicks."""
        n = len(self._filtered)
        if n == 0:
            return
        if args[0] == "moveto":
            frac = float(args[1])
            self._top_row = max(0, min(n - 1, int(frac * n)))
        elif args[0] == "scroll":
            amount = int(args[1])
            unit   = args[2]
            if unit == "units":
                self._top_row = max(0, min(n - 1, self._top_row + amount))
            elif unit == "pages":
                ch   = max(1, self._canvas.winfo_height())
                page = max(1, ch // self.ROW_H)
                self._top_row = max(0, min(n - 1, self._top_row + amount * page))
        self._update_scrollbar()
        self._paint()

    def _scroll_wheel(self, delta):
        n     = len(self._filtered)
        lines = -3 if delta > 0 else 3
        self._top_row = max(0, min(max(0, n - 1), self._top_row + lines))
        self._update_scrollbar()
        self._paint()

    # ── Filter / type ─────────────────────────────────────────────────────
    def _debounce_filter(self):
        if self._filter_job:
            self.after_cancel(self._filter_job)
        self._filter_job = self.after(180, self._apply_filter)

    def _set_type(self, label: str):
        self._type_var.set(label)
        for txt, btn in self._type_btns.items():
            btn.configure(fg=ACCENT if txt == label else MUTED)
        self._apply_filter()

    def _apply_filter(self):
        q    = self._filter_var.get().lower()
        kind = self._type_var.get()
        filtered = [h for h in self._all
                    if (kind == "All" or h.get("type", "") == kind)
                    and (not q
                         or q in h.get("original", "").lower()
                         or q in h.get("renamed",  "").lower())]
        self._render(filtered)

    def _clear_history(self):
        if messagebox.askyesno("Clear History",
                "Delete all rename history?\nThis cannot be undone.", parent=self):
            save_config({"history": []})
            self._all      = []
            self._filtered = []
            self._total_lbl.config(text="  0 total entries")
            self._render([])





# ── Embedded README content ───────────────────────────────────────────────────
README_CONTENT = """# 🎬 PlexBot v1.08
Automatic Media File Renamer for Plex
Powered by DAT — Dans Automation Tools

Stop renaming files by hand. PlexBot does it in seconds.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WHAT IS PLEXBOT?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PlexBot is a desktop application that takes your messy downloaded video
filenames and automatically renames them into clean, Plex-compatible
formats. It looks up episode titles and movie names from multiple online
databases, optionally tags files with resolution and codec info, organises
them into the correct folder structure, and handles subtitle files
alongside the video — all running in parallel so large batches complete
fast. Tested with 4,000+ files renamed in a single session.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HOW IT WORKS — TV SHOWS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PlexBot reads the filename and extracts the show name, season, and episode
number from patterns like:

    Happys.Place.S02E13.1080p.HEVC.x265-MeGusta.mkv
    Band.of.Brothers.S01E01.720p.mkv

It queries TVmaze or TheTVDB for the episode title and renames the file:

    Happy's Place (2024) - S02E13 - A New Chapter - 1080p - HEVC - 5.1.mkv

Files are organised into a structured folder hierarchy:

    TV Shows\
      └── Band of Brothers (2001)\
            └── Season 01\
                  ├── Band of Brothers (2001) - S01E01 - Currahee.mkv
                  └── Band of Brothers (2001) - S01E01 - Currahee.en.srt

Smart grouping: episodes of the same show share a single show-search
call. 20 episodes of one show = 1 search + 20 parallel episode fetches.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HOW IT WORKS — MOVIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PlexBot extracts the movie title and year from filenames like:

    Inception.2010.1080p.BluRay.x264.mkv
    The.Matrix.1999.REMASTERED.mkv

It queries OMDb, TheTVDB, or TMDb, then creates a per-movie subfolder:

    Movies\
      └── Inception (2010)\
            ├── Inception (2010) - 1080p - H.264 - 5.1.mkv
            └── Inception (2010).en.srt

All unique titles are searched in parallel. Duplicate titles only hit
the API once. Confident matches skip the redundant detail API call.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 LOOKUP VIA — SOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Both tabs have a LOOKUP VIA selector with brand icons in the toolbar.
The selected source icon also appears on the Lookup button itself.

  TV Shows:  TVmaze (default)  ·  TheTVDB
  Movies:    OMDb (default)    ·  TheTVDB  ·  TMDb

TVmaze   — Free, no key required, works immediately.
TheTVDB  — Built-in key, no setup required.
OMDb     — Free key required (1,000 lookups/day).
TMDb     — Built-in token, no setup required. Excellent coverage.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 API KEYS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TVmaze       — No key needed. Works straight away.
TheTVDB      — Built-in key. No setup needed.
TMDb         — Built-in token. No setup needed.
OMDb Movies  — Free key required (1,000 lookups/day).

To get an OMDb key:
  1. Go to omdbapi.com/apikey.aspx
  2. Select the Free tier and enter your email
  3. Your key arrives by email almost immediately
  4. Open the Movies tab and paste the key into OMDB API KEY

The key is saved automatically — you only need to enter it once.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 AUTO-UPDATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PlexBot checks GitHub for updates automatically on startup.

  · Check runs in the background — no delay to launch
  · If a newer version is found, a green banner appears below
    the header: "PlexBot v1.0x is available — click to update"
  · Click the banner to open the Update dialog
  · Click ✕ on the banner to dismiss it

Running from source (.py):
  PlexBot downloads the new plexbot.py, verifies it, replaces
  the current file, then offers to restart automatically.

Running as PlexBot.exe:
  The EXE cannot update itself. Clicking the banner opens the
  GitHub Releases page so you can download the new EXE.

Updates are hosted at:
  github.com/dmurr5050/Plexbot


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SETTINGS PANEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click the ▶ SETTINGS header in the right-hand panel to expand settings.

FILE MODE
  ✂  Move               — File is moved and renamed. Original is removed.
  ⎘  Copy & Keep        — Renamed copy made at destination. Original kept.

FOLDER STRUCTURE (TV Shows)
  Include year in show folder & filename
  → Show Name (YYYY) / Season 01 / Show Name (YYYY) - S01E01 - Title.mkv
  On by default.

FOLDER STRUCTURE (Movies)
  Create per-movie subfolder
  → Movie Title (YYYY) / Movie Title (YYYY).mkv
  On by default.

INCLUDE IN FILENAME
  Each tag can be toggled independently:
  · Video Resolution  (e.g. 1080p, 2160p)
  · Video Codec       (e.g. HEVC, H.264)
  · Audio Channels    (e.g. 5.1, 7.1, 2.0)

SEARCH OPTIONS
  Strip year from search query
  → Removes years like (2005) from search terms to avoid narrow results.
  → On by default.

  Concurrent lookups
  → 5 / 10 / 15 / 20 / 25 / 30 threads. Default is 5.
  → Higher values speed up large batches significantly.
  → The same thread count is used for both lookups and file renaming.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PERFORMANCE — LARGE BATCHES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  · TV: one show-search per unique show, not per episode. All show
    searches and episode fetches run in parallel.

  · Movies: all unique titles searched in parallel. Duplicate titles
    only searched once per session. Confident matches skip the
    detail fetch, halving API calls.

  · Lookup UI debounced at 100 ms — stays responsive during 100+
    concurrent threads.

  · Rename operations parallel with debounced UI at 150 ms.

  · History dialog virtual rendering — instant open with 4,000+ entries.

  · Apply & Rename button stays disabled until full batch completes.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SMART LOOKUP PICKER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When PlexBot cannot confidently match a filename, a search dialog
opens centred over the app window:

  · Pre-filled search box, ready to edit
  · Scrollable list of matches with title, year, description
  · Click any result to select it, then confirm
  · Batch continues after you confirm or skip


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 RIGHT-CLICK MENU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Right-click any file row during or after a lookup:

  🔍 Manual Search…     Open picker pre-filled with detected name
  🔄 Re-run Auto Lookup  Retry the automatic lookup for this file
  ✕  Remove from list   Remove this entry without processing it


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 RETRY ERRORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After a lookup completes, failed files show an ERROR badge.
The lookup button changes to 🔄 Retry Errors (N). Click it to retry
only the errored files — successfully looked-up files stay untouched.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FOLDER CLEANUP  (🧹 button in header)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Removes junk sidecar files recursively from any folder.

Files removed:  .txt  .idx  .nfo  .jpg  .htm  .png  .url  .bif
Also removes:   Empty subfolders · System Volume Information

How to use:
  1. Folder defaults to last folder you loaded files from
  2. Click 🔍 Scan to preview everything that will be deleted
  3. Click 🗑 Delete All Listed Files to remove


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 RENAME HISTORY  (📋 button in header)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every rename is logged. Opens instantly with 4,000+ entries.

  · Original and new filename side by side
  · Filter by All, TV, or Movie
  · Search by any part of the filename
  · Clear the full history when no longer needed


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SUPPORTED FILE TYPES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Video:     .mkv .mp4 .avi .mov .m4v .wmv .ts .m2ts .mpg .mpeg
Subtitles: .srt .sub .ass .ssa .vtt .idx .sup .pgs


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Settings saved automatically to:
  Documents\\PlexBot\\plexbot_config.json

Stores: OMDb key, destinations, all settings, full rename history.
Created automatically on first run.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GETTING STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run from source:
  pip install requests tkinterdnd2
  python plexbot.py

Build EXE:
  Put plexbot.py + plexbot.ico + Build_exe.bat in same folder
  Double-click Build_exe.bat — PlexBot.exe appears in ~2 minutes

FFmpeg (optional):
  winget install ffmpeg
  Enables resolution and codec tags in filenames.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 CONTACT & SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click the ✉ Contact button in the app header to copy the email,
or write to DMurr5050@gmail.com directly.

If PlexBot saves you time, click 💛 Donate via PayPal in the header.

PlexBot is not affiliated with Plex Inc., TVmaze, OMDb, TheTVDB,
or TMDb in any way.
"""

# ── Help / README Dialog ──────────────────────────────────────────────────────
class ReadmeDialog(Toplevel):
    """Scrollable in-app help viewer displaying README_CONTENT."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("PlexBot — Help & Documentation")
        self.geometry("780x640")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.grab_set()
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────────────
        hdr = Frame(self, bg=BG_PANEL, height=52)
        hdr.pack(fill=X); hdr.pack_propagate(False)
        Frame(hdr, bg=ACCENT_BLUE, width=4).pack(side=LEFT, fill=Y)
        Label(hdr, text="❓  Help & Documentation",
              font=("Segoe UI", 13, "bold"),
              fg=ACCENT_BLUE, bg=BG_PANEL).pack(side=LEFT, padx=14)
        Label(hdr, text=f"PlexBot v{VERSION}",
              font=FONT_SMALL, fg=MUTED, bg=BG_PANEL).pack(side=LEFT)

        # Close button
        close_lbl = Label(hdr, text="✕  Close", font=FONT_SMALL,
                          fg=MUTED, bg=BG_PANEL, cursor="hand2", padx=16)
        close_lbl.pack(side=RIGHT)
        close_lbl.bind("<Button-1>", lambda e: self.destroy())
        close_lbl.bind("<Enter>",    lambda e: close_lbl.configure(fg=WHITE))
        close_lbl.bind("<Leave>",    lambda e: close_lbl.configure(fg=MUTED))

        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # ── Scrollable text area ──────────────────────────────────────────
        tf = Frame(self, bg=BG_SURFACE)
        tf.pack(fill=BOTH, expand=True, padx=0, pady=0)

        sb = Scrollbar(tf, orient=VERTICAL, bg=BG_SURFACE, troughcolor=BG_DARK)
        sb.pack(side=RIGHT, fill=Y)

        txt = Text(tf, bg=BG_SURFACE, fg=TEXT, font=("Consolas", 9),
                   bd=0, padx=20, pady=16,
                   yscrollcommand=sb.set, wrap=WORD,
                   insertbackground=ACCENT_BLUE,
                   selectbackground=ACCENT_BLUE, selectforeground="#000",
                   highlightthickness=0, cursor="arrow")
        txt.pack(fill=BOTH, expand=True)
        sb.config(command=txt.yview)

        # ── Insert content with styled sections ───────────────────────────
        txt.tag_configure("title",   font=("Segoe UI", 14, "bold"), foreground=ACCENT,
                          spacing3=6)
        txt.tag_configure("section", font=("Segoe UI", 9,  "bold"), foreground=ACCENT_BLUE,
                          spacing1=10, spacing3=4)
        txt.tag_configure("code",    font=("Consolas", 8),          foreground=SUCCESS,
                          background="#0d1a0d", lmargin1=24, lmargin2=24, spacing1=1, spacing3=1)
        txt.tag_configure("body",    font=("Segoe UI", 9),          foreground=TEXT,
                          lmargin1=8, lmargin2=8, spacing1=2)
        txt.tag_configure("dim",     font=("Segoe UI", 8),          foreground=TEXT_DIM,
                          lmargin1=8)
        txt.tag_configure("rule",    foreground=BORDER)

        for line in README_CONTENT.splitlines():
            if line.startswith("# "):
                txt.insert(END, line[2:] + "\n", "title")
            elif line.startswith("━"):
                # Section header follows the rule line
                txt.insert(END, line + "\n", "rule")
            elif line.strip().startswith("·") or line.strip().startswith("→"):
                txt.insert(END, line + "\n", "dim")
            elif (line.startswith("    ") or line.startswith("\t")) and line.strip():
                txt.insert(END, line + "\n", "code")
            elif line.strip() == "":
                txt.insert(END, "\n", "body")
            else:
                txt.insert(END, line + "\n", "body")

        txt.configure(state=DISABLED)

        # Mouse-wheel scrolling
        txt.bind("<MouseWheel>",
                 lambda e: txt.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ── Bottom bar ────────────────────────────────────────────────────
        Frame(self, bg=BORDER, height=1).pack(fill=X)
        bot = Frame(self, bg=BG_PANEL, height=36)
        bot.pack(fill=X, side=BOTTOM); bot.pack_propagate(False)
        Label(bot,
              text="Powered by DAT (Dans Automation Tools)  ·  DMurr5050@gmail.com",
              font=("Segoe UI", 8), fg=MUTED, bg=BG_PANEL).pack(side=LEFT, padx=16, pady=8)


# ── Folder Cleanup Dialog ─────────────────────────────────────────────────────
CLEANUP_EXTENSIONS = {'.txt', '.idx', '.nfo', '.jpg', '.htm', '.png', '.url', '.bif'}

class CleanupDialog(Toplevel):
    """
    Scans a chosen folder recursively and removes junk sidecar files
    (.txt .idx .nfo .jpg .htm .png .url .bif) plus leftover empty folders,
    mirroring the behaviour of the JD Downloads cleanup batch file.
    """

    def __init__(self, parent, default_folder: str = ""):
        super().__init__(parent)
        self.title("Folder Cleanup")
        self.geometry("760x580")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.grab_set()
        self._folder_var  = StringVar(value=default_folder)
        self._scan_result = []   # list of Path objects found
        self._running     = False
        self._build()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = Frame(self, bg=BG_PANEL, height=52)
        hdr.pack(fill=X); hdr.pack_propagate(False)
        Frame(hdr, bg=ERROR, width=4).pack(side=LEFT, fill=Y)
        Label(hdr, text="🧹  Folder Cleanup", font=("Segoe UI", 13, "bold"),
              fg=ERROR, bg=BG_PANEL).pack(side=LEFT, padx=14)
        Label(hdr, text="Removes junk sidecar files and empty folders",
              font=FONT_SMALL, fg=MUTED, bg=BG_PANEL).pack(side=LEFT)
        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Folder picker
        fp = Frame(self, bg=BG_PANEL)
        fp.pack(fill=X, padx=16, pady=10)
        Label(fp, text="FOLDER TO CLEAN", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, pady=(0, 4))
        ff = Frame(fp, bg=BG_SURFACE, bd=0, highlightthickness=1,
                   highlightbackground=BORDER)
        ff.pack(fill=X)
        Entry(ff, textvariable=self._folder_var, font=FONT_MONO_SM,
              bg=BG_SURFACE, fg=TEXT, bd=0, insertbackground=ERROR,
              highlightthickness=0).pack(side=LEFT, fill=X, expand=True, padx=8, pady=6)
        bb = Label(ff, text="…", font=FONT_BOLD, fg=ERROR,
                   bg=BG_SURFACE, cursor="hand2", padx=10)
        bb.pack(side=RIGHT)
        bb.bind("<Button-1>", lambda e: self._pick_folder())

        # Extensions info
        ext_str = "  ".join(f"*{x}" for x in sorted(CLEANUP_EXTENSIONS))
        Label(fp, text=f"Will delete:  {ext_str}",
              font=("Segoe UI", 8), fg=MUTED, bg=BG_PANEL).pack(anchor=W, pady=(4, 0))
        Label(fp, text="Also removes: empty subfolders · System Volume Information",
              font=("Segoe UI", 8), fg=MUTED, bg=BG_PANEL).pack(anchor=W)

        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Scan / results area
        Label(self, text="SCAN RESULTS", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_DARK).pack(anchor=W, padx=16, pady=(10, 4))

        list_frame = Frame(self, bg=BG_DARK)
        list_frame.pack(fill=BOTH, expand=True, padx=16, pady=(0, 8))
        self._canvas = Canvas(list_frame, bg=BG_DARK, highlightthickness=0, bd=0)
        sb = Scrollbar(list_frame, orient=VERTICAL, command=self._canvas.yview,
                       bg=BG_SURFACE, troughcolor=BG_DARK)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=RIGHT, fill=Y)
        self._canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self._inner = Frame(self._canvas, bg=BG_DARK)
        self._cwin  = self._canvas.create_window((0, 0), window=self._inner, anchor=NW)
        self._inner.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cwin, width=e.width))
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._placeholder = Label(self._inner,
            text="Choose a folder and click Scan to preview what will be removed.",
            font=FONT_SMALL, fg=MUTED, bg=BG_DARK)
        self._placeholder.pack(pady=40)

        # Bottom bar
        Frame(self, bg=BORDER, height=1).pack(fill=X)
        bot = Frame(self, bg=BG_PANEL)
        bot.pack(fill=X, padx=16, pady=10)

        self._status_lbl = Label(bot, text="", font=FONT_SMALL,
                                  fg=TEXT_DIM, bg=BG_PANEL)
        self._status_lbl.pack(side=LEFT)

        cancel_lbl = Label(bot, text="Close", font=FONT_SMALL,
                           fg=MUTED, bg=BG_PANEL, cursor="hand2", padx=12, pady=8)
        cancel_lbl.pack(side=RIGHT)
        cancel_lbl.bind("<Button-1>", lambda e: self.destroy())

        self._run_btn = Label(bot, text="🗑  Delete All Listed Files",
                              font=FONT_BOLD, fg="#000", bg=ERROR,
                              cursor="hand2", padx=20, pady=8)
        self._run_btn.pack(side=RIGHT, padx=(0, 8))
        self._run_btn.bind("<Button-1>", lambda e: self._run_cleanup())
        self._run_btn.bind("<Enter>",
            lambda e: self._run_btn.configure(bg=self._lighten(ERROR)))
        self._run_btn.bind("<Leave>",
            lambda e: self._run_btn.configure(bg=ERROR))
        self._set_run_btn_state(False)

        self._scan_btn = Label(bot, text="🔍  Scan",
                               font=FONT_BOLD, fg="#000", bg=ACCENT,
                               cursor="hand2", padx=20, pady=8)
        self._scan_btn.pack(side=RIGHT, padx=(0, 6))
        self._scan_btn.bind("<Button-1>", lambda e: self._start_scan())
        self._scan_btn.bind("<Enter>",
            lambda e: self._scan_btn.configure(bg=self._lighten(ACCENT)))
        self._scan_btn.bind("<Leave>",
            lambda e: self._scan_btn.configure(bg=ACCENT))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _lighten(self, hc):
        h = hc.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return "#{:02x}{:02x}{:02x}".format(
            min(255, int(r*1.15)), min(255, int(g*1.15)), min(255, int(b*1.15)))

    def _pick_folder(self):
        f = filedialog.askdirectory(title="Select folder to clean", parent=self)
        if f:
            self._folder_var.set(f)
            self._scan_result.clear()
            self._render_results([])
            self._set_run_btn_state(False)

    def _set_run_btn_state(self, enabled: bool):
        if enabled:
            self._run_btn.configure(fg="#000", bg=ERROR, cursor="hand2")
        else:
            self._run_btn.configure(fg=MUTED, bg=BG_SURFACE, cursor="arrow")

    # ── Scan ──────────────────────────────────────────────────────────────────
    def _start_scan(self):
        folder = self._folder_var.get().strip()
        if not folder:
            messagebox.showwarning("No Folder", "Please choose a folder first.", parent=self)
            return
        root = Path(folder)
        if not root.is_dir():
            messagebox.showerror("Not Found", f"Folder not found:\n{root}", parent=self)
            return
        self._status_lbl.configure(text="Scanning…", fg=WARNING)
        self._set_run_btn_state(False)
        self._render_results([])
        self.update_idletasks()
        threading.Thread(target=self._scan_worker, args=(root,), daemon=True).start()

    def _scan_worker(self, root: Path):
        found_files  = []
        found_folders = []
        try:
            # Collect matching files
            for p in sorted(root.rglob("*")):
                if p.is_file() and p.suffix.lower() in CLEANUP_EXTENSIONS:
                    found_files.append(p)
            # Collect empty dirs (deepest first) — skip root itself
            for p in sorted(root.rglob("*"), key=lambda x: len(x.parts), reverse=True):
                if p.is_dir() and p != root:
                    try:
                        if not any(p.iterdir()):
                            found_folders.append(p)
                    except PermissionError:
                        pass
            # Also flag System Volume Information
            svi = root / "System Volume Information"
            if svi.is_dir() and svi not in found_folders:
                found_folders.append(svi)
        except Exception as ex:
            self.after(0, lambda: self._status_lbl.configure(
                text=f"Scan error: {ex}", fg=ERROR))
            return

        self._scan_result = found_files + found_folders
        self.after(0, lambda: self._scan_done(found_files, found_folders))

    def _scan_done(self, files, folders):
        total = len(files) + len(folders)
        if total == 0:
            self._status_lbl.configure(
                text="✓  Nothing to clean — folder is already tidy.", fg=SUCCESS)
            self._render_results([])
        else:
            self._status_lbl.configure(
                text=f"Found {len(files)} file(s) and {len(folders)} empty folder(s) to remove.",
                fg=WARNING)
            self._render_results(files, folders)
            self._set_run_btn_state(True)

    def _render_results(self, files=(), folders=()):
        for w in self._inner.winfo_children():
            w.destroy()

        if not files and not folders:
            Label(self._inner,
                  text="Choose a folder and click Scan to preview what will be removed.",
                  font=FONT_SMALL, fg=MUTED, bg=BG_DARK).pack(pady=40)
            self._canvas.update_idletasks()
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
            return

        all_items = [(p, "file") for p in files] + [(p, "folder") for p in folders]
        for i, (p, kind) in enumerate(all_items):
            bg = BG_ROW if i % 2 == 0 else BG_ROW_ALT
            row = Frame(self._inner, bg=bg)
            row.pack(fill=X)
            # Icon + type badge
            icon = "📁" if kind == "folder" else self._ext_icon(p.suffix.lower())
            Label(row, text=icon, font=("Segoe UI", 9),
                  bg=bg, padx=8, pady=5).pack(side=LEFT)
            # Extension badge
            badge_fg = "#c06020" if kind == "folder" else "#6080c0"
            badge_bg = "#2a1800" if kind == "folder" else "#0d1a2a"
            tag = "DIR" if kind == "folder" else p.suffix.upper().lstrip(".")
            Label(row, text=tag, font=("Segoe UI", 7, "bold"),
                  fg=badge_fg, bg=badge_bg, padx=5, pady=2).pack(side=LEFT, padx=(0, 6))
            # Path display — show relative path for readability
            try:
                folder = Path(self._folder_var.get())
                display = str(p.relative_to(folder))
            except ValueError:
                display = str(p)
            Label(row, text=display, font=FONT_MONO_SM, fg=TEXT_DIM,
                  bg=bg, anchor=W).pack(side=LEFT, fill=X, expand=True, padx=(0, 10), pady=5)
            Frame(self._inner, bg=BORDER, height=1).pack(fill=X)

        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _ext_icon(self, ext: str) -> str:
        return {"jpg": "🖼", ".jpg": "🖼", ".png": "🖼", ".nfo": "📄",
                ".txt": "📄", ".url": "🔗", ".htm": "🌐",
                ".idx": "📋", ".bif": "📋"}.get(ext, "📄")

    # ── Cleanup ───────────────────────────────────────────────────────────────
    def _run_cleanup(self):
        if self._running or not self._scan_result:
            return
        folder = self._folder_var.get().strip()
        n = len(self._scan_result)
        self._running = True
        self._set_run_btn_state(False)
        self._scan_btn.configure(fg=MUTED, bg=BG_SURFACE, cursor="arrow")
        self._status_lbl.configure(text="Deleting…", fg=WARNING)
        self.update_idletasks()
        threading.Thread(target=self._cleanup_worker,
                         args=(Path(folder), list(self._scan_result)),
                         daemon=True).start()

    def _cleanup_worker(self, root: Path, items: list):
        deleted_files = 0
        deleted_dirs  = 0
        errors        = []
        log_lines     = ["CLEANUP LOG", "=" * 60]

        # ── Delete files ──────────────────────────────────────────────────
        for p in items:
            if not p.is_file():
                continue
            try:
                # Clear read-only attribute before deleting (mirrors attrib -r)
                try:
                    p.chmod(p.stat().st_mode | 0o200)
                except Exception:
                    pass
                p.unlink()
                log_lines.append(f"  ✓  {p}")
                deleted_files += 1
            except Exception as ex:
                log_lines.append(f"  ✗  {p}  —  {ex}")
                errors.append(str(ex))

        # ── Remove empty dirs (deepest first) ────────────────────────────
        # Re-scan after file deletion so newly-emptied dirs are caught too
        dirs_to_try = []
        try:
            for p in sorted(root.rglob("*"), key=lambda x: len(x.parts), reverse=True):
                if p.is_dir() and p != root:
                    dirs_to_try.append(p)
            # Also System Volume Information
            svi = root / "System Volume Information"
            if svi.is_dir() and svi not in dirs_to_try:
                dirs_to_try.insert(0, svi)
        except Exception:
            pass

        for d in dirs_to_try:
            try:
                if not d.exists():
                    continue
                # Force-remove System Volume Information; otherwise only empty dirs
                is_svi = d.name == "System Volume Information"
                if is_svi:
                    shutil.rmtree(str(d), ignore_errors=True)
                    if not d.exists():
                        log_lines.append(f"  🗑  {d}  [System Volume Information removed]")
                        deleted_dirs += 1
                else:
                    if not any(d.iterdir()):
                        d.rmdir()
                        log_lines.append(f"  🗑  {d}  [empty folder removed]")
                        deleted_dirs += 1
            except Exception as ex:
                errors.append(str(ex))

        self.after(0, lambda: self._cleanup_done(deleted_files, deleted_dirs, errors, log_lines))

    def _cleanup_done(self, files: int, dirs: int, errors: list, log_lines: list):
        self._running = False
        self._scan_result.clear()
        self._render_results()

        parts = []
        if files: parts.append(f"{files} file(s) deleted")
        if dirs:  parts.append(f"{dirs} folder(s) removed")
        if errors: parts.append(f"{len(errors)} error(s)")
        summary = "  ·  ".join(parts) if parts else "Nothing was deleted"

        fg = SUCCESS if not errors else WARNING
        self._status_lbl.configure(text=f"✓  Done — {summary}", fg=fg)

        # Re-enable scan button
        self._scan_btn.configure(fg="#000", bg=ACCENT, cursor="hand2")

        # Show log
        win = Toplevel(self); win.title("Cleanup Complete")
        win.geometry("660x440"); win.configure(bg=BG_DARK); win.grab_set()
        Label(win, text="Cleanup Complete", font=FONT_BOLD, fg=ERROR,
              bg=BG_DARK).pack(anchor=W, padx=16, pady=(14, 6))
        Frame(win, bg=BORDER, height=1).pack(fill=X, padx=16)
        tf = Frame(win, bg=BG_SURFACE); tf.pack(fill=BOTH, expand=True, padx=16, pady=12)
        sb_w = Scrollbar(tf); sb_w.pack(side=RIGHT, fill=Y)
        txt = Text(tf, bg=BG_SURFACE, fg=SUCCESS, font=FONT_MONO, bd=0,
                   padx=12, pady=10, yscrollcommand=sb_w.set,
                   wrap=WORD, insertbackground=ERROR)
        txt.pack(fill=BOTH, expand=True); sb_w.config(command=txt.yview)
        txt.insert(END, "\n".join(log_lines))
        txt.configure(state=DISABLED)
        Button(win, text="Close", command=win.destroy, bg=BG_SURFACE, fg=TEXT,
               font=FONT_SMALL, bd=0, padx=20, pady=8, cursor="hand2",
               activebackground=BG_HOVER, activeforeground=WHITE).pack(pady=(0, 14))



# ── Auto-updater ──────────────────────────────────────────────────────────────
def _parse_version(v: str):
    """Convert '1.07' → (1, 7) for numeric comparison."""
    try:
        parts = str(v).lstrip("vV").strip().split(".")
        return tuple(int(x) for x in parts)
    except Exception:
        return (0,)

def fetch_latest_version() -> tuple:
    """
    Check GitHub releases API for the latest version tag.
    Returns (version_string, download_url) or raises on failure.
    Falls back to reading VERSION from raw plexbot.py if no release tag found.
    """
    # Try releases API first
    try:
        r = requests.get(GITHUB_API_URL,
                         headers={"Accept": "application/vnd.github+json"},
                         timeout=8)
        if r.status_code == 200:
            data = r.json()
            tag = data.get("tag_name", "").lstrip("vV")
            if tag:
                return tag, GITHUB_RAW_URL
    except Exception:
        pass

    # Fallback: read VERSION from raw source
    r = requests.get(GITHUB_RAW_URL, timeout=10)
    r.raise_for_status()
    for line in r.text.splitlines():
        if line.strip().startswith("VERSION"):
            # e.g.  VERSION       = "1.07"
            val = line.split("=", 1)[1].strip().strip('"').strip("'")
            return val, GITHUB_RAW_URL
    raise ValueError("Could not determine remote version")

def download_update(dest_path: Path, progress_cb=None) -> bool:
    """
    Download the latest plexbot.py to dest_path.
    progress_cb(pct) called with 0-100 during download.
    Returns True on success.
    """
    r = requests.get(GITHUB_RAW_URL, stream=True, timeout=30)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    downloaded = 0
    chunks = []
    for chunk in r.iter_content(chunk_size=8192):
        if chunk:
            chunks.append(chunk)
            downloaded += len(chunk)
            if progress_cb and total:
                progress_cb(int(downloaded / total * 100))
    dest_path.write_bytes(b"".join(chunks))
    return True


# ── Update Dialog ─────────────────────────────────────────────────────────────
class UpdateDialog(Toplevel):
    """
    Shown when a newer version is available on GitHub.
    Handles both .py (in-place replace + restart) and .exe (opens releases page).
    """
    def __init__(self, parent, remote_version: str):
        super().__init__(parent)
        self.title("Update Available")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.grab_set()
        self._remote = remote_version
        self._build()
        self.update_idletasks()
        # Centre over parent
        w, h = 480, 260
        px = parent.winfo_rootx() + (parent.winfo_width()  - w) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{max(0,px)}+{max(0,py)}")

    def _build(self):
        # Header
        hdr = Frame(self, bg=BG_PANEL, height=52)
        hdr.pack(fill=X); hdr.pack_propagate(False)
        Frame(hdr, bg=SUCCESS, width=4).pack(side=LEFT, fill=Y)
        Label(hdr, text="⬆  Update Available",
              font=("Segoe UI", 13, "bold"), fg=SUCCESS, bg=BG_PANEL
              ).pack(side=LEFT, padx=14)
        Frame(self, bg=BORDER, height=1).pack(fill=X)

        body = Frame(self, bg=BG_DARK)
        body.pack(fill=BOTH, expand=True, padx=24, pady=18)

        Label(body,
              text=f"PlexBot v{self._remote} is available  (you have v{VERSION})",
              font=("Segoe UI", 10), fg=TEXT, bg=BG_DARK).pack(anchor=W)

        Label(body,
              text=f"Source:  github.com/{GITHUB_USER}/{GITHUB_REPO}",
              font=FONT_MONO_SM, fg=TEXT_DIM, bg=BG_DARK).pack(anchor=W, pady=(6, 0))

        # Determine mode
        self._is_frozen = getattr(sys, "frozen", False)
        if self._is_frozen:
            note = ("Running as PlexBot.exe — the EXE cannot update itself.\n"
                    "Click below to open the Releases page and download the new EXE.")
        else:
            note = ("PlexBot will download the new plexbot.py, replace this file,\n"
                    "and ask you to restart the app.")

        Label(body, text=note, font=FONT_SMALL, fg=TEXT_DIM, bg=BG_DARK,
              justify=LEFT).pack(anchor=W, pady=(10, 0))

        # Progress bar (only relevant for .py update)
        self._prog_frame = Frame(body, bg=BG_DARK)
        self._prog_frame.pack(fill=X, pady=(12, 0))
        style = ttk.Style()
        style.configure("Upd.Horizontal.TProgressbar",
                        troughcolor=BG_SURFACE, background=SUCCESS,
                        borderwidth=0, lightcolor=SUCCESS, darkcolor=SUCCESS)
        self._prog = ttk.Progressbar(self._prog_frame,
                                     style="Upd.Horizontal.TProgressbar",
                                     mode="determinate", length=420)
        self._prog_lbl = Label(self._prog_frame, text="", font=FONT_SMALL,
                               fg=TEXT_DIM, bg=BG_DARK)

        # Buttons
        Frame(self, bg=BORDER, height=1).pack(fill=X)
        btn_row = Frame(self, bg=BG_PANEL); btn_row.pack(fill=X, pady=10)

        if self._is_frozen:
            self._update_btn = Label(btn_row, text="🌐  Open Releases Page",
                                     font=FONT_BOLD, fg="#000", bg=SUCCESS,
                                     cursor="hand2", padx=20, pady=8)
            self._update_btn.pack(side=LEFT, padx=16)
            self._update_btn.bind("<Button-1>", lambda e: self._open_releases())
        else:
            self._update_btn = Label(btn_row, text="⬆  Download & Install",
                                     font=FONT_BOLD, fg="#000", bg=SUCCESS,
                                     cursor="hand2", padx=20, pady=8)
            self._update_btn.pack(side=LEFT, padx=16)
            self._update_btn.bind("<Button-1>", lambda e: self._do_update())

        skip = Label(btn_row, text="Skip this update", font=FONT_SMALL,
                     fg=MUTED, bg=BG_PANEL, cursor="hand2", padx=16, pady=8)
        skip.pack(side=LEFT)
        skip.bind("<Button-1>", lambda e: self.destroy())

    def _open_releases(self):
        import webbrowser
        webbrowser.open(GITHUB_RELEASES_PAGE)
        self.destroy()

    def _do_update(self):
        """Download new plexbot.py and replace current file."""
        self._update_btn.configure(text="Downloading…", cursor="arrow",
                                   bg=BG_SURFACE, fg=MUTED)
        self._update_btn.unbind("<Button-1>")
        self._prog.pack(fill=X)
        self._prog_lbl.pack(fill=X)

        script_path = Path(__file__).resolve()
        tmp_path    = script_path.with_suffix(".py.update_tmp")

        def _run():
            try:
                def progress(pct):
                    self.after(0, lambda: self._prog.configure(value=pct))
                    self.after(0, lambda: self._prog_lbl.configure(
                        text=f"Downloading…  {pct}%"))
                download_update(tmp_path, progress_cb=progress)
                # Quick sanity check — make sure it looks like Python
                content = tmp_path.read_text(encoding="utf-8", errors="replace")
                if "VERSION" not in content or "PlexBot" not in content:
                    raise ValueError("Downloaded file doesn't look like plexbot.py")
                # Replace the running script
                script_path.write_bytes(tmp_path.read_bytes())
                tmp_path.unlink(missing_ok=True)
                self.after(0, self._update_done)
            except Exception as ex:
                try: tmp_path.unlink(missing_ok=True)
                except Exception: pass
                self.after(0, lambda: self._update_error(str(ex)))

        threading.Thread(target=_run, daemon=True).start()

    def _update_done(self):
        self._prog.configure(value=100)
        self._prog_lbl.configure(text="Download complete!")
        if messagebox.askyesno(
                "Restart Required",
                f"PlexBot v{self._remote} has been downloaded.\n\n"
                "Restart the app now to use the new version?",
                parent=self):
            python = sys.executable
            os.execv(python, [python] + sys.argv)
        self.destroy()

    def _update_error(self, msg: str):
        self._prog_lbl.configure(text=f"Error: {msg}", fg=ERROR)
        self._update_btn.configure(text="⬆  Retry", cursor="hand2",
                                   bg=SUCCESS, fg="#000")
        self._update_btn.bind("<Button-1>", lambda e: self._do_update())


# ── Main Window ───────────────────────────────────────────────────────────────
class PlexBot(Tk):
    def __init__(self):
        # Use TkinterDnD root if available so drag-and-drop works app-wide
        try:
            from tkinterdnd2 import TkinterDnD
            TkinterDnD.Tk.__init__(self)
        except ImportError:
            Tk.__init__(self)
        self.title(f"{APP_TITLE} v{VERSION} — Plex Media Renamer | Powered by DAT")
        self.geometry("1100x760")
        self.minsize(900, 640)
        self.configure(bg=BG_DARK)
        self.last_source_folder = ""
        self._build()
        self._set_window_icon()
        # Check for updates in the background — never blocks startup
        self.after(3000, self._start_update_check)

    def _set_window_icon(self):
        """Set the taskbar / titlebar icon from plexbot.ico (same folder as script)."""
        # Locate the .ico next to the running script / frozen exe
        if getattr(sys, "frozen", False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent

        ico_path = base / "plexbot.ico"
        if ico_path.exists():
            try:
                # iconbitmap works on Windows and shows in the taskbar
                self.iconbitmap(str(ico_path))
                return
            except Exception:
                pass

        # Fallback: use the embedded PNG header icon via PhotoImage
        # (works cross-platform but won't show in the Windows taskbar)
        try:
            import base64 as _b64
            from tkinter import PhotoImage as _PI
            _data = _b64.b64decode(HEADER_ICON_B64)
            _img  = _PI(data=_b64.b64encode(_data))
            self._taskbar_icon = _img   # keep reference
            self.iconphoto(True, _img)
        except Exception:
            pass

    def _build(self):
        # Header
        header = Frame(self, bg=BG_PANEL, height=58)
        header.pack(fill=X); header.pack_propagate(False)
        Frame(header, bg=ACCENT, width=4).pack(side=LEFT, fill=Y)

        # ── App icon + title block ────────────────────────────────────────
        tf = Frame(header, bg=BG_PANEL)
        tf.pack(side=LEFT, padx=(10, 0), pady=4)

        # Load and display the embedded icon
        try:
            import base64, io
            from tkinter import PhotoImage
            _ico_data = base64.b64decode(HEADER_ICON_B64)
            _ico_img  = PhotoImage(data=base64.b64encode(_ico_data))
            # Keep reference so it isn't garbage-collected
            self._header_icon = _ico_img
            Label(tf, image=_ico_img, bg=BG_PANEL).pack(side=LEFT, padx=(0, 8))
        except Exception:
            pass  # Icon failed to load — no crash, just skip it

        # Title text column
        title_col = Frame(tf, bg=BG_PANEL)
        title_col.pack(side=LEFT)

        # Row 1: PlexBot v1.0 · Media File Renamer
        row1 = Frame(title_col, bg=BG_PANEL)
        row1.pack(anchor=W)
        Label(row1, text="PlexBot", font=("Segoe UI", 17, "bold"),
              fg=ACCENT, bg=BG_PANEL).pack(side=LEFT)
        Label(row1, text=f" v{VERSION}", font=("Segoe UI", 10),
              fg=MUTED, bg=BG_PANEL).pack(side=LEFT, pady=(4, 0))
        Label(row1, text="  ·  Media File Renamer", font=("Segoe UI", 10),
              fg=TEXT_DIM, bg=BG_PANEL).pack(side=LEFT, pady=(4, 0))

        # Row 2: Powered by DAT
        row2 = Frame(title_col, bg=BG_PANEL)
        row2.pack(anchor=W)
        Label(row2, text="Powered by DAT (Dans Automation Tools)",
              font=("Segoe UI", 8), fg="#555577",
              bg=BG_PANEL).pack(side=LEFT)

        # ── Donate + Contact buttons (centred in header) ────────────────
        centre_frame = Frame(header, bg=BG_PANEL)
        centre_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        donate_btn = Label(
            centre_frame,
            text="💛  Donate via PayPal",
            font=("Segoe UI", 9, "bold"),
            fg="#000000", bg="#FFD700",
            cursor="hand2", padx=14, pady=6,
        )
        donate_btn.pack(side=LEFT, padx=(0, 6))
        donate_btn.bind("<Button-1>",
            lambda e: __import__("webbrowser").open(
                "https://www.paypal.com/donate/?hosted_button_id=6QVE3GP6SD8ZQ"))
        donate_btn.bind("<Enter>", lambda e: donate_btn.configure(bg="#FFC200"))
        donate_btn.bind("<Leave>", lambda e: donate_btn.configure(bg="#FFD700"))

        def _copy_contact():
            self.clipboard_clear()
            self.clipboard_append("DMurr5050@gmail.com")
            self.update()
            # Brief flash + tooltip-style notification
            contact_btn.configure(text="✓  Copied!", bg="#27ae60")
            self.after(2000, lambda: contact_btn.configure(
                text="✉  Contact", bg="#3a7bd5"))
            messagebox.showinfo(
                "Email Copied",
                "DMurr5050@gmail.com has been copied to your clipboard.\n\n"
                "Open your email app and paste it into the To: field.",
                parent=self)

        contact_btn = Label(
            centre_frame,
            text="✉  Contact",
            font=("Segoe UI", 9, "bold"),
            fg="#ffffff", bg="#3a7bd5",
            cursor="hand2", padx=14, pady=6,
        )
        contact_btn.pack(side=LEFT)
        contact_btn.bind("<Button-1>", lambda e: _copy_contact())
        contact_btn.bind("<Enter>", lambda e: contact_btn.configure(bg="#2d63b8"))
        contact_btn.bind("<Leave>", lambda e: contact_btn.configure(bg="#3a7bd5"))

        # History button (right side of header)
        hist_btn = Label(header, text="📋  History", font=FONT_SMALL,
                         fg=MUTED, bg=BG_PANEL, cursor="hand2", padx=16)
        hist_btn.pack(side=RIGHT, pady=0)
        hist_btn.bind("<Button-1>", lambda e: HistoryDialog(self))
        hist_btn.bind("<Enter>",    lambda e: hist_btn.configure(fg=WHITE))
        hist_btn.bind("<Leave>",    lambda e: hist_btn.configure(fg=MUTED))

        # Help button (right side of header)
        help_btn = Label(header, text="❓  Help", font=FONT_SMALL,
                         fg=MUTED, bg=BG_PANEL, cursor="hand2", padx=16)
        help_btn.pack(side=RIGHT, pady=0)
        help_btn.bind("<Button-1>", lambda e: ReadmeDialog(self))
        help_btn.bind("<Enter>",    lambda e: help_btn.configure(fg=ACCENT_BLUE))
        help_btn.bind("<Leave>",    lambda e: help_btn.configure(fg=MUTED))

        # Cleanup button (right side of header)
        clean_btn = Label(header, text="🧹  Cleanup", font=FONT_SMALL,
                          fg=MUTED, bg=BG_PANEL, cursor="hand2", padx=16)
        clean_btn.pack(side=RIGHT, pady=0)
        def _open_cleanup(e=None):
            default = self.last_source_folder or ""
            CleanupDialog(self, default_folder=default)
        clean_btn.bind("<Button-1>", lambda e: _open_cleanup())
        clean_btn.bind("<Enter>",    lambda e: clean_btn.configure(fg=ERROR))
        clean_btn.bind("<Leave>",    lambda e: clean_btn.configure(fg=MUTED))

        # Update banner — hidden until an update is found
        self._update_banner = Frame(self, bg="#1a2e1a", height=28)
        self._update_banner_lbl = Label(self._update_banner, text="",
                                        font=("Segoe UI", 9), fg=SUCCESS,
                                        bg="#1a2e1a", cursor="hand2")
        self._update_banner_lbl.pack(side=LEFT, padx=12, fill=Y)
        self._update_banner_x = Label(self._update_banner, text="✕",
                                      font=("Segoe UI", 9), fg=MUTED,
                                      bg="#1a2e1a", cursor="hand2", padx=10)
        self._update_banner_x.pack(side=RIGHT)
        self._update_banner_x.bind("<Button-1>",
                                   lambda e: self._update_banner.pack_forget())

        # Tabs
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("PB.TNotebook",
                        background=BG_DARK, borderwidth=0, tabmargins=0)
        style.configure("PB.TNotebook.Tab",
                        background=BG_PANEL, foreground=MUTED,
                        font=("Segoe UI",10,"bold"), padding=[22,8], borderwidth=0)
        style.map("PB.TNotebook.Tab",
                  background=[("selected", BG_DARK)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self, style="PB.TNotebook")
        nb.pack(fill=BOTH, expand=True)

        self.tv_tab     = TVTab(nb, self)
        self.movies_tab = MoviesTab(nb, self)
        nb.add(self.tv_tab,     text="  📺  TV Shows  ")
        nb.add(self.movies_tab, text="  🎬  Movies  ")

        # Status bar
        sb = Frame(self, bg=BG_PANEL, height=28)
        sb.pack(fill=X, side=BOTTOM); sb.pack_propagate(False)
        Frame(sb, bg=BORDER, height=1).pack(fill=X)
        self._sv = StringVar(value="  Ready — select a tab and add files")
        Label(sb, textvariable=self._sv, font=FONT_SMALL,
              fg=TEXT_DIM, bg=BG_PANEL, anchor=W, padx=12).pack(side=LEFT, fill=Y)
        self.file_count_label = Label(sb, text="", font=FONT_SMALL,
              fg=MUTED, bg=BG_PANEL, anchor=E, padx=12)
        self.file_count_label.pack(side=RIGHT, fill=Y)

    def set_status(self, msg: str):
        self._sv.set(f"  {msg}")

    def _start_update_check(self):
        """Fire a background thread to check GitHub for a newer version."""
        def _check():
            try:
                remote_ver, _ = fetch_latest_version()
                if _parse_version(remote_ver) > _parse_version(VERSION):
                    self.after(0, lambda: self._show_update_banner(remote_ver))
            except Exception:
                pass  # No network / rate-limited — fail silently
        threading.Thread(target=_check, daemon=True).start()

    def _show_update_banner(self, remote_version: str):
        """Show a slim green banner below the header offering the update."""
        self._update_banner_lbl.configure(
            text=f"⬆  PlexBot v{remote_version} is available — click to update")
        self._update_banner_lbl.bind(
            "<Button-1>", lambda e: UpdateDialog(self, remote_version))
        # Insert banner between header and the notebook
        self._update_banner.pack(fill=X, before=self.winfo_children()[1])


# ── Entry Point ───────────────────────────────────────────────────────────────
def main():
    try:
        import requests  # noqa
    except ImportError:
        print("ERROR: 'requests' not found.\nRun:  pip install requests")
        sys.exit(1)
    try:
        import tkinterdnd2  # noqa
    except ImportError:
        print("TIP: Install tkinterdnd2 to enable drag-and-drop:\n"
              "     pip install tkinterdnd2")
    PlexBot().mainloop()

if __name__ == "__main__":
    main()
