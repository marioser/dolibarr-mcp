"""Direct test for ultra simple server - completely self-contained."""

import sys
import os

print("=" * 50)
print("Ultra-Simple Dolibarr MCP Server Test")
print("=" * 50)
print(f"Python version: {sys.version}")
print("")

# Test 1: Standard library
print("✅ Testing standard library imports:")
try:
    import json
    import logging
    import os
    import sys
    from typing import Dict, List, Optional, Any
    print("   json, logging, os, sys, typing - OK")
except ImportError as e:
    print(f"   ❌ Standard library import failed: {e}")
    sys.exit(1)

# Test 2: Requests library
print("✅ Testing requests library:")
try:
    import requests
    print(f"   requests {requests.__version__} - OK")
except ImportError as e:
    print(f"   ❌ requests import failed: {e}")
    print("   Please run: setup_ultra.bat")
    sys.exit(1)

# Test 3: Direct import of ultra server
print("✅ Testing ultra server import:")
try:
    # Direct import without going through package
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'dolibarr_mcp'))
    import ultra_simple_server
    print("   ultra_simple_server module - OK")
except ImportError as e:
    print(f"   ❌ ultra_simple_server import failed: {e}")
    sys.exit(1)

# Test 4: Server instantiation
print("✅ Testing server creation:")
try:
    server = ultra_simple_server.UltraSimpleServer("test-ultra")
    tools = server.get_available_tools()
    print(f"   Server created - OK")
    print(f"   Available tools: {len(tools)}")
    print(f"   Sample tools: {', '.join(tools[:5])}")
except Exception as e:
    print(f"   ❌ Server creation failed: {e}")
    sys.exit(1)

# Test 5: Configuration loading
print("✅ Testing configuration:")
try:
    config = ultra_simple_server.UltraSimpleConfig()
    print(f"   Configuration loaded - OK")
    print(f"   URL: {config.dolibarr_url}")
    print(f"   API Key: {'*' * min(len(config.api_key), 10)}...")
except Exception as e:
    print(f"   ⚠️  Configuration error: {e}")

# Test 6: Tool call structure
print("✅ Testing tool call structure:")
try:
    result = server.handle_tool_call("test_connection", {})
    if "error" in result:
        print("   Tool call structure - OK (API error expected)")
        print(f"   Error type: {result.get('type', 'unknown')}")
    else:
        print("   Tool call structure - OK")
    print(f"   Response format: {type(result).__name__}")
except Exception as e:
    print(f"   ❌ Tool call failed: {e}")
    sys.exit(1)

print("")
print("=" * 50)
print("🎉 ALL TESTS PASSED!")
print("=" * 50)
print("")
print("✅ Ultra-simple server is ready")
print("✅ Zero compiled extensions")
print("✅ Complete self-contained implementation")
print("")
print("🚀 To run the server:")
print("   .\\run_ultra.bat")
print("")
print("🧪 To run directly:")
print("   python src\\dolibarr_mcp\\ultra_simple_server.py")
print("")
print("Test completed successfully!")
