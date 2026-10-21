@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\open-forge.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Forge encountered an error while starting.
    pause
)
endlocal
