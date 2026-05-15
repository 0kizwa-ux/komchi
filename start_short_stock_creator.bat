@echo off
cd /d "%~dp0"
set STOCK_DIR=C:\Users\osk_k\Desktop\ユーチューブショート動画ストック
set /p THEME=ショート動画のテーマを入力してください: 
if "%THEME%"=="" set THEME=今日の便利ワザ
py -3 shorts\create_stock_short.py --theme "%THEME%" --output-dir "%STOCK_DIR%"
if errorlevel 1 python shorts\create_stock_short.py --theme "%THEME%" --output-dir "%STOCK_DIR%"
pause
