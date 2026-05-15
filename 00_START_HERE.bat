@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Komchi Creator App - START HERE
cls
echo ========================================
echo   START HERE / まず最初にこれを起動
echo ========================================
echo.
echo This is the main launcher.
echo これがメイン起動ファイルです。
echo.
echo Browser will open automatically.
echo ブラウザが自動で開きます。
echo.
py -3 komchi_app.py
if errorlevel 1 python komchi_app.py
pause
