@echo off
cd /d "%~dp0"
set STOCK_DIR=C:\Users\osk_k\Desktop\ユーチューブショート動画ストック
set /p IMAGE_PATH=肖像画像のパスを入力してください: 
set /p THEME=動画テーマを入力してください: 
set /p BGM_PATH=BGMファイルのパスを入力してください（空欄なら簡易ビート）: 
if "%THEME%"=="" set THEME=写真ダンス
if "%BGM_PATH%"=="" (
  py -3 shorts\create_photo_dance.py --image "%IMAGE_PATH%" --theme "%THEME%" --output-dir "%STOCK_DIR%"
  if errorlevel 1 python shorts\create_photo_dance.py --image "%IMAGE_PATH%" --theme "%THEME%" --output-dir "%STOCK_DIR%"
) else (
  py -3 shorts\create_photo_dance.py --image "%IMAGE_PATH%" --theme "%THEME%" --bgm "%BGM_PATH%" --output-dir "%STOCK_DIR%"
  if errorlevel 1 python shorts\create_photo_dance.py --image "%IMAGE_PATH%" --theme "%THEME%" --bgm "%BGM_PATH%" --output-dir "%STOCK_DIR%"
)
pause
