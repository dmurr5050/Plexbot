# 🎬 PlexBot v1.06
**Automatic Media File Renamer for Plex**  
*Powered by DAT — Dans Automation Tools*

> Stop renaming files by hand. PlexBot does it in seconds.  
> Tested with 4,000+ files renamed in a single session.

---

## What is PlexBot?

PlexBot is a desktop application that takes your messy downloaded video filenames and automatically renames them into clean, Plex-compatible formats. It looks up episode titles and movie names from multiple online databases, optionally tags files with resolution and codec info, organises them into the correct folder structure, moves them to your Plex library, and handles subtitle files alongside the video — all running in parallel so large batches complete fast.

---

## Features

| Feature | Details |
|---|---|
| 📺 TV Show renaming | Looks up episode titles via **TVmaze** or **TheTVDB** |
| 🎬 Movie renaming | Looks up titles and years via **OMDb** or **TheTVDB** |
| 🔤 Subtitle renaming | Renames and moves `.srt`, `.ass`, `.vtt` and more, preserving language tags |
| 🏷️ Media tags | Optionally appends resolution, video codec, and audio channels to filenames |
| 📁 Drag and drop | Drop files or whole folders directly onto the app |
| 🔁 Recursive scan | Scans all subfolders automatically |
| ⚡ Parallel lookups | Configurable 5–30 concurrent threads for lookups and renames |
| 🎯 Smart grouping | TV: one show-search per unique show. Movies: one search per unique title |
| 🔍 Smart picker | Centred search dialog when auto-match isn't confident |
| 🖱️ Right-click menu | Manual search or retry lookup on any file |
| 📋 Rename history | Instant-open even with 4,000+ entries (virtual rendering) |
| 💾 Saved settings | All preferences remembered between sessions |
| 🧹 Folder cleanup | Removes junk sidecar files and empty folders |
| ✂️ Move or Copy mode | Move files or keep originals and make a renamed copy |
| ❓ In-app Help | Full documentation embedded — no internet needed |

---

## How It Works

### TV Shows

Input:
```
Band.of.Brothers.S01E01.720p.mkv
```

Output folder structure:
```
TV Shows\
  └── Band of Brothers (2001)\
        └── Season 01\
              ├── Band of Brothers (2001) - S01E01 - Currahee - 1080p - HEVC - 5.1.mkv
              └── Band of Brothers (2001) - S01E01 - Currahee.en.srt
```

**Smart grouping:** 20 episodes of one show = 1 show search + 20 parallel episode fetches, not 20 separate searches.

### Movies

Input:
```
Inception.2010.1080p.BluRay.x264.mkv
```

Output folder structure:
```
Movies\
  └── Inception (2010)\
        ├── Inception (2010) - 1080p - H.264 - 5.1.mkv
        └── Inception (2010).en.srt
```

**Performance:** All unique titles searched in parallel. Duplicate titles (same movie, multiple files) only searched once per session. Confident matches skip the redundant detail API call.

---

## Supported File Types

**Video:** `.mkv` `.mp4` `.avi` `.mov` `.m4v` `.wmv` `.ts` `.m2ts` `.mpg` `.mpeg`

**Subtitles:** `.srt` `.sub` `.ass` `.ssa` `.vtt` `.idx` `.sup` `.pgs`

---

## Getting Started

### Option A — Run the EXE
1. Download `PlexBot.exe` and `plexbot.ico` from the Releases page — keep both in the same folder
2. Double-click to run — no installation needed

### Option B — Run from Python source
```bash
pip install requests tkinterdnd2
python plexbot.py
```
Optional: `winget install ffmpeg` — enables resolution/codec tag detection.

### Option C — Build the EXE yourself
1. Put `plexbot.py`, `plexbot.ico`, and `Build_exe.bat` in the same folder
2. Double-click `Build_exe.bat` — `PlexBot.exe` appears in ~2 minutes

---

## API Keys

| Source | Setup |
|---|---|
| TVmaze | No key needed |
| TheTVDB | Built-in key — no setup required |
| OMDb | Free key required (1,000 lookups/day) — [omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx) |

---

## Settings Panel

Click **▶ SETTINGS** in the right-hand panel to expand (collapses by default).

- **File Mode** — Move (default) or Copy & Keep Original
- **Folder Structure** — Toggle year in TV folder/filename; toggle per-movie subfolder for movies
- **Include in Filename** — Video Resolution, Video Codec, Audio Channels (each toggleable)
- **Strip year from search query** — removes years from search terms (on by default)
- **Concurrent lookups** — 5 / 10 / 15 / 20 / 25 / 30 threads (default 5) — used for both lookups and renames

---

## Performance — Large Batches

| Area | Optimisation |
|---|---|
| TV lookups | One show-search per unique show; all searches + fetches parallel |
| Movie lookups | All unique titles parallel; duplicate cache; skip redundant detail fetch |
| Lookup UI | Debounced at 100ms — stays responsive during 100+ concurrent threads |
| Rename UI | Debounced at 150ms — stays responsive during 200+ parallel renames |
| History dialog | Virtual canvas rendering — instant open with 4,000+ entries |
| Apply button | Stays disabled until full batch completes |

---

## Key Features

### Smart Lookup Picker
When auto-match isn't confident, a search dialog opens **centred over the app**. Pre-filled with the detected title — edit and search, pick from results, continue the batch.

### Right-Click Menu
Right-click any file row: 🔍 Manual Search · 🔄 Re-run Auto Lookup · ✕ Remove

### Retry Errors
After lookup, failed files stay in the list. The button shows **🔄 Retry Errors (N)**. Click to retry only failed files.

### Folder Cleanup (🧹)
Removes `.txt .idx .nfo .jpg .htm .png .url .bif`, empty subfolders, and System Volume Information. Defaults to last source folder. Scan first, then delete.

### Rename History (📋)
Every rename logged. Opens instantly with thousands of entries. Filter by All/TV/Movie, search by filename, clear when done.

### In-App Help (❓)
Full documentation embedded in the app — always available, no internet needed.

---

## Configuration

Auto-saved to `Documents\PlexBot\plexbot_config.json` — OMDb key, destinations, all settings, full history.

---

## Requirements

| Requirement | Notes |
|---|---|
| Python 3.10+ | Only if running from source |
| `requests` | `pip install requests` |
| `tkinterdnd2` | `pip install tkinterdnd2` — drag and drop |
| FFmpeg | Optional — resolution and codec tags |
| OMDb API key | Free — needed for OMDb movie lookups only |

---

## Changelog

### v1.06
- Movie lookup parallelisation — all unique titles searched in parallel (same as TV)
- Movie session cache — duplicate titles only searched once per session
- Skip redundant detail fetch when match is confident — halves API calls per movie
- History dialog: virtual canvas rendering — instant open with 4,000+ entries
- Search picker always centres over the app window
- Lookup UI debounced at 100ms — responsive at 100+ concurrent threads
- Rename UI debounced at 150ms — responsive at 200+ parallel renames
- Apply & Rename button stays disabled until full lookup batch completes

### v1.05
- Fixed Apply & Rename button enabling mid-lookup
- Suppressed CMD window flash during ffprobe calls
- Taskbar icon uses `plexbot.ico`

### v1.04
- Folder Cleanup defaults to last source folder
- Removed confirmation dialogs from Apply & Rename and Delete All

### v1.03
- Move or Copy mode
- Collapsible Settings panel
- Preview Only button removed

### v1.02
- TheTVDB support for TV Shows and Movies
- Lookup Via source selector in both tab toolbars

### v1.01
- Strip year from search query option
- Right-click context menu (Manual Search, Re-run, Remove)
- Parallel lookups — 5–30 configurable threads
- TV folder structure with year and Season subfolders
- Movie per-title subfolders
- Retry Errors — lookup button shows count, retries only failures
- Folder Cleanup tool (🧹)
- In-app Help (❓) — embedded documentation
- Rename on background thread — no UI freeze
- Live flicker-free UI updates during lookup
- Auto-scroll to active lookup row
- Successful renames removed from list immediately

### v1.0 — Initial Release
- TV renaming via TVmaze, Movie renaming via OMDb
- Subtitle auto-detection and renaming
- Media tags, drag and drop, recursive scanning
- Smart picker, rename history, PyInstaller EXE build

---

## Support

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-FFD700?style=for-the-badge&logo=paypal&logoColor=black)](https://www.paypal.com/donate/?hosted_button_id=6QVE3GP6SD8ZQ)

**Contact:** click **✉ Contact** in the app, or email **DMurr5050@gmail.com**

*PlexBot is not affiliated with Plex Inc., TVmaze, OMDb, or TheTVDB.*
