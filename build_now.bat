@echo off
rem Bermuda Hub: rebuild the deals page and the planner page from saved data, rebuild the Hub and publish it.
rem Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
rem Version: 1.2
rem Last Updated: 2026-11-22
rem Change Log
rem   1.2 2026-11-22  Also rebuilds the deals page (run.py --all --build), so changes to Eats show up.
rem   1.1 2026-11-22  Runs Python itself and writes to build_output.log, so it no longer waits for
rem                   run_output.txt when another job (the menu reader) has that file open.
rem   1.0 2026-11-22  First release.
rem Depends on: run.py in this folder. Collects nothing new, so it takes under a minute.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo Rebuilding the Hub. The window closes when it is done.
"%PY%" run.py --all --build >> build_output.log 2>&1
