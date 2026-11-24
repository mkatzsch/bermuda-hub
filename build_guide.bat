@echo off
rem Bermuda Hub: refresh the Field guide, rebuild the page and publish it.
rem Part of Bermuda Hub | github.com/mkatzsch/bermuda-hub
rem Version: 1.0
rem Last Updated: 2026-11-22
rem Change Log
rem   1.0 2026-11-22  First release. Same as typing: run.bat --guide --build
rem Depends on: run.bat and run.py in this folder. Safe to double-click any time.
cd /d "%~dp0"
echo Refreshing the Field guide and rebuilding the Hub. This takes about 10 minutes. The window closes when it is done.
call run.bat --guide --build
