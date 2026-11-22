@echo off
setlocal EnableExtensions
title GramAI - Desktop Launcher
cd /d "%~dp0"

echo.
echo  ==========================================
echo       GramAI - Rural Assistance System
echo  ==========================================
echo.

rem Prefer the project's virtual environment when available.
set "PYTHON_EXE="
if exist "%~dp0.venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%~dp0venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"

if not defined PYTHON_EXE (
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -c "import sys; print(sys.version)" >nul 2>&1
        if not errorlevel 1 set "PYTHON_EXE=py -3"
    )
)
if not defined PYTHON_EXE (
    where python >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
    echo [ERROR] Python 3 was not found.
    echo Install Python 3.10 or newer from https://www.python.org/downloads/
    echo Make sure Python is added to PATH, then double-click this file again.
    goto :failed
)

echo [INFO] Checking required desktop packages...
%PYTHON_EXE% -c "import PyQt6, mysql.connector, speech_recognition, gtts, pygame" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Some dependencies are missing.
    echo.
    choice /C YN /M "Install requirements from requirements.txt now"
    if errorlevel 2 goto :failed
    %PYTHON_EXE% -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        echo Check the error above. PyAudio may require a compatible Python version.
        goto :failed
    )
)

echo [INFO] Starting GramAI...
%PYTHON_EXE% "%~dp0main.py"
if errorlevel 1 (
    echo.
    echo [ERROR] GramAI closed with an error.
    echo Check the messages above. MySQL must be configured separately.
    goto :failed
)
echo [INFO] GramAI closed.
exit /b 0

:failed
echo.
pause
exit /b 1
