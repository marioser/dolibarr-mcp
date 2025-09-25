#!/usr/bin/env python3
"""
Fixed Dolibarr MCP Server launcher.
This script ensures the module can be found and launched correctly.
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_python_path():
    """Add necessary directories to Python path."""
    script_dir = Path(__file__).resolve().parent
    
    # Try different possible locations
    paths_to_try = [
        script_dir,  # Current directory
        script_dir / 'src',  # src subdirectory
        script_dir.parent,  # Parent directory
        script_dir.parent / 'src',  # Parent's src subdirectory
    ]
    
    for path in paths_to_try:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
            logger.info(f"Added to Python path: {path}")
    
    # Also check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.info(f"Running in virtual environment: {sys.prefix}")

def main():
    """Main entry point."""
    setup_python_path()
    
    try:
        # Try to import and run the server
        from dolibarr_mcp.dolibarr_mcp_server import main as server_main
        logger.info("Successfully imported dolibarr_mcp server")
        server_main()
    except ImportError as e:
        logger.error(f"Failed to import dolibarr_mcp: {e}")
        logger.error("Trying alternative import...")
        try:
            # Try alternative import path
            from src.dolibarr_mcp.dolibarr_mcp_server import main as server_main
            logger.info("Successfully imported using alternative path")
            server_main()
        except ImportError as e2:
            logger.error(f"Failed with alternative import: {e2}")
            logger.error("Please ensure the dolibarr_mcp module is installed correctly.")
            logger.error("Try running: pip install -e . from the project root directory")
            sys.exit(1)

if __name__ == "__main__":
    main()
