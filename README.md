🎬 PlexBot v1.0
Automatic Media File Renamer for Plex
Powered by DAT — Dans Automation Tools


Stop renaming files by hand. PlexBot does it in seconds.


<img width="1095" height="788" alt="image" src="https://github.com/user-attachments/assets/9666877b-9323-46c1-b1fb-b97433556f9e" />


What is PlexBot?
PlexBot is a FileBot-style desktop application that takes your messy downloaded video filenames and automatically renames them into clean, Plex-compatible formats. It looks up episode titles and movie names from online databases, optionally tags files with resolution and codec info, moves them to your Plex library folders, and handles subtitle files alongside the video — all with a live preview before anything is changed.



Features at a Glance
FeatureDetails📺 TV Show renamingLooks up episode titles via TVmaze🎬 Movie renamingLooks up titles and years via OMDb🔤 Subtitle renamingRenames and moves .srt, .ass, .vtt and more alongside the video🏷️ Media tagsOptionally appends resolution, video codec, and audio channels to filenames📁 Drag and dropDrop files or whole folders directly onto the app🔁 Recursive scanScans all subfolders automatically👁️ Dry run previewSee exactly what will change before applying anything🔍 Smart pickerA search dialog lets you pick the right match when results are ambiguous📋 Rename historyEvery rename is logged and searchable💾 Saved settingsDestination folders and API key remembered between sessions🗑️ Empty folder cleanupRemoves leftover empty folders after moving files out

How It Works
TV Shows Tab
PlexBot reads the filename and extracts the show name, season, and episode number from patterns like:
Happys.Place.S02E13.1080p.HEVC.x265-MeGusta.mkv
It queries TVmaze for the episode title and renames the file to:
Happy's Place - S02E13 - A New Chapter - 1080p - HEVC - 5.1.mkv
Files are moved into a subfolder named after the show inside your chosen destination:
D:\Plex Library\TV Shows\
  └── Happy's Place\
        ├── Happy's Place - S02E13 - A New Chapter - 1080p - HEVC - 5.1.mkv
        └── Happy's Place - S02E13 - A New Chapter.en.srt
Movies Tab
PlexBot extracts the movie title and year from filenames like:
Inception.2010.1080p.BluRay.x264.mkv
The.Matrix.1999.REMASTERED.mkv
It queries OMDb to confirm the exact title and release year, then renames to:
Inception (2010) - 1080p - H.264 - 5.1.mkv
Movies are placed directly in your destination folder with no subfolder.

Output Format
TV Shows
Show Name - S01E02 - Episode Title - 1080p - HEVC - 5.1.mkv
Show Name - S01E02 - Episode Title.en.srt
Show Name - S01E02 - Episode Title.fr.srt
Movies
Movie Title (2024) - 1080p - HEVC - 5.1.mkv
Movie Title (2024).en.srt
The resolution, video codec, and audio channels tags are each individually toggleable via checkboxes in the app. Turn off any you do not need.

Supported File Types
Video
.mkv .mp4 .avi .mov .m4v .wmv .ts .m2ts .mpg .mpeg
Subtitles
.srt .sub .ass .ssa .vtt .idx .sup .pgs

Getting Started

Go to the Releases page
Download PlexBot.exe
Double-click to run — no installation needed

Option A — Run from Python source
Requirements: Python 3.10 or newer
bashpip install requests tkinterdnd2
python plexbot.py
Optional but recommended: Install FFmpeg to enable resolution and codec detection. On Windows you can run winget install ffmpeg. Without it the app still renames files correctly, just without the technical tags.

Option B — Build the EXE yourself

Put plexbot.py, plexbot.ico, and build_exe.bat in the same folder
Double-click build_exe.bat
Wait 1 to 3 minutes — PlexBot.exe appears in the same folder, ready to use or share


API Keys
PlexBot uses two free online databases:
TVmaze — TV Shows
No API key required. TVmaze is a free, public API and works straight away.
OMDb — Movies
A free API key is required (1,000 lookups per day on the free tier).

Go to omdbapi.com/apikey.aspx
Select the Free tier and enter your email address
Your key arrives by email almost immediately
Open PlexBot, go to the Movies tab, and paste the key into the OMDB API KEY field at the top

The key is saved automatically and reloaded every time the app opens. You only need to enter it once.

Configuration
PlexBot saves all settings automatically to:
C:\Users\YourName\Documents\PlexBot\plexbot_config.json
This file stores:

Your OMDb API key
TV Shows destination folder
Movies destination folder
Full rename history

The folder and file are created automatically on first run. Destination fields start blank and are saved the moment you select a folder.

Rename History
Every file renamed by PlexBot is recorded in the history log. Click the History button in the top-right corner of the app to open the history window, where you can:

See the original filename and the new Plex-formatted name side by side
Filter by All, TV, or Movie
Search by any part of the filename
Clear the full history when you no longer need it


Smart Lookup Picker
When PlexBot cannot confidently match a filename to a single result, it pauses and opens a search dialog so you can choose:

A pre-filled search box with the detected title, ready to edit
A scrollable list of matches from TVmaze or OMDb showing title, year, and description
Click any result to select it, then confirm
The rest of the batch continues processing after you confirm or skip


Requirements Summary
RequirementNotesPython 3.10+Only needed if running from sourcerequestspip install requeststkinterdnd2pip install tkinterdnd2 — enables drag and drop supportFFmpegOptional — enables resolution and codec tag detectionOMDb API keyFree at omdbapi.com — needed for movie lookups only

Changelog
v1.0 — Initial Release

TV show renaming via TVmaze
Movie renaming via OMDb
Subtitle auto-detection, rename, and move with language tag preservation
Media tags: resolution, video codec, audio channels — each independently toggleable
Drag and drop support
Recursive folder scanning from Add Files dialog and Add Folder button
Smart lookup picker for ambiguous or unmatched files
Dry run preview before applying any renames
Rename history with search and type filter
OMDb API key and destination folders saved to Documents\PlexBot\
Destination fields start blank and are remembered after first use
Empty subfolder cleanup after moving files — root source folders are always protected
Single-file Windows EXE build via PyInstaller


Support the Project
If PlexBot saves you time, a small donation is always appreciated and helps keep the project going.
Show Image

Contact
Questions, bug reports, and feature ideas are welcome.
Click the Contact button inside the app to copy the email address to your clipboard, or write to DMurr5050@gmail.com directly.

Disclaimer
PlexBot is an independent open-source project and is not affiliated with, endorsed by, or connected to Plex Inc., TVmaze, or OMDb in any way.
