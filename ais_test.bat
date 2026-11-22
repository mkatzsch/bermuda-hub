@echo off
rem Bermuda Hub: AIS coverage test. Listens to AISStream for 10 minutes and lists the ships heard near Bermuda.
rem Developed by AiTide Ltd. | www.AiTide.com
rem Version: 1.0
rem Last Updated: 2026-11-22
rem Change Log
rem   1.0 2026-11-22  First release.
rem Depends on: ais_test.py and .env (AISSTREAM_KEY) in this folder, Anaconda Python, the internet.
rem Installs the "websockets" Python package if it is missing. Result: ais_test_output.log and events\data\ais_test.json.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo AIS test: listening for 10 minutes. The window closes when it is done.
"%PY%" -m pip install -q websockets > ais_test_output.log 2>&1
"%PY%" ais_test.py --minutes 10 >> ais_test_output.log 2>&1
