#!/usr/bin/env python3
"""
Cleanup script to remove unnecessary files from dolibarr-mcp repository.
This script should be run locally after checking out the cleanup-restructure-v2 branch.
"""

import os
import shutil
from pathlib import Path

# List of files to remove
FILES_TO_REMOVE = [
    # Test scripts in root directory
    "test_api_connection.py",
    "test_api_debug.py",
    "test_connection.py",
    "test_dolibarr_mcp.py",
    "test_install.py",
    "test_standalone.py",
    "test_ultra.py",
    "test_ultra_direct.py",
    "diagnose_and_fix.py",
    
    # Batch files
    "cleanup.bat",
    "fix_installation.bat",
    "run_dolibarr_mcp.bat",
    "run_server.bat",
    "run_standalone.bat",
    "run_ultra.bat",
    "setup.bat",
    "setup_claude_complete.bat",
    "setup_manual.bat",
    "setup_standalone.bat",
    "setup_ultra.bat",
    "setup_windows_fix.bat",
    "start_server.bat",
    "validate_claude_config.bat",
    
    # Python scripts in root
    "mcp_server_launcher.py",
    "setup_env.py",
    
    # Alternative server implementations
    "src/dolibarr_mcp/simple_client.py",
    "src/dolibarr_mcp/standalone_server.py",
    "src/dolibarr_mcp/ultra_simple_server.py",
    
    # Multiple requirements files
    "requirements-minimal.txt",
    "requirements-ultra-minimal.txt",
    "requirements-windows.txt",
    
    # Documentation files
    "README_DE.md",
    "CLAUDE_CONFIG.md",
    "CONFIG_COMPATIBILITY.md",
    "MCP_FIX_GUIDE.md",
    "ULTRA-SOLUTION.md",
]

# Directories to remove
DIRS_TO_REMOVE = [
    "api",
]

def cleanup():
    """Remove unnecessary files and directories."""
    removed_files = []
    removed_dirs = []
    errors = []
    
    # Get repository root
    repo_root = Path(__file__).parent
    
    # Remove files
    for file_path in FILES_TO_REMOVE:
        full_path = repo_root / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                removed_files.append(file_path)
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                errors.append(f"Failed to remove {file_path}: {e}")
                print(f"❌ Failed: {file_path} - {e}")
        else:
            print(f"⚠️  Not found: {file_path}")
    
    # Remove directories
    for dir_path in DIRS_TO_REMOVE:
        full_path = repo_root / dir_path
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                removed_dirs.append(dir_path)
                print(f"✅ Removed directory: {dir_path}")
            except Exception as e:
                errors.append(f"Failed to remove {dir_path}: {e}")
                print(f"❌ Failed: {dir_path} - {e}")
        else:
            print(f"⚠️  Directory not found: {dir_path}")
    
    # Summary
    print("\n" + "="*50)
    print("CLEANUP SUMMARY")
    print("="*50)
    print(f"Files removed: {len(removed_files)}")
    print(f"Directories removed: {len(removed_dirs)}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\n❌ Errors encountered:")
        for error in errors:
            print(f"  - {error}")
    
    print("\n✅ Cleanup complete!")
    print("Don't forget to commit these changes:")
    print("  git add -A")
    print("  git commit -m 'Remove unnecessary files and clean up structure'")
    print("  git push origin cleanup-restructure-v2")

if __name__ == "__main__":
    print("🧹 Starting cleanup of dolibarr-mcp repository...")
    print("This will remove unnecessary files to match prestashop-mcp structure.\n")
    
    response = input("Are you sure you want to proceed? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        cleanup()
    else:
        print("Cleanup cancelled.")
