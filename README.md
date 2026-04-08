# 🎬 PlexBot v1.08
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
| 🔤 Subtitle renaming | Renames and moves `.srt`, `.ass`, `.vtt` and more, preserving language tags |
| 🏷️ Media tags | Optionally appends resolution, video codec, and audio channels to filenames |
| 🎨 Source brand icons | Brand icons on source pills and the Lookup button — updates live |
| ⬆️ Auto-update | Checks GitHub on startup; downloads and installs updates in one click |
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

Output:
```
TV Shows\
  └── Band of Brothers (2001)\
        └── Season 01\
              ├── Band of Brothers (2001) - S01E01 - Currahee - 1080p - HEVC - 5.1.mkv
              └── Band of Brothers (2001) - S01E01 - Currahee.en.srt
```

**Smart grouping:** 20 episodes of one show = 1 show search + 20 parallel episode fetches.

### Movies

Input:
```
Inception.2010.1080p.BluRay.x264.mkv
```

Output:
```
Movies\
  └── Inception (2010)\
        ├── Inception (2010) - 1080p - H.264 - 5.1.mkv
        └── Inception (2010).en.srt
```

**Performance:** All unique titles searched in parallel. Duplicate titles only searched once per session. Confident matches skip the redundant detail API call.

---

## Lookup Sources

Both tabs show brand icons on the **LOOKUP VIA** source selector pills and on the **Lookup button** itself — the icon updates live when you switch sources.

| Tab | Sources |
|---|---|
| 📺 TV Shows | TVmaze *(default)* · TheTVDB |
| 🎬 Movies | OMDb *(default)* · TheTVDB · TMDb |

| Source | Setup |
|---|---|
| TVmaze | No key needed — works immediately |
| TheTVDB | Built-in key — no setup |
| OMDb | Free key required — [omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx) |
| TMDb | Built-in token — no setup. Excellent coverage. |

---

## Auto-Update

PlexBot checks GitHub for a newer version automatically on every startup.

- The check runs in a **background thread** — no delay to launch
- If a newer version is found, a **green banner** appears below the header
- Click the banner to open the Update dialog
- Click **✕** on the banner to dismiss it

**Running from source (.py):** PlexBot downloads the new `plexbot.py`, verifies it, replaces the current file, and offers to restart automatically via one click.

**Running as PlexBot.exe:** The EXE cannot self-replace. Clicking the banner opens the GitHub Releases page so you can download the new EXE.

Updates are hosted at: **[github.com/dmurr5050/Plexbot](https://github.com/dmurr5050/Plexbot)**

To push an update: bump `VERSION` in `plexbot.py`, commit and push to `main`. That's it.

---

## Settings Panel

Click **▶ SETTINGS** in the right-hand panel to expand.

- **File Mode** — Move *(default)* or Copy & Keep Original
- **Folder Structure** — Year in TV folder/filename; per-movie subfolder (both on by default)
- **Include in Filename** — Resolution, Video Codec, Audio Channels (each toggleable)
- **Strip year from search query** — removes years from search terms (on by default)
- **Concurrent lookups** — 5/10/15/20/25/30 threads (default 5), used for both lookups and renames

---

## Performance — Large Batches

| Area | Optimisation |
|---|---|
| TV lookups | One show-search per unique show; all searches + fetches parallel |
| Movie lookups | All unique titles parallel; session cache; skip redundant detail fetch |
| Lookup UI | Debounced at 100ms — stays responsive at 100+ concurrent threads |
| Rename UI | Debounced at 150ms — stays responsive at 200+ parallel renames |
| History dialog | Virtual canvas — instant open with 4,000+ entries |
| Apply button | Stays disabled until full lookup batch completes |

---

## Key Features

### Auto-Update
Checks GitHub 3 seconds after launch. Green banner appears if an update is available. One-click download and install for source users; opens Releases page for EXE users.

### Source Brand Icons
TVmaze (orange), TheTVDB (green), OMDb (gold star), TMDb (blue/teal). Icons appear on source pills and update live on the Lookup button.

### Smart Lookup Picker
Always **centres over the app window**. Pre-filled with detected title. Pick from results, continue the batch.

### Right-Click Menu
Right-click any file: 🔍 Manual Search · 🔄 Re-run Auto Lookup · ✕ Remove

### Retry Errors
After lookup the button shows **🔄 Retry Errors (N)**. Only failed files retried.

### Folder Cleanup (🧹)
Removes `.txt .idx .nfo .jpg .htm .png .url .bif`, empty folders, System Volume Information. Defaults to last source folder.

### Rename History (📋)
Virtual canvas — instant open with thousands of entries. Filter All/TV/Movie, search, clear.

### In-App Help (❓)
Full documentation embedded — always available offline.

---

## Supported File Types

**Video:** `.mkv` `.mp4` `.avi` `.mov` `.m4v` `.wmv` `.ts` `.m2ts` `.mpg` `.mpeg`  
**Subtitles:** `.srt` `.sub` `.ass` `.ssa` `.vtt` `.idx` `.sup` `.pgs`

---

## Getting Started

### Option A — Run the EXE
Download `PlexBot.exe` and `plexbot.ico` from [Releases](https://github.com/dmurr5050/Plexbot/releases) — keep both in the same folder. Double-click to run.

### Option B — Run from Python source
```bash
pip install requests tkinterdnd2
python plexbot.py
```
Optional: `winget install ffmpeg` for resolution/codec tags.

### Option C — Build the EXE yourself
Put `plexbot.py`, `plexbot.ico`, and `Build_exe.bat` in the same folder. Double-click `Build_exe.bat` — done in ~2 minutes.

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

### v1.08
- **Auto-update system** — PlexBot checks GitHub for a newer version on every startup
- Green update banner appears below the header when an update is available
- One-click download and install for source (.py) users — automatically restarts
- EXE users are directed to the GitHub Releases page
- Update check runs in background thread — zero impact on startup time
- Hosted at github.com/dmurr5050/Plexbot — push a new version to `main` to distribute

### v1.07
- Source brand icons — TVmaze, TheTVDB, OMDb, TMDb each have a branded icon on their selector pills
- Lookup button shows the icon of the currently active source; updates live when switching
- Fixed infinite recursion crash on startup caused by proxy bind loop in lookup button

### v1.06
- TMDb added as a movie lookup source — built-in token, no setup required
- Movie lookup parallelisation — all unique titles searched in parallel
- Movie session cache — duplicate titles only searched once per session
- Skip redundant detail fetch when match is confident — halves API calls
- History dialog virtual canvas rendering — instant open with 4,000+ entries
- Search picker always centres over the app window
- Lookup UI debounced at 100ms; Rename UI debounced at 150ms
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

### v1.02
- TheTVDB support for TV Shows and Movies
- Lookup Via source selector with pill buttons

### v1.01
- Strip year from search query; right-click menu; parallel lookups (5–30 threads)
- TV year-in-folder structure; movie per-title subfolders
- Retry Errors; Folder Cleanup (🧹); In-app Help (❓)
- Rename on background thread; live flicker-free UI updates

### v1.0 — Initial Release
- TV renaming via TVmaze, Movie renaming via OMDb
- Subtitle auto-detection and renaming, media tags
- Drag and drop, recursive scanning, smart picker, rename history

---

## Support

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-FFD700?style=for-the-badge&logo=paypal&logoColor=black)](https://www.paypal.com/donate/?hosted_button_id=6QVE3GP6SD8ZQ)

**Contact:** click **✉ Contact** in the app, or email **DMurr5050@gmail.com**

*PlexBot is not affiliated with Plex Inc., TVmaze, OMDb, TheTVDB, or TMDb.*
