@echo off
rem Bermuda Hub daily run. Called by the scheduled task; safe to double-click any time.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
"%PY%" run.py %* >> run_output.txt 2>&1
