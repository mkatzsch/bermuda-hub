@echo off
cd /d "%~dp0"
set PY=%USERPROFILE%\anaconda3\python.exe
if not exist "%PY%" set PY=python
echo Installing the OCR readers (EasyOCR downloads its model the first time it runs, about 100 MB)...
"%PY%" -m pip install -r deals\requirements.txt
echo.
echo Reading the flyer images already on this laptop...
cd deals
"%PY%" collect.py --ocr-only
cd ..
echo.
echo Done. The result is in deals\data\flyers\lindos_ocr.json and supermart_ocr.json.
pause
