@echo off
rem Bermuda Hub: AIS coverage test. Listens to AISStream for 3 minutes and lists the ships heard near Bermuda.
rem Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
rem Version: 1.1
rem Last Updated: 2026-11-22
rem Change Log
rem   1.1 2026-11-22  Listens for 3 minutes instead of 10, since ais_test.py now runs its own control.
rem   1.0 2026-11-22  First release.
rem Depends on: ais_test.py and .env (AISSTREAM_KEY) in this folder, Anaconda Python, the internet.
rem Installs the "websockets" Python package if it is missing. Result: ais_test_output.log and events\data\ais_test.json.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo AIS test: listening for 3 minutes, plus 1 more if Bermuda is silent. The window closes when it is done.
"%PY%" -m pip install -q websockets > ais_test_output.log 2>&1
"%PY%" ais_test.py --minutes 3 >> ais_test_output.log 2>&1
