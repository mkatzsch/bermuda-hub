@echo off
rem Bermuda Hub: yoga probe. Saves the schedule pages of Shamana Circle and Salt Yoga so a reader can be written.
rem Developed by AiTide Ltd. | www.AiTide.com
rem Version: 1.0
rem Last Updated: 2026-11-22
rem Change Log
rem   1.0 2026-11-22  First release.
rem Depends on: yoga_probe.py in this folder, Anaconda Python, the internet. Result: .cache\yoga_probe\
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
"%PY%" yoga_probe.py
