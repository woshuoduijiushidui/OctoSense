@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
echo Starting latest Pantry Steward. Keep this window open.
python -X utf8 "%~dp0tools\run_pantry_local.py" %*
set "pantry_status=%errorlevel%"
if not "%pantry_status%"=="0" pause
exit /b %pantry_status%
