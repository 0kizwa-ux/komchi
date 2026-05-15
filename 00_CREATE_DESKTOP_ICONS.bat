@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Komchi - Create Desktop Icons
cls
echo ========================================
echo   CREATE DESKTOP ICONS / アイコン作成
echo ========================================
echo.
echo This creates Komchi shortcuts on your Desktop.
echo デスクトップに Komchi のアイコンを作成します。
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_desktop_shortcuts.ps1"
echo.
echo Done. Please check your Desktop.
echo 完了しました。デスクトップを確認してください。
pause
