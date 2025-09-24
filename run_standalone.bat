@echo off
cls
echo ======================================
echo Dolibarr MCP Standalone Server
echo ======================================
echo Starting Windows-compatible server...
echo (No pywin32 required!)
echo.

REM Check if virtual environment exists
if not exist "venv_dolibarr\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: setup_standalone.bat first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] Configuration file .env not found!
    echo.
    echo Creating .env from template...
    copy ".env.example" ".env" >nul
    echo [INFO] Please edit .env file with your Dolibarr credentials:
    echo   DOLIBARR_URL=https://your-dolibarr-instance.com/api/index.php
    echo   DOLIBARR_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv_dolibarr\Scripts\activate.bat

echo.
echo Starting Standalone Dolibarr MCP Server...
echo ✅ Using Python libraries without MCP package
echo ✅ No Windows permission issues
echo ✅ All CRUD operations available
echo.

REM Start the standalone server
python -m src.dolibarr_mcp.standalone_server

echo.
echo Server stopped.
pause
