# 🎬 PlexBot v1.09
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
| 🎬 Movie renaming | Looks up titles and years via **OMDb**, **TheTVDB**, or **TMDb** |
| 🔤 Subtitle renaming | Same-folder subs and Subs/Subtitles subfolder subs, with language tag detection |
| 🏷️ Media tags | Optionally appends resolution, video codec, and audio channels |
| 🧹 Auto-cleanup | Removes junk sidecar files from source after move — toggleable, on by default |
| 🎨 Source brand icons | Brand icons on source pills and the Lookup button |
| ⬆️ Auto-update | Checks GitHub on startup; one-click download and install |
| 📁 Drag and drop | Drop files or whole folders directly onto the app |
| 🔁 Recursive scan | Scans all subfolders automatically |
| ⚡ Parallel lookups | Configurable 5–30 concurrent threads |
| 🎯 Smart grouping | TV: one show-search per unique show. Movies: one search per unique title |
| 🔍 Smart picker | Centred search dialog when auto-match isn't confident |
| 🖱️ Right-click menu | Manual search or retry on any file |
| 📋 Rename history | Instant-open with 4,000+ entries (virtual rendering) |
| 💾 Saved settings | All preferences remembered between sessions |
| ✂️ Move or Copy mode | Move files or keep originals and make a renamed copy |
| ❓ In-app Help | Full documentation embedded — no internet needed |

---

## How It Works

### TV Shows

```
Band.of.Brothers.S01E01.720p.mkv
  →  TV Shows\Band of Brothers (2001)\Season 01\Band of Brothers (2001) - S01E01 - Currahee - 1080p - HEVC - 5.1.mkv
```

**Smart grouping:** 20 episodes of one show = 1 show search + 20 parallel episode fetches.

### Movies

```
Inception.2010.1080p.BluRay.x264.mkv
  →  Movies\Inception (2010)\Inception (2010) - 1080p - H.264 - 5.1.mkv
```

**Performance:** All unique titles searched in parallel. Duplicate titles only searched once. Confident matches skip the redundant detail API call.

---

## Subtitle Detection

PlexBot finds subtitles in **two locations**:

1. **Same folder as the video** — any subtitle whose filename starts with the video stem. Language tags (`.en`, `.fr`, `.sdh`, `.forced`) are preserved automatically.

2. **Subtitle subfolders** — checks for any folder named `Subs`, `Subtitles`, `Sub`, or `Subtitle` (any capitalisation) inside the video's directory. All subtitle files found there are included. Language is detected from the filename — `English.srt` → `.en.srt`, `French.forced.srt` → `.fr.forced.srt`.

All subtitles are moved alongside the renamed video to the destination folder.

---

## Settings Panel

Click **▶ SETTINGS** in the right-hand panel to expand.

### File Mode
| Mode | Behaviour |
|---|---|
| **✂ Move** | File is moved and renamed. Original is removed. *(default)* |
| **⎘ Copy & Keep Original** | Renamed copy made at destination. Original kept. |

### Post-Rename Cleanup
**Auto-clean junk files after move** — on by default.

After a successful Move, automatically removes junk sidecar files (`.nfo`, `.jpg`, `.txt`, `.idx`, `.htm`, `.png`, `.url`, `.bif`) from the source folder. Also removes empty `Subs`/`Subtitles` subfolders and the source folder itself if empty.

- Grayed out and inactive when **Copy** mode is selected
- Only runs when a destination folder is set (i.e. files are moving to a different location)
- Each deletion is safe — errors are silently skipped, never affects the rename

### Folder Structure
- **TV Shows** — "Include year in show folder & filename" → `Show Name (YYYY) / Season 01 / ...` — on by default
- **Movies** — "Create per-movie subfolder" → `Movie Title (YYYY) / ...` — on by default

### Include in Filename
Toggle each independently: Video Resolution · Video Codec · Audio Channels

### Search Options
- **Strip year from search query** — removes years from search terms (on by default)
- **Concurrent lookups** — 5/10/15/20/25/30 threads (default 5), used for both lookups and renames

---

## Lookup Sources

| Tab | Sources |
|---|---|
| 📺 TV Shows | TVmaze *(default)* · TheTVDB |
| 🎬 Movies | OMDb *(default)* · TheTVDB · TMDb |

| Source | Setup |
|---|---|
| TVmaze | No key needed |
| TheTVDB | Built-in key — no setup |
| OMDb | Free key required — [omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx) |
| TMDb | Built-in token — no setup. Excellent coverage. |

---

## Auto-Update

PlexBot checks GitHub 3 seconds after launch (background thread — zero startup delay).

- Green banner appears below the header if an update is available
- **Source users (.py):** one-click download, replace, and restart
- **EXE users:** opens the GitHub Releases page
- Hosted at [github.com/dmurr5050/Plexbot](https://github.com/dmurr5050/Plexbot)

---

## Performance — Large Batches

| Area | Optimisation |
|---|---|
| TV lookups | One show-search per unique show; all parallel |
| Movie lookups | All unique titles parallel; session cache; skip redundant fetch |
| Lookup UI | Debounced at 100ms |
| Rename UI | Debounced at 150ms |
| History dialog | Virtual canvas — instant with 4,000+ entries |

---

## Supported File Types

**Video:** `.mkv` `.mp4` `.avi` `.mov` `.m4v` `.wmv` `.ts` `.m2ts` `.mpg` `.mpeg`  
**Subtitles:** `.srt` `.sub` `.ass` `.ssa` `.vtt` `.idx` `.sup` `.pgs`

---

## Getting Started

### Option A — Run the EXE
Download `PlexBot.exe` and `plexbot.ico` from [Releases](https://github.com/dmurr5050/Plexbot/releases) — keep both in the same folder.

### Option B — Run from Python source
```bash
pip install requests tkinterdnd2
python plexbot.py
```
Optional: `winget install ffmpeg` for resolution/codec tags.

### Option C — Build the EXE yourself
Put `plexbot.py`, `plexbot.ico`, and `Build_exe.bat` in the same folder. Double-click `Build_exe.bat`.

---

## Configuration

Auto-saved to `Documents\PlexBot\plexbot_config.json`

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

### v1.09
- **Auto-cleanup setting** — "Auto-clean junk files after move" checkbox added to Settings panel under new POST-RENAME CLEANUP section
- On by default; grayed out automatically when Copy mode is selected
- **Subtitle subfolder detection** — PlexBot now also searches `Subs`, `Subtitles`, `Sub`, and `Subtitle` subfolders for subtitle files
- Language detection for subfolder subs: `English.srt` → `.en.srt`, `French.forced.srt` → `.fr.forced.srt`

### v1.08
- Auto-update system — checks GitHub on startup, green banner when update available
- One-click download and install for source users; opens Releases page for EXE users
- Hosted at github.com/dmurr5050/Plexbot

### v1.07
- Source brand icons on selector pills and Lookup button (updates live)
- Fixed infinite recursion crash in lookup button proxy

### v1.06
- TMDb added as a movie lookup source
- Movie lookup parallelisation and session cache
- History dialog virtual canvas rendering — instant with 4,000+ entries
- Search picker always centres over the app window
- Debounced lookup and rename UI updates

### v1.05
- Fixed Apply & Rename enabling mid-lookup
- Taskbar icon uses `plexbot.ico`

### v1.04
- Folder Cleanup defaults to last source folder

### v1.03
- Move or Copy mode; collapsible Settings panel

### v1.02
- TheTVDB support; Lookup Via source selector

### v1.01
- Strip year; right-click menu; parallel lookups; TV/movie folder structure
- Retry Errors; Folder Cleanup; In-app Help; background rename thread

### v1.0 — Initial Release
- TV via TVmaze, Movie via OMDb, subtitle auto-detection, media tags, drag and drop

---

## Support

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-FFD700?style=for-the-badge&logo=paypal&logoColor=black)](https://www.paypal.com/donate/?hosted_button_id=6QVE3GP6SD8ZQ)

**Contact:** click **✉ Contact** in the app, or email **DMurr5050@gmail.com**

*PlexBot is not affiliated with Plex Inc., TVmaze, OMDb, TheTVDB, or TMDb.*
