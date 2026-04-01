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
TVMAZE_BASE  = "https://api.tvmaze.com"
OMDB_BASE    = "http://www.omdbapi.com"
OMDB_API_KEY = ""          # Paste your free OMDb key here, or enter it in the Movies tab
APP_TITLE    = "PlexBot"
VERSION      = "1.02"

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
    time.sleep(0.2)
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
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", str(filepath)],
            capture_output=True, timeout=15)
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
                  use_res: bool, use_vc: bool, use_ac: bool) -> str:
    show  = safe_name(parsed["show_name"])
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
        self.geometry("680x520")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.grab_set()
        self.focus_set()

        self.search_fn     = search_fn
        self.color         = color
        self.chosen        = None   # Set when user picks a result
        self._results      = []
        self._search_after = None

        self._build(filename, initial_query)
        self.after(100, lambda: self._do_search(initial_query))

        # Block caller until dialog closes
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
        _saved_mode = load_config().get("file_mode", "move")
        self.opt_copy_mode   = BooleanVar(value=(_saved_mode == "copy"))
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
        # Destination
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

        Frame(p, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(10, 6))

        # Copy / Move toggle
        Label(p, text="FILE OPERATION", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(0, 6))
        fof = Frame(p, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        fof.pack(fill=X, padx=16)

        # Two pill-style radio buttons inside the box
        self._mode_frame = Frame(fof, bg=BG_SURFACE)
        self._mode_frame.pack(fill=X, padx=8, pady=8)

        self._move_btn = Label(self._mode_frame, text="✂  Move",
                               font=FONT_SMALL, fg="#000",
                               bg=self.color, cursor="hand2",
                               padx=12, pady=5, anchor=CENTER)
        self._move_btn.pack(side=LEFT, fill=X, expand=True, padx=(0, 4))

        self._copy_btn = Label(self._mode_frame, text="⎘  Copy",
                               font=FONT_SMALL, fg=TEXT_DIM,
                               bg=BG_DARK, cursor="hand2",
                               padx=12, pady=5, anchor=CENTER)
        self._copy_btn.pack(side=LEFT, fill=X, expand=True)

        # Hint line
        self._mode_hint = Label(p, text="Original file will be deleted after rename",
                                font=("Segoe UI", 8), fg=MUTED,
                                bg=BG_PANEL, wraplength=240, justify=LEFT)
        self._mode_hint.pack(anchor=W, padx=16, pady=(2, 0))

        def _set_move():
            self.opt_copy_mode.set(False)
            self._move_btn.configure(fg="#000", bg=self.color)
            self._copy_btn.configure(fg=TEXT_DIM, bg=BG_DARK)
            self._mode_hint.configure(text="Original file will be deleted after rename")
            save_config({"file_mode": "move"})
            self._update_preview()

        def _set_copy():
            self.opt_copy_mode.set(True)
            self._copy_btn.configure(fg="#000", bg=self.color)
            self._move_btn.configure(fg=TEXT_DIM, bg=BG_DARK)
            self._mode_hint.configure(text="Original file is kept — a renamed copy is created")
            save_config({"file_mode": "copy"})
            self._update_preview()

        self._move_btn.bind("<Button-1>", lambda e: _set_move())
        self._copy_btn.bind("<Button-1>", lambda e: _set_copy())

        # Apply saved state on init
        if self.opt_copy_mode.get():
            _set_copy()

        Frame(p, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(10, 0))

        # Checkboxes
        Label(p, text="INCLUDE IN FILENAME", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(0, 6))
        cbf = Frame(p, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        cbf.pack(fill=X, padx=16)
        for txt, var, tip in [
            ("  Video Resolution  (e.g. 1080p)", self.opt_resolution,  "Append resolution tag"),
            ("  Video Codec       (e.g. HEVC)",  self.opt_video_codec, "Append video codec tag"),
            ("  Audio Channels    (e.g. 5.1)",   self.opt_audio_codec, "Append audio channel count like 5.1, 7.1, 2.0"),
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

        Frame(p, bg=BORDER, height=1).pack(fill=X, padx=16, pady=(10, 0))

        # Preview
        Label(p, text="FORMAT PREVIEW", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(10, 6))
        pbox = Frame(p, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        pbox.pack(fill=X, padx=16)
        self.preview_label = Label(pbox, text="", font=("Consolas", 8),
                                   fg=SUCCESS, bg=BG_SURFACE, wraplength=230,
                                   justify=LEFT, padx=10, pady=10)
        self.preview_label.pack()
        self._update_preview()

        Frame(p, bg=BORDER, height=1).pack(fill=X, padx=16, pady=12)

        # Buttons
        self.lookup_btn = self._big_btn(p, self._lookup_label(), self._start_lookup,
                                        self.color, "#000")
        self.lookup_btn.pack(fill=X, padx=16, pady=(0, 8))

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
        self.apply_btn.pack(fill=X, padx=16, pady=(0, 6))

        self.dryrun_btn = self._big_btn(p, "👁  Preview Only", self._dry_run,
                                        BLUE, WHITE, state=DISABLED)
        self.dryrun_btn.pack(fill=X, padx=16, pady=(0, 6))

        Frame(p, bg=BORDER, height=1).pack(fill=X, padx=16, pady=6)

        Label(p, text="SUMMARY", font=("Segoe UI", 9, "bold"),
              fg=MUTED, bg=BG_PANEL).pack(anchor=W, padx=16, pady=(0, 6))
        sf = Frame(p, bg=BG_SURFACE, bd=0, highlightthickness=1, highlightbackground=BORDER)
        sf.pack(fill=X, padx=16)
        self.sum_total = self._srow(sf, "Total files", "0", TEXT_DIM)
        self.sum_ready = self._srow(sf, "Matched",     "0", SUCCESS)
        self.sum_skip  = self._srow(sf, "Unmatched",   "0", MUTED)
        self.sum_error = self._srow(sf, "Errors",      "0", ERROR)

    # ── Helpers ───────────────────────────────────────────────────────────────
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
        self._disable_btn(self.dryrun_btn)
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
        for w in self.rows_frame.winfo_children(): w.destroy()
        for i, e in enumerate(self.file_entries):
            self._row(e, i, BG_ROW if i%2==0 else BG_ROW_ALT)
        self.app.file_count_label.config(
            text=f"{len(self.file_entries)} file{'s' if len(self.file_entries)!=1 else ''}")
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _row(self, entry, idx, bg):
        row = Frame(self.rows_frame, bg=bg, height=38)
        row.pack(fill=X); row.pack_propagate(False)
        on_e = lambda e, r=row: (r.configure(bg=BG_HOVER),
               [c.configure(bg=BG_HOVER) for c in r.winfo_children()])
        on_l = lambda e, r=row, b=bg: (r.configure(bg=b),
               [c.configure(bg=b) for c in r.winfo_children()])
        row.bind("<Enter>", on_e); row.bind("<Leave>", on_l)

        rm = Label(row, text="✕", font=("Segoe UI",9), fg=MUTED, bg=bg, cursor="hand2", padx=6)
        rm.pack(side=LEFT)
        rm.bind("<Button-1>", lambda e, i=idx: self._remove(i))
        rm.bind("<Enter>",    lambda e, l=rm: l.configure(fg=ERROR))
        rm.bind("<Leave>",    lambda e, l=rm, b=bg: l.configure(fg=MUTED))

        orig = Label(row, text=entry["path"].name, font=FONT_MONO_SM,
                     fg=TEXT_DIM, bg=bg, anchor=W, width=42)
        orig.pack(side=LEFT, padx=(2,0))
        Tooltip(orig, str(entry["path"]))

        Label(row, text=" → ", font=FONT_SMALL, fg=MUTED, bg=bg).pack(side=LEFT)

        st = entry["status"]
        fg_map   = {"pending":MUTED,"loading":WARNING,"done":SUCCESS,"error":ERROR,"renamed":ACCENT}
        text_map = {
            "pending": "— waiting —",
            "loading": "⟳ Looking up...",
            "done":    entry.get("new_name") or "—",
            "error":   f"✗ {entry.get('error_msg','Error')}",
            "renamed": f"✓ {entry.get('new_name','')}",
        }
        Label(row, text=text_map.get(st,"—"), font=FONT_MONO_SM,
              fg=fg_map.get(st,MUTED), bg=bg, anchor=W).pack(side=LEFT, fill=X, expand=True, padx=(0,6))

        pt, pf, pb = {"pending":("PENDING",MUTED,BG_SURFACE),"loading":("LOOKUP",WARNING,"#2a1f00"),
                      "done":("READY",SUCCESS,"#0d2a1a"),"error":("ERROR",ERROR,"#2a0d0d"),
                      "renamed":("DONE",ACCENT,"#2a1f00")}.get(st,("—",MUTED,BG_SURFACE))
        Label(row, text=pt, font=("Segoe UI",8,"bold"),
              fg=pf, bg=pb, padx=8, pady=2).pack(side=RIGHT, padx=8)
        Frame(self.rows_frame, bg=BORDER, height=1).pack(fill=X)

        # ── Subtitle sub-rows ──────────────────────────────────────────────
        for sub in entry.get("subtitles", []):
            sub_bg = "#161620"  # slightly different shade for sub-rows
            srow = Frame(self.rows_frame, bg=sub_bg, height=28)
            srow.pack(fill=X); srow.pack_propagate(False)

            # Indent marker
            Label(srow, text="   ↳", font=("Segoe UI",9), fg=MUTED,
                  bg=sub_bg, padx=6).pack(side=LEFT)
            Label(srow, text="SUB", font=("Segoe UI",7,"bold"),
                  fg="#6688aa", bg=sub_bg, padx=4).pack(side=LEFT)

            # Original subtitle name
            Label(srow, text=sub["path"].name, font=FONT_MONO_SM,
                  fg="#5566aa", bg=sub_bg, anchor=W, width=40).pack(side=LEFT, padx=(2,0))

            Label(srow, text=" → ", font=FONT_SMALL, fg=MUTED,
                  bg=sub_bg).pack(side=LEFT)

            # New subtitle name
            new_sub_fg = SUCCESS if st in ("done","renamed") else MUTED
            Label(srow, text=sub.get("new_name","—"), font=FONT_MONO_SM,
                  fg=new_sub_fg, bg=sub_bg, anchor=W).pack(
                  side=LEFT, fill=X, expand=True, padx=(0,8))

            Frame(self.rows_frame, bg="#1a1a28", height=1).pack(fill=X)

    # ── Lookup ────────────────────────────────────────────────────────────────
    def _start_lookup(self):
        if self.lookup_running: return
        if not self.file_entries:
            messagebox.showwarning("No Files", "Add some video files first."); return
        self.lookup_running = True
        self._disable_btn(self.lookup_btn)
        self._disable_btn(self.apply_btn)
        self._disable_btn(self.dryrun_btn)
        self.progress.pack(fill=X, pady=(0,4))
        self.prog_label.pack(fill=X)
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        total = len(self.file_entries)
        for i, entry in enumerate(self.file_entries):
            if entry["status"] == "renamed":
                self._prog(i+1, total, entry["path"].name); continue
            entry["status"] = "loading"
            self.after(0, self._refresh)
            if not entry["parsed"]:
                entry["status"] = "error"
                entry["error_msg"] = "Could not parse filename"
                self._prog(i+1, total, entry["path"].name); continue
            try:
                self._do_lookup(entry)
            except LookupNotFoundError as ex:
                # Show picker dialog on main thread, block until user picks
                event   = threading.Event()
                chosen  = [None]
                def show_picker(entry=entry, ex=ex, event=event, chosen=chosen):
                    dlg = self._show_picker(entry, str(ex.query))
                    chosen[0] = dlg.chosen if dlg else None
                    event.set()
                self.after(0, show_picker)
                event.wait()  # Block worker thread until dialog closes
                if chosen[0]:
                    try:
                        self._do_lookup_with_choice(entry, chosen[0])
                    except Exception as ex2:
                        entry["status"] = "error"
                        entry["error_msg"] = str(ex2)
                else:
                    entry["status"] = "error"
                    entry["error_msg"] = "Skipped by user"
            except Exception as ex:
                entry["status"] = "error"
                entry["error_msg"] = str(ex)
            self._prog(i+1, total, entry["path"].name)
        self.after(0, self._lookup_done)

    def _do_lookup(self, entry): pass           # override
    def _show_picker(self, entry, query): return None  # override
    def _do_lookup_with_choice(self, entry, choice): pass  # override

    def _prog(self, done, total, name):
        pct   = int(done/total*100)
        short = name[:50]+"…" if len(name)>50 else name
        self.after(0, lambda: self.progress.configure(value=pct))
        self.after(0, lambda: self.prog_label.configure(text=f"{done}/{total}  {short}"))
        self.after(0, self._refresh)
        self.after(0, self._summary)

    def _lookup_done(self):
        self.lookup_running = False
        self._enable_btn(self.lookup_btn, self._start_lookup)
        if any(e["status"]=="done" for e in self.file_entries):
            self._enable_btn(self.apply_btn, self._apply_rename)
            self._enable_btn(self.dryrun_btn, self._dry_run)
        ready  = sum(1 for e in self.file_entries if e["status"]=="done")
        errors = sum(1 for e in self.file_entries if e["status"]=="error")
        self.app.set_status(f"Lookup complete — {ready} ready, {errors} errors")
        self.after(2500, lambda: [self.progress.pack_forget(), self.prog_label.pack_forget()])

    # ── Apply / Dry run ───────────────────────────────────────────────────────
    def _dest_for(self, entry):
        dest = self.dest_var.get().strip()
        if dest:
            sub = safe_name(self._subfolder(entry))
            return Path(dest) / sub if sub else Path(dest)
        return entry["path"].parent

    def _subfolder(self, entry): return ""  # override

    def _dry_run(self):
        ready = [e for e in self.file_entries if e["status"]=="done"]
        if not ready:
            messagebox.showinfo("Nothing Ready","Run Lookup first."); return
        mode = "COPY  (original kept)" if self.opt_copy_mode.get() else "MOVE  (original deleted)"
        lines = [f"PREVIEW — no files will be changed\nMode: {mode}\n","="*60]
        for e in ready:
            lines.append(f"\n  FROM:  {e['path'].name}")
            lines.append(f"    TO:  {self._dest_for(e) / e['new_name']}")
        self._log("Preview (Dry Run)", "\n".join(lines))

    def _apply_rename(self):
        ready = [e for e in self.file_entries if e["status"]=="done"]
        if not ready:
            messagebox.showinfo("Nothing Ready","Run Lookup first."); return
        dest_root = self.dest_var.get().strip()
        dest_path = Path(dest_root) if dest_root else None
        copy_mode = self.opt_copy_mode.get()
        if dest_path and not dest_path.exists():
            if messagebox.askyesno("Create Folder?",
                    f"Destination doesn't exist:\n{dest_path}\n\nCreate it?"):
                dest_path.mkdir(parents=True)
            else: return
        op_word = "Copy" if copy_mode else "Rename"
        if not messagebox.askyesno("Confirm",
                f"{op_word} {len(ready)} file(s)"
                +(f"\nand {'copy' if copy_mode else 'move'} to:\n{dest_path}" if dest_path else "")
                +("\n\nOriginals will be KEPT." if copy_mode else "\n\nOriginals will be deleted.")
                +"\n\nContinue?"): return

        log_lines   = [f"{'COPY' if copy_mode else 'RENAME'} LOG","="*60]
        renamed = errors = sub_count = 0
        src_folders = set()  # Track folders we moved files out of

        for e in ready:
            src     = e["path"]
            tgt_dir = self._dest_for(e)
            tgt     = tgt_dir / e["new_name"]
            try:
                tgt_dir.mkdir(parents=True, exist_ok=True)

                # ── Find subtitle siblings BEFORE moving the video ──
                subs = find_subtitle_siblings(src)

                # ── Copy or Move / rename the video file ──
                e["_orig_name"] = src.name   # save before overwriting path
                if copy_mode:
                    shutil.copy2(str(src), str(tgt))
                elif dest_path:
                    shutil.move(str(src), str(tgt))
                else:
                    src.rename(tgt)
                src_folders.add(src.parent)
                e["path"] = tgt; e["status"] = "renamed"
                op_sym = "⎘" if copy_mode else "✓"
                log_lines.append(f"\n  {op_sym}  {src.name}\n     → {tgt}")
                renamed += 1

                # ── Copy or Move / rename each subtitle sibling ──
                for sub in subs:
                    new_sub_name = build_subtitle_name(e["new_name"], sub)
                    sub_tgt      = tgt_dir / new_sub_name
                    try:
                        if copy_mode:
                            shutil.copy2(str(sub), str(sub_tgt))
                        elif dest_path:
                            shutil.move(str(sub), str(sub_tgt))
                        else:
                            sub.rename(sub_tgt)
                        log_lines.append(f"     ↳ subtitle: {sub.name}\n              → {sub_tgt.name}")
                        src_folders.add(sub.parent)
                        sub_count += 1
                    except Exception as sub_ex:
                        log_lines.append(f"     ↳ subtitle ERROR: {sub.name} — {sub_ex}")

            except Exception as ex:
                e["status"] = "error"; e["error_msg"] = str(ex)
                log_lines.append(f"\n  ✗  {src.name}\n     ERROR: {ex}")
                errors += 1

        # ── Clean up empty source folders (Move mode only) ─────────────────
        removed_folders = []
        if not copy_mode:
            dest_root_path = Path(dest_root) if dest_root else None

            # Protect any folder whose parent is NOT also in src_folders
            # (i.e. the top-level folder the user loaded from).
            protected = set()
            for folder in src_folders:
                if folder.parent not in src_folders:
                    protected.add(folder)

            # Sort deepest first so children are removed before parents
            for folder in sorted(src_folders, key=lambda p: len(p.parts), reverse=True):
                if folder in protected:
                    continue  # Never delete the root source folder(s)
                if dest_root_path and folder == dest_root_path:
                    continue  # Never delete the destination root
                try_remove_empty_folder(folder)
                if not folder.exists():
                    removed_folders.append(folder)
                    log_lines.append(f"\n  🗑  Removed empty folder: {folder}")

        # ── Save history entries to config ──
        import datetime
        tab_type = "TV" if isinstance(self, TVTab) else "Movie"
        new_history = []
        for e in ready:
            if e["status"] == "renamed":
                new_history.append({
                    "type":      tab_type,
                    "original":  e.get("_orig_name", e["path"].name),
                    "renamed":   e["new_name"],
                    "dest":      str(e["path"].parent),
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
        if new_history:
            cfg = load_config()
            history = cfg.get("history", [])
            history = new_history + history   # newest first
            history = history[:2000]           # cap at 2000 entries
            save_config({"history": history})

        self._refresh(); self._summary()
        op_done = "copied" if copy_mode else "renamed"
        status = f"Done — {renamed} {op_done}"
        if sub_count:  status += f", {sub_count} subtitle(s)"
        if errors:     status += f", {errors} error(s)"
        if removed_folders: status += f", {len(removed_folders)} empty folder(s) deleted"
        self.app.set_status(status)
        self._log(f"{'Copy' if copy_mode else 'Rename'} Complete", "\n".join(log_lines))

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
        self._dest_var_ref = StringVar(value=_tv_dest)
        super().__init__(parent, app, self._dest_var_ref, ACCENT)
        # Save whenever the destination changes
        self._dest_var_ref.trace_add("write",
            lambda *_: save_config({"tv_dest": self._dest_var_ref.get().strip()}))

    def _toolbar(self, p):
        super()._toolbar(p)
        Label(p, text="Lookup via TV Maze", font=("Segoe UI", 8),
              fg=MUTED, bg=BG_PANEL).pack(side=RIGHT, padx=14)

    def _lookup_label(self): return "🔍  Lookup Episodes"
    def _parse(self, f):     return parse_tv_filename(f)
    def _subfolder(self, e): return safe_name(e["parsed"]["show_name"]) if e.get("parsed") else ""

    def _do_lookup(self, entry):
        p = entry["parsed"]
        # Try exact single-search first; fall back to multi-search picker
        results = tvmaze_search_shows(p["show_name"])
        if not results:
            raise LookupNotFoundError(
                f"Show not found: '{p['show_name']}'", p["show_name"])
        # Use top result — if confidence is low (name differs a lot), show picker
        top  = results[0]
        name_match = top["name"].lower().strip()
        query_norm = p["show_name"].lower().strip()
        if name_match != query_norm and len(results) > 1:
            raise LookupNotFoundError(
                f"Multiple matches for '{p['show_name']}'", p["show_name"])
        self._finish_tv_lookup(entry, top["id"], top["name"])

    def _finish_tv_lookup(self, entry, show_id: int, show_name: str):
        p  = entry["parsed"]
        ep = tvmaze_get_episode_by_id(show_id, p["season"], p["episode"])
        media = get_media_info(entry["path"])
        entry["media_info"] = media
        # Update parsed show name to the confirmed TVmaze name
        p["show_name"] = show_name
        entry["new_name"] = build_tv_name(p, ep["name"], media,
            self.opt_resolution.get(), self.opt_video_codec.get(), self.opt_audio_codec.get())
        entry["status"] = "done"
        # Scan for subtitle siblings and pre-compute their new names
        subs = find_subtitle_siblings(entry["path"])
        entry["subtitles"] = [
            {"path": s, "new_name": build_subtitle_name(entry["new_name"], s)}
            for s in subs
        ]

    def _show_picker(self, entry, query: str):
        def search_fn(q):
            return tvmaze_search_shows(q)
        dlg = SearchPickerDialog(
            self.app, "TV Show Not Found — Pick a Match",
            entry["path"].name, query, search_fn, self.color)
        return dlg

    def _do_lookup_with_choice(self, entry, choice: dict):
        self._finish_tv_lookup(entry, choice["id"], choice["name"])

    def _update_preview(self):
        parts = ["Show Name - S01E01 - Episode Title"]
        if self.opt_resolution.get():  parts.append("1080p")
        if self.opt_video_codec.get(): parts.append("HEVC")
        if self.opt_audio_codec.get(): parts.append("5.1")
        self.preview_label.config(text=" - ".join(parts)+".mkv")
        # Update apply button label to reflect current mode
        try:
            lbl = "⎘  Copy & Rename" if self.opt_copy_mode.get() else "✓  Apply & Rename"
            self.apply_btn.configure(text=lbl)
        except Exception:
            pass


# ── Movies Tab ────────────────────────────────────────────────────────────────
class MoviesTab(BaseTab):
    def __init__(self, parent, app):
        _movie_dest = load_config().get("movie_dest", "")
        self._dest_var_ref = StringVar(value=_movie_dest)
        super().__init__(parent, app, self._dest_var_ref, ACCENT_BLUE)
        # Save whenever the destination changes
        self._dest_var_ref.trace_add("write",
            lambda *_: save_config({"movie_dest": self._dest_var_ref.get().strip()}))
        self._inject_api_bar()

    def _inject_api_bar(self):
        """Add OMDb API key bar at the very top of the tab."""
        bar = Frame(self, bg=BG_PANEL)
        # Place it before the first child (toolbar)
        bar.pack(fill=X, before=self.winfo_children()[0])
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

        # Save key to config whenever it changes
        self.api_key_var.trace_add("write",
            lambda *_: save_config({"omdb_api_key": self.api_key_var.get().strip()}))

        link = Label(row, text="  Get a free key at omdbapi.com/apikey.aspx",
                     font=("Segoe UI", 8), fg=BLUE, bg=BG_PANEL,
                     cursor="hand2")
        link.pack(side=LEFT)
        link.bind("<Button-1>", lambda e: __import__("webbrowser").open(
            "http://www.omdbapi.com/apikey.aspx"))
        link.bind("<Enter>", lambda e: link.configure(fg=WHITE,
            font=("Segoe UI", 8, "underline")))
        link.bind("<Leave>", lambda e: link.configure(fg=BLUE,
            font=("Segoe UI", 8)))

    def _lookup_label(self): return "🔍  Lookup Movies"
    def _parse(self, f):     return parse_movie_filename(f)

    def _subfolder(self, e):
        # Movies drop directly into the destination — no subfolder
        return ""

    def _do_lookup(self, entry):
        key = self.api_key_var.get().strip()
        if not key:
            raise ValueError("Enter your OMDb API key at the top of the Movies tab")
        p       = entry["parsed"]
        results = omdb_search_movies(p["raw_title"], p.get("year"), key)
        if not results:
            raise LookupNotFoundError(
                f"Movie not found: '{p['raw_title']}'", p["raw_title"])
        top = results[0]
        # If year doesn't match or multiple plausible results, show picker
        if p.get("year") and top["year"] != str(p["year"]) and len(results) > 1:
            raise LookupNotFoundError(
                f"Multiple matches for '{p['raw_title']}'", p["raw_title"])
        # Fetch full details to confirm title
        full = omdb_get_movie(top["id"], key)
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
        # Scan for subtitle siblings and pre-compute their new names
        subs = find_subtitle_siblings(entry["path"])
        entry["subtitles"] = [
            {"path": s, "new_name": build_subtitle_name(entry["new_name"], s)}
            for s in subs
        ]

    def _show_picker(self, entry, query: str):
        key = self.api_key_var.get().strip()
        def search_fn(q):
            return omdb_search_movies(q, None, key)
        dlg = SearchPickerDialog(
            self.app, "Movie Not Found — Pick a Match",
            entry["path"].name, query, search_fn, self.color)
        return dlg

    def _do_lookup_with_choice(self, entry, choice: dict):
        key  = self.api_key_var.get().strip()
        full = omdb_get_movie(choice["id"], key) if choice.get("id") else choice
        self._finish_movie_lookup(entry, full)

    def _update_preview(self):
        parts = ["Movie Title (2024)"]
        if self.opt_resolution.get():  parts.append("1080p")
        if self.opt_video_codec.get(): parts.append("HEVC")
        if self.opt_audio_codec.get(): parts.append("5.1")
        self.preview_label.config(text=" - ".join(parts)+".mkv")
        # Update apply button label to reflect current mode
        try:
            lbl = "⎘  Copy & Rename" if self.opt_copy_mode.get() else "✓  Apply & Rename"
            self.apply_btn.configure(text=lbl)
        except Exception:
            pass


# ── History Dialog ───────────────────────────────────────────────────────────
class HistoryDialog(Toplevel):
    """Shows all renamed TV and Movie files from the saved history."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Rename History")
        self.geometry("980x620")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.grab_set()
        self._filter_var = StringVar()
        self._type_var   = StringVar(value="All")
        self._all        = load_config().get("history", [])
        self._build()
        self._render(self._all)

    def _build(self):
        # Header
        hdr = Frame(self, bg=BG_PANEL, height=52)
        hdr.pack(fill=X); hdr.pack_propagate(False)
        Frame(hdr, bg=ACCENT, width=4).pack(side=LEFT, fill=Y)
        Label(hdr, text="Rename History", font=("Segoe UI",13,"bold"),
              fg=ACCENT, bg=BG_PANEL).pack(side=LEFT, padx=14)
        Label(hdr, text=f"  {len(self._all)} total entries",
              font=FONT_SMALL, fg=MUTED, bg=BG_PANEL).pack(side=LEFT, pady=(6,0))

        # Clear history button (right side of header)
        clr = Label(hdr, text="🗑 Clear History", font=FONT_SMALL,
                    fg=ERROR, bg=BG_PANEL, cursor="hand2", padx=14)
        clr.pack(side=RIGHT)
        clr.bind("<Button-1>", lambda e: self._clear_history())

        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Filter bar
        fb = Frame(self, bg=BG_PANEL, height=40)
        fb.pack(fill=X); fb.pack_propagate(False)

        # Search box
        sf = Frame(fb, bg=BG_SURFACE, bd=0, highlightthickness=1,
                   highlightbackground=BORDER)
        sf.pack(side=LEFT, padx=12, pady=6, fill=X, expand=True)
        Label(sf, text="🔍", font=FONT_SMALL, fg=MUTED,
              bg=BG_SURFACE, padx=6).pack(side=LEFT)
        Entry(sf, textvariable=self._filter_var, font=FONT_MONO_SM,
              bg=BG_SURFACE, fg=TEXT, bd=0, insertbackground=ACCENT,
              highlightthickness=0).pack(side=LEFT, fill=X, expand=True, padx=(0,6), pady=4)
        self._filter_var.trace_add("write", lambda *_: self._apply_filter())

        # Type filter
        for label in ("All", "TV", "Movie"):
            btn = Label(fb, text=label, font=FONT_SMALL,
                        fg=ACCENT if label=="All" else MUTED,
                        bg=BG_PANEL, cursor="hand2", padx=10)
            btn.pack(side=LEFT, pady=8)
            btn.bind("<Button-1>", lambda e, l=label, b=btn: self._set_type(l))
        self._type_btns = {c.cget("text"): c for c in fb.winfo_children()
                           if isinstance(c, Label)}

        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Column headers
        ch = Frame(self, bg=BG_PANEL, height=30)
        ch.pack(fill=X); ch.pack_propagate(False)
        for text, x, w in [("TYPE",8,50),("ORIGINAL FILENAME",66,380),
                            ("RENAMED TO",454,380),("DATE",842,100)]:
            Label(ch, text=text, font=FONT_SMALL, fg=MUTED,
                  bg=BG_PANEL, anchor=W).place(x=x, y=7, width=w)
        Frame(self, bg=BORDER, height=1).pack(fill=X)

        # Scrollable list
        lf = Frame(self, bg=BG_DARK)
        lf.pack(fill=BOTH, expand=True)
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

        # Status / count bar
        Frame(self, bg=BORDER, height=1).pack(fill=X)
        bot = Frame(self, bg=BG_PANEL, height=30)
        bot.pack(fill=X, side=BOTTOM); bot.pack_propagate(False)
        self._count_lbl = Label(bot, text="", font=FONT_SMALL,
                                 fg=TEXT_DIM, bg=BG_PANEL, anchor=W, padx=12)
        self._count_lbl.pack(side=LEFT, fill=Y)
        Label(bot, text="Close", font=FONT_SMALL, fg=MUTED,
              bg=BG_PANEL, cursor="hand2", padx=16).pack(side=RIGHT)
        bot.winfo_children()[-1].bind("<Button-1>", lambda e: self.destroy())

    def _set_type(self, label: str):
        self._type_var.set(label)
        # Update button colours
        for txt, btn in self._type_btns.items():
            btn.configure(fg=ACCENT if txt==label else MUTED)
        self._apply_filter()

    def _apply_filter(self):
        q    = self._filter_var.get().lower()
        kind = self._type_var.get()
        filtered = [h for h in self._all
                    if (kind == "All" or h.get("type","") == kind)
                    and (not q or q in h.get("original","").lower()
                              or q in h.get("renamed","").lower())]
        self._render(filtered)

    def _render(self, entries: list):
        for w in self._inner.winfo_children():
            w.destroy()

        if not entries:
            Label(self._inner, text="No history entries found",
                  font=FONT_SMALL, fg=MUTED, bg=BG_DARK).pack(pady=40)
            self._count_lbl.config(text="0 entries")
            return

        for i, h in enumerate(entries):
            bg   = BG_ROW if i%2==0 else BG_ROW_ALT
            row  = Frame(self._inner, bg=bg, height=34)
            row.pack(fill=X); row.pack_propagate(False)

            kind  = h.get("type","?")
            color = ACCENT if kind=="TV" else ACCENT_BLUE
            Label(row, text=kind, font=("Segoe UI",8,"bold"),
                  fg=color, bg=bg, width=5, anchor=W).place(x=8, y=9)

            orig = h.get("original","")
            Label(row, text=orig, font=FONT_MONO_SM, fg=TEXT_DIM,
                  bg=bg, anchor=W).place(x=66, y=9, width=380)

            new = h.get("renamed","")
            Label(row, text=new, font=FONT_MONO_SM, fg=SUCCESS,
                  bg=bg, anchor=W).place(x=454, y=9, width=380)

            ts = h.get("timestamp","")
            Label(row, text=ts, font=("Segoe UI",8),
                  fg=MUTED, bg=bg, anchor=W).place(x=842, y=10, width=120)

            Frame(self._inner, bg=BORDER, height=1).pack(fill=X)

        self._count_lbl.config(text=f"  {len(entries)} entr{'y' if len(entries)==1 else 'ies'}")
        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _clear_history(self):
        if messagebox.askyesno("Clear History",
                "Delete all rename history?\nThis cannot be undone.", parent=self):
            save_config({"history": []})
            self._all = []
            self._render([])
            self._count_lbl.config(text="  0 entries")


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
        self._build()

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
