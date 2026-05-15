@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Komchi
cls
echo Komchi を起動しています...
echo.
if not exist komchi_app.py (
  echo komchi_app.py が見つかりません。
  echo このSTART.batをKomchiフォルダ内で実行してください。
  pause
  exit /b 1
)

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"
if "%PYTHON_CMD%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if "%PYTHON_CMD%"=="" (
  echo Python が見つかりません。
  echo 先に Python 3 をインストールしてください。
  echo https://www.python.org/downloads/
  echo.
  pause
  exit /b 1
)

echo Python: %PYTHON_CMD%
echo ブラウザが開かない場合は、表示されるURLをコピーしてください。
echo.
%PYTHON_CMD% komchi_app.py
if errorlevel 1 (
  echo.
  echo 起動に失敗しました。上のエラーをコピーして送ってください。
  echo 詳細確認は START_DEBUG.bat を実行してください。
  pause
  exit /b 1
)
echo.
echo Komchi が終了しました。
pause
