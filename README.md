# 🎬 PlexBot v1.07
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
| 🎨 Source brand icons | Brand icons shown on source selector pills and the Lookup button |
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

Both tabs show brand icons on the **LOOKUP VIA** source selector pills and on the **Lookup button** itself — the button icon updates to match the active source.

| Tab | Sources |
|---|---|
| 📺 TV Shows | TVmaze *(default)* · TheTVDB |
| 🎬 Movies | OMDb *(default)* · TheTVDB · TMDb |

| Source | Icon | Setup |
|---|---|---|
| TVmaze | 🟠 orange TV | No key needed — works immediately |
| TheTVDB | 🟢 green shield | Built-in key — no setup |
| OMDb | ⭐ gold star | Free key required (1,000/day) |
| TMDb | 🔵 blue/teal bar | Built-in token — no setup. Excellent coverage. |

---

## API Keys

Only OMDb requires a user-supplied key. All other sources are built-in.

**Getting an OMDb key:**
1. Go to [omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx)
2. Select the **Free** tier, enter your email
3. Key arrives almost immediately
4. Open PlexBot → Movies tab → paste into **OMDB API KEY**

The key is saved automatically — enter it once, never again.

---

## Settings Panel

Click **▶ SETTINGS** in the right-hand panel to expand.

- **File Mode** — Move *(default)* or Copy & Keep Original
- **Folder Structure** — Year in TV folder/filename; per-movie subfolder for movies (both on by default)
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

### Source Brand Icons
Each lookup source has a brand icon: TVmaze (orange), TheTVDB (green), OMDb (gold star), TMDb (blue/teal). Icons appear on the source selector pills in the toolbar and update live on the Lookup button as you switch sources.

### Smart Lookup Picker
Search dialog always **centres over the app window**. Pre-filled with the detected title. Pick from results, continue the batch.

### Right-Click Menu
Right-click any file row: 🔍 Manual Search · 🔄 Re-run Auto Lookup · ✕ Remove

### Retry Errors
After lookup, the button shows **🔄 Retry Errors (N)**. Only failed files are retried.

### Folder Cleanup (🧹)
Removes `.txt .idx .nfo .jpg .htm .png .url .bif`, empty folders, and System Volume Information. Defaults to last source folder.

### Rename History (📋)
Virtual canvas rendering — opens instantly with thousands of entries. Filter All/TV/Movie, search, clear.

### In-App Help (❓)
Full documentation embedded — always available, no internet needed.

---

## Supported File Types

**Video:** `.mkv` `.mp4` `.avi` `.mov` `.m4v` `.wmv` `.ts` `.m2ts` `.mpg` `.mpeg`  
**Subtitles:** `.srt` `.sub` `.ass` `.ssa` `.vtt` `.idx` `.sup` `.pgs`

---

## Getting Started

### Option A — Run the EXE
Download `PlexBot.exe` and `plexbot.ico` from Releases — keep both in the same folder. Double-click to run.

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

### v1.07
- **Source brand icons** — TVmaze, TheTVDB, OMDb, and TMDb each have a brand-coloured icon displayed on their selector pills
- **Lookup button icon** — the Lookup button now shows the icon of the currently selected source; updates live when you switch sources
- Icons are embedded as PNG data — no external files needed, works in the compiled EXE

### v1.06
- TMDb (The Movie Database) added as a movie lookup source — built-in token, no setup required
- Movie lookup parallelisation — all unique titles searched in parallel (same pattern as TV shows)
- Movie session cache — duplicate titles only searched once per session
- Skip redundant detail fetch — halves API calls when match is confident
- History dialog virtual canvas rendering — instant open with 4,000+ entries
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

### v1.02
- TheTVDB support for TV Shows and Movies
- Lookup Via source selector with pill buttons in both toolbars

### v1.01
- Strip year from search query option
- Right-click context menu (Manual Search, Re-run, Remove)
- Parallel lookups — 5–30 configurable threads
- TV year-in-folder structure; movie per-title subfolders
- Retry Errors — lookup button shows count, retries only failures
- Folder Cleanup tool (🧹), In-app Help (❓)
- Rename on background thread; live flicker-free UI updates

### v1.0 — Initial Release
- TV renaming via TVmaze, Movie renaming via OMDb
- Subtitle auto-detection and renaming
- Media tags, drag and drop, recursive scanning
- Smart picker, rename history, PyInstaller EXE build

---

## Support

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-FFD700?style=for-the-badge&logo=paypal&logoColor=black)](https://www.paypal.com/donate/?hosted_button_id=6QVE3GP6SD8ZQ)

**Contact:** click **✉ Contact** in the app, or email **DMurr5050@gmail.com**

*PlexBot is not affiliated with Plex Inc., TVmaze, OMDb, TheTVDB, or TMDb.*
