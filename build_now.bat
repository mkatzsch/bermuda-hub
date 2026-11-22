@echo off
rem Bermuda Hub: redraw the planner page from the saved events, rebuild the Hub and publish it.
rem Developed by AiTide Ltd. | www.AiTide.com
rem Version: 1.1
rem Last Updated: 2026-11-22
rem Change Log
rem   1.1 2026-11-22  Runs Python itself and writes to build_output.log, so it no longer waits for
rem                   run_output.txt when another job (the menu reader) has that file open.
rem   1.0 2026-11-22  First release. Same as typing: run.bat --events --build
rem Depends on: run.py in this folder. Collects nothing new, so it takes under a minute.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo Rebuilding the Hub. The window closes when it is done.
"%PY%" run.py --events --build >> build_output.log 2>&1
