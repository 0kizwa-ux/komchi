@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Komchi Debug Start
cls
echo ========================================
echo   Komchi Debug Start
echo ========================================
echo.
echo Current folder:
echo %CD%
echo.
echo Checking files...
if exist komchi_app.py (
  echo OK: komchi_app.py found
) else (
  echo ERROR: komchi_app.py not found in this folder
  echo Please run this file from the Komchi folder.
  pause
  exit /b 1
)
echo.
echo Checking Python...
set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"
if "%PYTHON_CMD%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)
if "%PYTHON_CMD%"=="" (
  echo ERROR: Python not found.
  echo Install Python 3 from https://www.python.org/downloads/
  pause
  exit /b 1
)
echo Python command: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.
echo Starting Komchi...
echo If browser does not open, copy the URL shown below.
echo.
%PYTHON_CMD% komchi_app.py
echo.
echo Komchi stopped or failed. If there is an error above, copy it and send it.
pause
