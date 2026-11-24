@echo off
rem Bermuda Hub: Atlantic Explorer probe. Saves the BIOS cruise schedule and what Python can read from it.
rem Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
rem Version: 1.0
rem Last Updated: 2026-11-23
rem Change Log
rem   1.0 2026-11-23  First release.
rem Depends on: ae_probe.py in this folder, Anaconda Python with pdfplumber, the internet. Result: .cache\ae_probe\
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
"%PY%" ae_probe.py > ae_probe_output.log 2>&1
