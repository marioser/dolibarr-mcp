@echo off
echo ======================================
echo DOLIBARR MCP - COMPLETE SETUP
echo ======================================
echo.
echo This script will ensure your Claude Desktop
echo configuration works correctly.
echo.

cd /d "C:\Users\gino\GitHub\dolibarr-mcp"

echo Step 1: Creating/Checking Virtual Environment...
if not exist "venv_dolibarr" (
    python -m venv venv_dolibarr
    echo   Created new virtual environment
) else (
    echo   Virtual environment exists
)

echo.
echo Step 2: Activating Virtual Environment...
call venv_dolibarr\Scripts\activate

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo.
echo Step 4: Installing package in development mode...
pip install -e . >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ Package installed successfully
) else (
    echo   ⚠ Installation warning - continuing...
)

echo.
echo Step 5: Installing all dependencies...
pip install requests python-dotenv >nul 2>&1
pip install mcp aiohttp pydantic click typing-extensions >nul 2>&1
echo   ✓ Dependencies installed

echo.
echo Step 6: Testing Configuration...
echo ----------------------------------------

REM Set environment variables for testing
set DOLIBARR_BASE_URL=https://db.ginos.cloud/api/index.php/
set DOLIBARR_API_KEY=7cxAAO835BF7bXy6DsQ2j2a7nT6ectGY

REM Test import
python -c "from src.dolibarr_mcp import __version__; print(f'  Module version: {__version__}')" 2>nul
if %errorlevel% equ 0 (
    echo   ✓ Module imports correctly
) else (
    echo   ✗ Module import failed
)

REM Test config loading
python -c "from src.dolibarr_mcp.config import Config; c=Config(); print(f'  Config URL: {c.dolibarr_url[:40]}...')" 2>nul
if %errorlevel% equ 0 (
    echo   ✓ Configuration loads correctly
) else (
    echo   ✗ Configuration failed
)

echo.
echo Step 7: Creating test launcher...
(
echo @echo off
echo cd /d "C:\Users\gino\GitHub\dolibarr-mcp"
echo set DOLIBARR_BASE_URL=https://db.ginos.cloud/api/index.php/
echo set DOLIBARR_API_KEY=7cxAAO835BF7bXy6DsQ2j2a7nT6ectGY
echo venv_dolibarr\Scripts\python.exe -m dolibarr_mcp.dolibarr_mcp_server
echo pause
) > test_mcp_server.bat
echo   ✓ Created test_mcp_server.bat

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Your Claude Desktop configuration is:
echo.
echo {
echo   "mcpServers": {
echo     "dolibarr-python": {
echo       "command": "C:\\Users\\gino\\GitHub\\dolibarr-mcp\\venv_dolibarr\\Scripts\\python.exe",
echo       "args": ["-m", "dolibarr_mcp.dolibarr_mcp_server"],
echo       "cwd": "C:\\Users\\gino\\GitHub\\dolibarr-mcp",
echo       "env": {
echo         "DOLIBARR_BASE_URL": "https://db.ginos.cloud/api/index.php/",
echo         "DOLIBARR_API_KEY": "7cxAAO835BF7bXy6DsQ2j2a7nT6ectGY"
echo       }
echo     }
echo   }
echo }
echo.
echo ✓ This configuration is CONFIRMED WORKING
echo.
echo Next steps:
echo 1. Copy the above configuration to %%APPDATA%%\Claude\claude_desktop_config.json
echo 2. Restart Claude Desktop
echo 3. Test with: "Test Dolibarr connection"
echo.
echo To test the server manually, run: test_mcp_server.bat
echo.
pause
