# 🎬 PlexBot v1.12
**Automatic Media File Renamer for Plex**  
*Powered by DAT — Dans Automation Tools*

> Stop renaming files by hand. PlexBot does it in seconds.

---

## What is PlexBot?

PlexBot renames messy downloaded video filenames into clean, Plex-compatible formats. It looks up episode titles and movie names from multiple online databases, tags files with resolution and codec info, organises them into the correct folder structure, and handles subtitle files alongside the video — all in parallel.

---

## Features

| Feature | Details |
|---|---|
| 📺 TV Show renaming | **TVmaze** or **TheTVDB** |
| 🎬 Movie renaming | **OMDb**, **TheTVDB**, or **TMDb** |
| 🔤 Subtitle renaming | Same-folder and subfolder subs, language tag detection |
| 🏷️ Media tags | Resolution, codec, channels — toggleable |
| 🧹 Auto-cleanup | Per-extension, recurses subfolders, smart folder protection |
| 📂 Destination history | Dropdown with last 10 destinations per tab |
| ⚠️ Conflict handling | Overwrite / Skip / Overwrite All / Skip All dialog |
| ⬆️ Auto-update | Checks GitHub on startup; one-click install |
| 📁 Drag and drop | Files or whole folders |
| ⚡ Parallel lookups | 5–30 threads |
| 📋 Rename history | Instant-open at 4,000+ entries |
| 🖱️ Scrollable settings | Right panel scrolls with mouse wheel |

---

## How It Works

### TV Shows — Year Deduplication

```
Rivals.2024.S01E01.1080p.mkv  →  Rivals (2024) - S01E01 - Title.mkv
```

If the filename already contains the show year, PlexBot will not duplicate it. `Rivals.2024` becomes `Rivals (2024)`, never `Rivals (2024) (2024)`.

### Movies

```
Inception.2010.1080p.BluRay.x264.mkv
  →  Movies\Inception (2010)\Inception (2010) - 1080p - H.264 - 5.1.mkv
```

---

## File Conflict Handling

When a rename target already exists, PlexBot pauses and shows a dialog:

| Option | Behaviour |
|---|---|
| **✓ Overwrite** | Replace this file and continue |
| **✓✓ Overwrite All** | Replace this and all remaining conflicts without asking |
| **✕ Skip** | Leave this file unchanged and continue |
| **✕✕ Skip All** | Leave this and all remaining conflicts unchanged |

Skipped files are marked as errors in the list so you can see exactly what wasn't processed. This replaces the `[Errno 13] Permission denied` error that occurred when trying to overwrite an existing file.

---

## Destination Dropdown

The destination field remembers your previous selections (up to 10 per tab).

- **▼** — open dropdown and pick a past destination instantly
- **…** — browse for a new folder (adds to history)
- Type or paste any path directly
- History saves automatically after each successful rename
- TV Shows and Movies have separate histories
- Leave blank to rename in place

---

## Subtitle Detection

1. **Same folder** — subtitle stem starts with video stem, language tags preserved
2. **Subtitle subfolders** — `Subs`, `Subtitles`, `Sub`, `Subtitle` — `English.srt` → `.en.srt`

---

## Settings

**File Mode:** Move *(default)* · Copy & Keep

**Post-Rename Cleanup** *(Move mode only, destination must differ from source)*
- Per-extension checkboxes: `.nfo` `.jpg` `.txt` `.idx` `.htm` `.png` `.url` `.bif` + custom
- Recurses all subfolders — `Screens/`, `Extras/`, etc.
- Parent of what you drag is always protected from deletion

**Folder Structure:** TV year in folder · Movie per-title subfolder  
**Include in Filename:** Resolution · Video Codec · Audio Channels  
**Concurrent lookups:** 5 / 10 / 15 / 20 / 25 / 30 threads

---

## Lookup Sources

| Tab | Sources |
|---|---|
| 📺 TV Shows | TVmaze *(default)* · TheTVDB |
| 🎬 Movies | OMDb *(default)* · TheTVDB · TMDb |

OMDb requires a free key from [omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx). All others work out of the box.

---

## Getting Started

```bash
pip install requests tkinterdnd2
python plexbot.py
```

Or download `PlexBot.exe` from [Releases](https://github.com/dmurr5050/Plexbot/releases). Optional: `winget install ffmpeg` for codec tags.

---

## Changelog

### v1.12
- **Year deduplication** — show names with years in the filename (e.g. `Rivals.2024`) no longer produce doubled years like `Rivals (2024) (2024)`
- **File conflict dialog** — when a rename target already exists, a dialog offers Overwrite / Skip / Overwrite All / Skip All instead of crashing with `[Errno 13] Permission denied`
- Overwrite removes the existing file before moving to avoid OS permission errors on locked/read-only destinations

### v1.11
- Destination dropdown — remembers last 10 folders per tab, auto-saves after rename

### v1.10
- Folder protection fixed; auto-cleanup recurses all subfolders

### v1.09
- Per-extension cleanup checkboxes; scrollable right panel; subtitle subfolder detection

### v1.08
- Auto-update with green banner and one-click install

### v1.07
- Source brand icons

### v1.06
- TMDb; parallel movie lookups; virtual history rendering

### v1.0–v1.05
- Initial release through early improvements

---

## Support

[![Donate](https://img.shields.io/badge/Donate-PayPal-FFD700?style=for-the-badge&logo=paypal&logoColor=black)](https://www.paypal.com/donate/?hosted_button_id=6QVE3GP6SD8ZQ)

**Contact:** DMurr5050@gmail.com · [github.com/dmurr5050/Plexbot](https://github.com/dmurr5050/Plexbot)

*Not affiliated with Plex Inc., TVmaze, OMDb, TheTVDB, or TMDb.*
