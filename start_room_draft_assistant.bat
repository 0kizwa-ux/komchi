@echo off
cd /d "%~dp0"
py -3 start_room_draft_assistant.py
if errorlevel 1 python start_room_draft_assistant.py
pause
