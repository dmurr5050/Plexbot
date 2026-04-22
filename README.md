# 🎬 PlexBot v1.11
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
| 🔤 Subtitle renaming | Same-folder and subfolder subs with language tag detection |
| 🏷️ Media tags | Resolution, video codec, audio channels — each toggleable |
| 🧹 Auto-cleanup | Per-extension toggles, recurses into subfolders, smart folder protection |
| 📂 Destination history | Dropdown remembers last 10 destinations per tab |
| 🎨 Source brand icons | Brand icons on source pills and Lookup button |
| ⬆️ Auto-update | Checks GitHub on startup; one-click install |
| 📁 Drag and drop | Files or whole folders |
| 🔁 Recursive scan | All subfolders scanned automatically |
| ⚡ Parallel lookups | 5–30 configurable threads |
| 📋 Rename history | Instant-open with 4,000+ entries |
| 💾 Saved settings | All preferences persisted between sessions |
| ✂️ Move or Copy | Move files or keep originals |
| 🖱️ Scrollable settings | Right panel fully scrollable with mouse wheel |
| ❓ In-app Help | Full docs embedded — no internet needed |

---

## How It Works

### TV Shows

```
Band.of.Brothers.S01E01.720p.mkv
  →  TV Shows\Band of Brothers (2001)\Season 01\
       Band of Brothers (2001) - S01E01 - Currahee.mkv
```

### Movies

```
Inception.2010.1080p.BluRay.x264.mkv
  →  Movies\Inception (2010)\Inception (2010) - 1080p - H.264 - 5.1.mkv
```

---

## Destination Folder

The DESTINATION field is now a **dropdown** that remembers your previous selections.

- Click **▼** to open the dropdown and select a past destination instantly
- Click **…** to browse for a new folder
- Type or paste a path directly into the field
- History is saved automatically after each successful rename
- Up to **10 entries per tab** (TV and Movies have separate histories)
- Leave blank to rename files in place without moving them

---

## Subtitle Detection

PlexBot finds subtitles in **two locations**:

1. **Same folder** — subtitle stem starts with the video stem. Language tags preserved (`.en`, `.fr`, `.sdh`, `.forced`).
2. **Subtitle subfolders** — checks `Subs`, `Subtitles`, `Sub`, `Subtitle` (any case). Language detected from filename: `English.srt` → `.en.srt`, `French.forced.srt` → `.fr.forced.srt`.

---

## Settings Panel

Click **▶ SETTINGS** in the right panel to expand. The entire right panel scrolls with the mouse wheel.

### File Mode
| Mode | Behaviour |
|---|---|
| **✂ Move** *(default)* | File moved and renamed. Original removed. |
| **⎘ Copy & Keep** | Renamed copy created. Original kept. |

### Post-Rename Cleanup

Click **▶ POST-RENAME CLEANUP** to expand. The **"Enable auto-clean after move"** checkbox activates the feature.

Each file type has its own checkbox — all on by default:

| Extension | Type |
|---|---|
| `.nfo` | Metadata files |
| `.jpg` | Poster / fanart images |
| `.txt` | Text files |
| `.idx` | Subtitle index files |
| `.htm` | HTML files |
| `.png` | PNG images *(includes subfolders like `Screens/`)* |
| `.url` | Internet shortcuts |
| `.bif` | Plex trick-play files |
| Custom | Comma-separated extensions |

**Rules:**
- Only runs in **Move** mode (grayed out in Copy)
- Only runs when a **destination folder is set**
- **Recurses into all subfolders** — catches files in `Screens/`, `Extras/`, etc.
- Removes empty subfolders after cleaning

**Folder protection — the parent of what you drag is always safe:**

| You drag | Protected | Can be deleted when empty |
|---|---|---|
| Episode folder (`DMV.S01E16…`) | Its parent (`JD Downloads`) | The episode folder ✓ |
| Parent folder (`JD Downloads`) | Its parent (`Desktop`) | Episode subfolders ✓ |
| Individual files | Their containing folder | Sub-folders inside ✓ |

### Folder Structure
- **TV** — "Include year in show folder" → `Show Name (YYYY) / Season 01 / …`
- **Movies** — "Create per-movie subfolder" → `Movie Title (YYYY) / …`

### Include in Filename
Toggle independently: Video Resolution · Video Codec · Audio Channels

### Search Options
- Strip year from search query (on by default)
- Concurrent lookups: 5 / 10 / 15 / 20 / 25 / 30 threads (default 5)

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
| OMDb | Free key — [omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx) |
| TMDb | Built-in token — no setup |

---

## Auto-Update

Checks GitHub 3 seconds after launch (background — zero startup delay).

- Green banner if update available
- **Source (.py):** one-click download, replace, restart
- **EXE:** opens GitHub Releases page
- [github.com/dmurr5050/Plexbot](https://github.com/dmurr5050/Plexbot)

---

## Getting Started

**Option A — Run the EXE**  
Download `PlexBot.exe` and `plexbot.ico` from [Releases](https://github.com/dmurr5050/Plexbot/releases).

**Option B — Run from source**
```bash
pip install requests tkinterdnd2
python plexbot.py
```

**Option C — Build EXE**  
Put `plexbot.py`, `plexbot.ico`, `Build_exe.bat` in same folder → double-click `Build_exe.bat`.

**Optional:** `winget install ffmpeg` for resolution/codec tags.

---

## Requirements

| Requirement | Notes |
|---|---|
| Python 3.10+ | Source only |
| `requests` | `pip install requests` |
| `tkinterdnd2` | `pip install tkinterdnd2` |
| FFmpeg | Optional — codec/resolution tags |
| OMDb API key | Free — OMDb lookups only |

---

## Changelog

### v1.11
- **Destination dropdown** — the destination field is now a combobox that remembers the last 10 folders used per tab (TV and Movies tracked separately)
- Dropdown history saves automatically after each successful rename
- Browse (…) button adds the selected folder to history immediately
- Fully editable — type or paste any path directly

### v1.10
- Folder protection fixed — parent of dragged item is protected, not the item itself
- Auto-cleanup recurses into all subfolders (Screens/, Extras/, etc.)
- Per-file exception handling — locked files never abort the cleanup pass

### v1.09
- Post-rename cleanup expandable with per-extension checkboxes plus custom extensions
- Right panel scrollable with mouse wheel
- Subtitle subfolder detection with language name→code mapping

### v1.08
- Auto-update system with green banner and one-click install

### v1.07
- Source brand icons on pills and Lookup button

### v1.06
- TMDb source; parallel movie lookups; virtual history rendering

### v1.05
- Fixed Apply & Rename enabling mid-lookup

### v1.04
- Folder Cleanup defaults to last source folder

### v1.03
- Move/Copy mode; collapsible Settings panel

### v1.02
- TheTVDB support; Lookup Via source selector

### v1.01
- Parallel lookups; right-click menu; TV/movie folder structure

### v1.0
- Initial release

---

## Support

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-FFD700?style=for-the-badge&logo=paypal&logoColor=black)](https://www.paypal.com/donate/?hosted_button_id=6QVE3GP6SD8ZQ)

**Contact:** click **✉ Contact** in the app, or email **DMurr5050@gmail.com**

*PlexBot is not affiliated with Plex Inc., TVmaze, OMDb, TheTVDB, or TMDb.*
