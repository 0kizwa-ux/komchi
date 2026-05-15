@echo off
cd /d "%~dp0"
py -3 komchi_app.py
if errorlevel 1 python komchi_app.py
pause
