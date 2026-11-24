@echo off
rem Bermuda Hub: On this day miner. Reads Wikipedia articles and lists dated sentences for checking.
rem Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
rem Version: 1.0
rem Last Updated: 2026-11-24
rem Change Log
rem   1.0 2026-11-24  First release.
rem Depends on: otd_mine.py in this folder, Anaconda Python, the internet. Result: events\data\onthisday_candidates.json
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
"%PY%" otd_mine.py > otd_mine_output.log 2>&1
