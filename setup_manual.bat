@echo off
echo 🔧 Manual Setup for Dolibarr MCP (Windows Fix)
echo.

REM Activate virtual environment first
echo 🐍 Activating virtual environment...
call venv_dolibarr\Scripts\activate.bat

REM Verify Python installation
echo ✅ Checking Python version...
venv_dolibarr\Scripts\python.exe --version

REM Install requirements again with explicit encoding
echo 📦 Installing requirements with UTF-8 encoding...
set PYTHONIOENCODING=utf-8
venv_dolibarr\Scripts\python.exe -m pip install --upgrade pip
venv_dolibarr\Scripts\python.exe -m pip install aiohttp>=3.9.0
venv_dolibarr\Scripts\python.exe -m pip install pydantic>=2.5.0
venv_dolibarr\Scripts\python.exe -m pip install python-dotenv>=1.0.0
venv_dolibarr\Scripts\python.exe -m pip install click>=8.1.0
venv_dolibarr\Scripts\python.exe -m pip install typing-extensions>=4.8.0

REM Install MCP manually - try different sources
echo 🔗 Installing MCP framework...
venv_dolibarr\Scripts\python.exe -m pip install mcp==1.0.0
if errorlevel 1 (
    echo 🔄 Trying alternative MCP installation...
    venv_dolibarr\Scripts\python.exe -m pip install git+https://github.com/modelcontextprotocol/python-sdk.git
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env 2>nul || (
        echo # Dolibarr MCP Configuration > .env
        echo DOLIBARR_URL=https://your-dolibarr-instance.com/api/index.php >> .env
        echo DOLIBARR_API_KEY=your_api_key_here >> .env
        echo LOG_LEVEL=INFO >> .env
    )
)

REM Test Python module import manually
echo 🧪 Testing module import...
venv_dolibarr\Scripts\python.exe -c "import sys; sys.path.insert(0, 'src'); from dolibarr_mcp.config import Config; print('✅ Module import successful')" 2>nul
if errorlevel 1 (
    echo ⚠️  Direct import failed, but this is expected without development installation
) else (
    echo ✅ Module import working!
)

REM Test basic connection
echo 🔌 Testing Dolibarr connection (if configured)...
venv_dolibarr\Scripts\python.exe test_connection.py 2>nul
if errorlevel 1 (
    echo ⚠️  Connection test failed - please check your .env configuration
) else (
    echo ✅ Connection test passed!
)

echo.
echo 🎯 Manual Setup Complete!
echo.
echo 📋 Next Steps:
echo   1. Edit .env file: notepad .env
echo   2. Configure your Dolibarr URL and API key
echo   3. Test: venv_dolibarr\Scripts\python.exe test_connection.py
echo   4. Run MCP: venv_dolibarr\Scripts\python.exe -m dolibarr_mcp.dolibarr_mcp_server
echo.
echo 💡 Alternative: Use Docker instead: docker-compose up
echo.

pause
