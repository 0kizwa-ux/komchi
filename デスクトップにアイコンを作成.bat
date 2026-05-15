@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Komchi Desktop Icons
cls
echo ========================================
echo   デスクトップに Komchi アイコンを作成します
echo ========================================
echo.
echo 作成されるアイコン:
echo  - Komchi Creator App
echo  - Komchi ROOM Draft
echo  - Komchi Photo Dance
echo  - Komchi Short Stock
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_desktop_shortcuts.ps1"
echo.
echo 完了しました。デスクトップを確認してください。
pause
