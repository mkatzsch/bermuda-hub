@echo off
rem Bermuda Hub: install the PDF readers for Python, read the restaurant menus again, then rebuild and publish.
rem Developed by AiTide Ltd. | www.AiTide.com
rem Version: 1.0
rem Last Updated: 2026-11-22
rem Change Log
rem   1.0 2026-11-22  First release. Installs pypdf and pdfplumber from the Python package index (pip), then runs
rem                   the menu reader (deals\collect.py --own-menus-only) and a full rebuild (run.py --all --build).
rem Depends on: Anaconda Python, an internet connection. Writes menus_output.log and build_output.log.
rem Takes about half an hour. The window closes when it is done.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo Installing the PDF readers, reading menus, then rebuilding. About half an hour.
"%PY%" -m pip install pypdf pdfplumber >> menus_output.log 2>&1
cd /d "%~dp0deals"
"%PY%" collect.py --own-menus-only >> "%~dp0menus_output.log" 2>&1
cd /d "%~dp0"
"%PY%" run.py --all --build >> build_output.log 2>&1
