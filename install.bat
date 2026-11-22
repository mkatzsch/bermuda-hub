@echo off
rem One-time setup for Bermuda Hub.
rem 1. Moves the data from the old BermudaDeals folder (next to this one) into deals\ if it has not been moved yet.
rem 2. Installs the Python packages the planner needs (the deals collector only needs what Anaconda already has).
rem 3. Replaces the old "Bermuda Deals collector" task with one "Bermuda Hub" task, daily at 6:00 am, wake enabled.
rem 4. Runs once now.
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python

set OLD=%~dp0..\BermudaDeals
if exist "%OLD%\data" if not exist "deals\data" (
  echo Moving data from BermudaDeals into deals\ ...
  move "%OLD%\data" "deals\data" >nul
  if exist "%OLD%\flyers" move "%OLD%\flyers" "deals\flyers" >nul
  for %%F in (history.csv editorial.json log.txt status.json) do if exist "%OLD%\%%F" move /Y "%OLD%\%%F" "deals\%%F" >nul
  echo Moved. The old folder can be deleted once you are happy with the new one.
)

echo Installing planner dependencies ...
"%PY%" -m pip install -q -r events\requirements.txt
"%PY%" -m pip install -q -r deals\requirements.txt
"%PY%" -m pip install -q playwright && "%PY%" -m playwright install chromium

schtasks /Delete /F /TN "Bermuda Deals collector" >nul 2>&1
schtasks /Create /F /SC DAILY /ST 06:00 /TN "Bermuda Hub" /TR "\"%~dp0run.bat\"" /RL LIMITED
if errorlevel 1 (echo Could not register the scheduled task. Run this file again as administrator.& pause& exit /b 1)
powershell -NoProfile -Command "Set-ScheduledTask -TaskName \"Bermuda Hub\" -Settings (New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 2)) | Out-Null"
echo Scheduled task registered: Bermuda Hub, daily 6:00 am (deals every day, planner Mondays and Fridays).

echo Running once now (planner seed plus a full collection; a few minutes) ...
call run.bat --all
echo.
echo Done. Open site\index.html. Logs: log.txt (hub), deals\log.txt, run_output.txt.
pause
