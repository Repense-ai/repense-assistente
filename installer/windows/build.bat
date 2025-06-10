@echo off
setlocal

REM Get the directory of this script
set "SCRIPT_DIR=%~dp0"

echo ===================================
echo  Build do Instalador Windows
echo  Repense Assistente
echo ===================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ and add it to your PATH.
    pause
    exit /b 1
)

echo [INFO] Found Python installation.
echo.

REM Run the main build script
python "%SCRIPT_DIR%build.py"

REM Check the exit code of the Python script
if errorlevel 1 (
    echo.
    echo [ERROR] The build script failed.
    pause
    exit /b 1
)

echo.
echo ===================================
echo  Build process finished.
echo ===================================
echo.

pause
