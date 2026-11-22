@echo off
rem Bermuda Hub: redraw the planner page from the saved events, rebuild the Hub and publish it.
rem Developed by AiTide Ltd. | www.AiTide.com
rem Version: 1.0
rem Last Updated: 2026-11-22
rem Change Log
rem   1.0 2026-11-22  First release. Same as typing: run.bat --events --build
rem Depends on: run.bat and run.py in this folder. Collects nothing new, so it takes under a minute.
cd /d "%~dp0"
echo Rebuilding the Hub. The window closes when it is done.
call run.bat --events --build
