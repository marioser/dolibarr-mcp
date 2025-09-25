#!/usr/bin/env python3
"""
Comprehensive diagnostic and repair tool for Dolibarr MCP Server.
This script identifies and fixes common installation and configuration issues.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
import importlib.util

class DolibarrMCPDiagnostic:
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.root_dir = Path(__file__).resolve().parent
        
    def run_diagnostics(self):
        """Run all diagnostic checks."""
        print("=" * 60)
        print("Dolibarr MCP Server - Diagnostic & Repair Tool")
        print("=" * 60)
        print()
        
        # Check Python version
        self.check_python_version()
        
        # Check virtual environment
        self.check_virtual_environment()
        
        # Check package installation
        self.check_package_installation()
        
        # Check module structure
        self.check_module_structure()
        
        # Check environment variables
        self.check_environment()
        
        # Check MCP server files
        self.check_server_files()
        
        # Report results
        self.report_results()
        
    def check_python_version(self):
        """Check if Python version is compatible."""
        print("Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.issues.append(f"Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        else:
            print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
            
    def check_virtual_environment(self):
        """Check if running in a virtual environment."""
        print("Checking virtual environment...")
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if not in_venv:
            print("⚠ Not running in a virtual environment")
            venv_path = self.root_dir / 'venv_dolibarr'
            if not venv_path.exists():
                print(f"  Creating virtual environment at {venv_path}...")
                try:
                    subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
                    self.fixes_applied.append("Created virtual environment")
                except subprocess.CalledProcessError as e:
                    self.issues.append(f"Failed to create virtual environment: {e}")
        else:
            print(f"✓ Virtual environment active: {sys.prefix}")
            
    def check_package_installation(self):
        """Check if the package is installed correctly."""
        print("Checking package installation...")
        
        # Try to import the module
        try:
            import dolibarr_mcp
            print("✓ dolibarr_mcp module found")
        except ImportError:
            print("✗ dolibarr_mcp module not found")
            
            # Try to fix by adjusting sys.path
            src_path = self.root_dir / 'src'
            if src_path.exists():
                sys.path.insert(0, str(src_path))
                try:
                    import dolibarr_mcp
                    print("✓ Fixed by adding src to path")
                    self.fixes_applied.append(f"Added {src_path} to Python path")
                except ImportError:
                    self.issues.append("Module cannot be imported even with path adjustment")
                    self.attempt_install()
                    
    def attempt_install(self):
        """Attempt to install the package."""
        print("  Attempting to install package...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', str(self.root_dir)], 
                         check=True, capture_output=True, text=True)
            self.fixes_applied.append("Installed package in development mode")
            print("  ✓ Package installed successfully")
        except subprocess.CalledProcessError as e:
            self.issues.append(f"Failed to install package: {e}")
            
    def check_module_structure(self):
        """Check if the module structure is correct."""
        print("Checking module structure...")
        
        required_files = [
            self.root_dir / 'src' / 'dolibarr_mcp' / '__init__.py',
            self.root_dir / 'src' / 'dolibarr_mcp' / 'dolibarr_mcp_server.py',
            self.root_dir / 'src' / 'dolibarr_mcp' / 'dolibarr_client.py',
            self.root_dir / 'src' / 'dolibarr_mcp' / 'config.py',
        ]
        
        missing_files = []
        for file in required_files:
            if not file.exists():
                missing_files.append(str(file.relative_to(self.root_dir)))
                
        if missing_files:
            self.issues.append(f"Missing required files: {', '.join(missing_files)}")
        else:
            print("✓ All required module files present")
            
    def check_environment(self):
        """Check environment variables."""
        print("Checking environment configuration...")
        
        env_file = self.root_dir / '.env'
        if not env_file.exists():
            print("✗ .env file not found")
            env_example = self.root_dir / '.env.example'
            if env_example.exists():
                print("  Creating .env from .env.example...")
                import shutil
                shutil.copy(env_example, env_file)
                self.fixes_applied.append("Created .env file from template")
                print("  ⚠ Please edit .env with your Dolibarr credentials")
        else:
            print("✓ .env file exists")
            
            # Check if it has required variables
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                
                required_vars = ['DOLIBARR_URL', 'DOLIBARR_API_KEY']
                missing_vars = []
                
                for var in required_vars:
                    if not os.getenv(var):
                        missing_vars.append(var)
                        
                if missing_vars:
                    self.issues.append(f"Missing environment variables: {', '.join(missing_vars)}")
                else:
                    print("✓ All required environment variables set")
            except ImportError:
                print("  Installing python-dotenv...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-dotenv'], 
                             capture_output=True)
                self.fixes_applied.append("Installed python-dotenv")
                
    def check_server_files(self):
        """Check if MCP server can be started."""
        print("Checking MCP server readiness...")
        
        # Try to import and check main function
        try:
            spec = importlib.util.spec_from_file_location(
                "server_test",
                self.root_dir / 'src' / 'dolibarr_mcp' / 'dolibarr_mcp_server.py'
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'main'):
                    print("✓ Server main function found")
                else:
                    self.issues.append("Server main function not found")
        except Exception as e:
            self.issues.append(f"Cannot load server module: {e}")
            
    def report_results(self):
        """Report diagnostic results and provide recommendations."""
        print()
        print("=" * 60)
        print("Diagnostic Results")
        print("=" * 60)
        
        if self.fixes_applied:
            print("\n✅ Fixes Applied:")
            for fix in self.fixes_applied:
                print(f"  - {fix}")
                
        if self.issues:
            print("\n⚠ Issues Found:")
            for issue in self.issues:
                print(f"  - {issue}")
                
            print("\n📋 Recommended Actions:")
            print("1. Run fix_installation.bat to reinstall")
            print("2. Update .env file with your Dolibarr credentials")
            print("3. Try running: python mcp_server_launcher.py")
        else:
            print("\n✅ No issues found! Server should be ready to run.")
            print("\nYou can now:")
            print("1. Configure Claude Desktop (see CLAUDE_CONFIG.md)")
            print("2. Run the server with: python mcp_server_launcher.py")
            
        # Create a quick launcher if everything is OK
        if not self.issues:
            self.create_quick_launcher()
            
    def create_quick_launcher(self):
        """Create a quick launcher script."""
        launcher_path = self.root_dir / 'quick_start.bat'
        
        content = f'''@echo off
echo Starting Dolibarr MCP Server...
cd /d "{self.root_dir}"

if exist venv_dolibarr (
    call venv_dolibarr\\Scripts\\activate
)

python mcp_server_launcher.py
pause
'''
        
        with open(launcher_path, 'w') as f:
            f.write(content)
            
        print(f"\n✨ Created quick_start.bat for easy server launch")

if __name__ == "__main__":
    diagnostic = DolibarrMCPDiagnostic()
    diagnostic.run_diagnostics()
