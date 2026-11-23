@echo off
rem Bermuda Hub map check: runs repin.py, which looks up approximate Explore pins on OpenStreetMap.
rem Developed by AiTide Ltd. | www.AiTide.com
rem Version: 1.0
rem Last Updated: 2026-11-22
rem Change Log
rem   1.0 2026-11-22  First release.
rem Depends on: repin.py in this folder and the internet. Takes about five minutes. Changes no pins.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo Checking the map pins. The window closes when it is done.
"%PY%" repin.py > repin_output.log 2>&1
