@echo off
REM Daily YouTube early-signal digest. Windows Task Scheduler runs this at 12:00
REM local time; the machine is on Central, so noon Chicago needs no timezone math
REM and daylight saving handles itself.
REM
REM Absolute paths only: a scheduled task does not start in the repo.
set REPO=C:\Users\david\projects\youtube-money
set PY=C:\Users\david\AppData\Local\Programs\Python\Python312\python.exe

cd /d "%REPO%"
echo ==== %DATE% %TIME% ==== >> "%REPO%\data\digest\run.log"
"%PY%" "%REPO%\scripts\digest\daily.py" --post >> "%REPO%\data\digest\run.log" 2>&1
echo exit=%ERRORLEVEL% >> "%REPO%\data\digest\run.log"
