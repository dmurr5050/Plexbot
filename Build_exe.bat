@echo off
:: ============================================================
::  PlexBot EXE Builder  —  DAT (Dans Automation Tools)
::  Place this file next to plexbot.py and plexbot.ico
::  then double-click to build PlexBot.exe
:: ============================================================
setlocal enabledelayedexpansion

echo.
echo  =============================================
echo   PlexBot EXE Builder  ^|  Powered by DAT
echo  =============================================
echo.

:: ── Find real Python (skip Windows Store stub) ──────────────
set PYTHON=
for /f "delims=" %%i in ('where python 2^>nul') do (
    echo %%i | findstr /i "WindowsApps" >nul
    if errorlevel 1 ( if "!PYTHON!"=="" set PYTHON=%%i )
)
if "!PYTHON!"=="" (
    echo ERROR: Python not found. Install from https://python.org
    pause & exit /b 1
)
echo  [1/4] Python  : !PYTHON!

:: ── Check required files ─────────────────────────────────────
set SCRIPT=%~dp0plexbot.py
set ICON=%~dp0plexbot.ico

if not exist "%SCRIPT%" (
    echo ERROR: plexbot.py not found next to this script.
    pause & exit /b 1
)
echo  [2/4] Script  : %SCRIPT%

if exist "%ICON%" (
    echo  [2/4] Icon    : %ICON%
    set ICON_ARG=--icon "%ICON%"
) else (
    echo  [2/4] Icon    : not found - building without icon
    set ICON_ARG=
)

:: ── Install dependencies ─────────────────────────────────────
echo  [3/4] Installing PyInstaller, requests, tkinterdnd2...
"!PYTHON!" -m pip install pyinstaller requests tkinterdnd2 --quiet
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause & exit /b 1
)
echo        Done.

:: ── Build EXE ────────────────────────────────────────────────
echo  [4/4] Building PlexBot.exe (this takes 1-3 minutes)...
echo.

"!PYTHON!" -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "PlexBot" ^
    %ICON_ARG% ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import requests ^
    --hidden-import json ^
    --hidden-import subprocess ^
    --hidden-import webbrowser ^
    --hidden-import datetime ^
    --hidden-import tkinterdnd2 ^
    --collect-all tkinterdnd2 ^
    --clean ^
    --noconfirm ^
    "%SCRIPT%"

if errorlevel 1 (
    echo.
    echo  ERROR: Build failed. See output above for details.
    pause & exit /b 1
)

:: ── Move EXE to current folder ────────────────────────────────
if exist "%~dp0dist\PlexBot.exe" (
    move /y "%~dp0dist\PlexBot.exe" "%~dp0PlexBot.exe" >nul
    echo.
    echo  =============================================
    echo   SUCCESS!
    echo   PlexBot.exe is ready in this folder.
    echo  =============================================
    echo.
    echo   - Double-click PlexBot.exe to launch
    echo   - Right-click ^> Send to ^> Desktop (shortcut)
    echo   - The icon shows the PlexBot logo
    echo.
) else (
    echo.
    echo  Build may have completed — check the dist\ folder.
    echo.
)

:: ── Clean up build artifacts ──────────────────────────────────
if exist "%~dp0dist"         rmdir /s /q "%~dp0dist"
if exist "%~dp0build"        rmdir /s /q "%~dp0build"
if exist "%~dp0PlexBot.spec" del /q "%~dp0PlexBot.spec"

pause