@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Komchi Icons
cls
echo Komchi のデスクトップアイコンを作成しています...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_desktop_shortcuts.ps1"
if errorlevel 1 (
  echo.
  echo アイコン作成に失敗しました。上のエラーをコピーして送ってください。
  pause
  exit /b 1
)
echo.
echo 完了しました。デスクトップを確認してください。
pause
