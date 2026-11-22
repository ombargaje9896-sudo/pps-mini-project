@echo off
cd /d "%~dp0"
py gui.py
if errorlevel 1 (
    echo Could not start the desktop app. Make sure Python with Tkinter is installed.
    pause
)
