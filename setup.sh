#!/bin/bash
echo "🚀 Setting up Dolibarr MCP Development Environment..."
echo

# Run the setup script
python3 setup.py

echo
echo "📋 Quick Start Commands:"
echo
echo "  Activate virtual environment:"
echo "  \$ source venv_dolibarr/bin/activate"
echo
echo "  Test the server:"
echo "  \$ venv_dolibarr/bin/python -m dolibarr_mcp.dolibarr_mcp_server"
echo
echo "  Run with Docker:"
echo "  \$ docker-compose up"
echo
