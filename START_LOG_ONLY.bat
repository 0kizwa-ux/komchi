@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "LOG=%~dp0START_LOG.txt"
echo Komchi start log > "%LOG%"
echo Folder: %CD% >> "%LOG%"
echo Time: %DATE% %TIME% >> "%LOG%"
echo. >> "%LOG%"
if not exist komchi_app.py (
  echo ERROR: komchi_app.py が見つかりません。 >> "%LOG%"
  start notepad "%LOG%"
  exit /b 1
)
where py >> "%LOG%" 2>>&1
if errorlevel 1 (
  where python >> "%LOG%" 2>>&1
)
echo. >> "%LOG%"
echo Starting Komchi... >> "%LOG%"
start "" python komchi_app.py >> "%LOG%" 2>>&1
if errorlevel 1 start "" py -3 komchi_app.py >> "%LOG%" 2>>&1
start notepad "%LOG%"
