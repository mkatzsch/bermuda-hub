@echo off
rem Bermuda Hub: look for reusable photos (Field guide species and Explore places), then rebuild and publish.
rem Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
rem Version: 1.0
rem Last Updated: 2026-11-22
rem Change Log
rem   1.0 2026-11-22  First release. Same as: run.py --all --build --photos
rem Depends on: run.py in this folder and the internet (iNaturalist, Wikipedia, Wikimedia Commons).
rem Takes about ten minutes. Safe to double click any time. Output goes to photos_output.log.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo Looking for photos and rebuilding the Hub. The window closes when it is done.
"%PY%" run.py --all --build --photos > photos_output.log 2>&1
