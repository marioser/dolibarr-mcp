@echo off
cls
echo ======================================
echo Dolibarr MCP ULTRA Server
echo ======================================
echo Maximum Windows Compatibility Mode
echo ZERO compiled extensions (.pyd files)
echo.

REM Check if ultra virtual environment exists
if not exist "venv_ultra\Scripts\activate.bat" (
    echo [ERROR] Ultra virtual environment not found!
    echo Please run: setup_ultra.bat first
    echo.
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

echo Activating ultra virtual environment...
call venv_ultra\Scripts\activate.bat

echo.
echo 🚀 Starting ULTRA-COMPATIBLE Dolibarr MCP Server...
echo ✅ Pure Python implementation
echo ✅ ZERO compiled extensions
echo ✅ Standard library + requests only
echo ✅ Works on ANY Windows version
echo.
echo Available features:
echo   • All CRUD operations for Dolibarr
echo   • Interactive testing console
echo   • Professional error handling
echo   • Zero permission issues
echo.

REM Start the ultra-simple server
python -m src.dolibarr_mcp.ultra_simple_server

echo.
echo Server stopped.
echo.
pause
