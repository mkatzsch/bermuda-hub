@echo off
rem Bermuda Hub: papers miner. Lists research papers about Bermuda and the Sargasso Sea for checking.
rem Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
rem Version: 1.0
rem Last Updated: 2026-11-24
rem Change Log
rem   1.0 2026-11-24  First release.
rem Depends on: papers_mine.py in this folder, Anaconda Python, the internet. Result: events\data\papers_candidates.json
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
"%PY%" papers_mine.py > papers_mine_output.log 2>&1
