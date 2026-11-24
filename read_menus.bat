@echo off
rem Bermuda Hub: read restaurant prices from each restaurant's own website.
rem Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
rem Version: 1.1
rem Last Updated: 2026-11-22
rem Change Log
rem   1.1 2026-11-22  Writes to menus_output.log instead of run_output.txt, which blocked builds while it ran.
rem   1.0 2026-11-22  First release. Same as typing, in the deals folder: python collect.py --own-menus-only
rem Depends on: deals\collect.py and deals\bgd\menus_own.py. Writes deals\data\menus_own.json and markup.json.
rem Can take half an hour or more. Progress is written to deals\log.txt. The window closes when it is done.
cd /d "%~dp0deals"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo Reading restaurant menus. This can take half an hour or more.
"%PY%" collect.py --own-menus-only >> "%~dp0menus_output.log" 2>&1
