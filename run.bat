@echo off
setlocal
cd /d "%~dp0"

set "APP_URL=http://localhost:8504"
set "APP_HEALTH=http://127.0.0.1:8504/_stcore/health"

rem Reuse the updated project server when it is already running.
powershell.exe -NoProfile -Command "try { $null = Invoke-WebRequest -UseBasicParsing -Uri '%APP_HEALTH%' -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 goto start_app
goto open_app

:start_app
set "PYTHON=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if exist "%PYTHON%" (
    start "Quizly server" /min "%PYTHON%" -m streamlit run "%~dp0app.py" --server.port 8504 --server.headless true
) else (
    where py >nul 2>&1
    if errorlevel 1 (
        echo Python was not found. Install Python, then run: py -m pip install -r requirements.txt
        pause
        exit /b 1
    )
    start "Quizly server" /min py -m streamlit run "%~dp0app.py" --server.port 8504 --server.headless true
)

set /a attempts=0
:wait_for_app
powershell.exe -NoProfile -Command "try { $null = Invoke-WebRequest -UseBasicParsing -Uri '%APP_HEALTH%' -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto open_app
set /a attempts+=1
if %attempts% GEQ 30 (
    echo Quizly did not start. Check that Streamlit is installed with: py -m pip install -r requirements.txt
    pause
    exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait_for_app

:open_app
start "" "%APP_URL%"
exit /b 0
