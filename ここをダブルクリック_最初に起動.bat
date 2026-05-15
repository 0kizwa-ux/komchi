@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Komchi Creator App
cls
echo ========================================
echo   Komchi Creator App を起動します
echo ========================================
echo.
echo 基本はこのファイルだけをダブルクリックすればOKです。
echo ブラウザが開いたら、画面のボタンから機能を選んでください。
echo.
echo デスクトップにアイコンを作りたい場合は、
echo 「デスクトップにアイコンを作成.bat」をダブルクリックしてください。
echo.
py -3 komchi_app.py
if errorlevel 1 python komchi_app.py
pause
