@echo off
cls
echo ======================================
echo Dolibarr MCP Windows Setup Fix v2.1
echo ======================================

echo Cleaning up old artifacts...

REM Force cleanup of problematic files
if exist "venv_dolibarr" (
    echo Removing old virtual environment...
    rmdir /s /q "venv_dolibarr" 2>nul
    timeout /t 2 /nobreak >nul
)

echo Creating fresh virtual environment...
python -m venv venv_dolibarr
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to create virtual environment
    echo Check if Python 3.8+ is installed: python --version
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv_dolibarr\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Pip upgrade failed but continuing...
)

echo Installing dependencies (minimal set to avoid Windows issues)...
pip install -r requirements-minimal.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Trying alternative installation method...
    
    echo Installing packages individually...
    pip install mcp>=1.0.0
    pip install requests>=2.31.0
    pip install aiohttp>=3.9.0
    pip install pydantic>=2.5.0
    pip install click>=8.1.0
    pip install python-dotenv>=1.0.0
    pip install typing-extensions>=4.8.0
    
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Individual package installation also failed
        echo Trying with --no-deps flag for problematic packages...
        pip install --no-deps aiohttp
        pip install --no-deps pydantic
    )
)

echo.
echo Testing installation...
python -c "import mcp; import requests; import aiohttp; import pydantic; import click; import dotenv; print('✅ All core packages imported successfully')"
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Some packages may not have installed correctly
    echo But attempting to continue...
)

echo.
echo Checking if .env file exists...
if not exist ".env" (
    echo Creating .env file from template...
    copy ".env.example" ".env" >nul 2>&1
    echo [INFO] Please edit .env file with your Dolibarr credentials
)

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo ✅ Virtual environment: venv_dolibarr
echo ✅ Dependencies: Installed (minimal set)
echo 📝 Next steps:
echo    1. Edit .env file with your Dolibarr credentials
echo    2. Run: start_server.bat
echo.
echo To test the server:
echo    python -m src.dolibarr_mcp
echo.
pause
