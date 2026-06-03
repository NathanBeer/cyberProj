@echo off
echo Starting CyberDetect Pipeline...
echo.
echo Services:
echo   JupyterLab       -^> http://localhost:8888  (token: cyberdetect)
echo   Redpanda Console -^> http://localhost:8080
echo   Jaeger Tracing   -^> http://localhost:16686
echo.

cd /d "%~dp0pipeline"

docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

docker compose build --no-cache
docker compose up
if errorlevel 1 (
    echo.
    echo ERROR: docker compose failed. See output above.
)

pause
