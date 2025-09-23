#!/usr/bin/env python3
"""Test script to verify Dolibarr API connection."""

import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_dolibarr_connection():
    """Test Dolibarr API connection with different endpoints."""
    
    # Get configuration from environment
    base_url = os.getenv("DOLIBARR_URL", "")
    api_key = os.getenv("DOLIBARR_API_KEY", "")
    
    print("🔧 Configuration:")
    print(f"   Base URL: {base_url}")
    print(f"   API Key: {'*' * 10 if api_key else 'NOT SET'}")
    print()
    
    if not base_url or not api_key:
        print("❌ Missing configuration!")
        print("   Please set DOLIBARR_URL and DOLIBARR_API_KEY in .env file")
        return False
    
    # Ensure URL format is correct
    if not base_url.endswith('/api/index.php'):
        if base_url.endswith('/'):
            base_url = base_url + 'api/index.php'
        else:
            base_url = base_url + '/api/index.php'
    
    # Test different endpoints
    endpoints_to_test = [
        "/status",
        "/explorer/swagger",  # Swagger documentation
        "/setup/modules",     # Module list
        "/users",            # Users list
        "/thirdparties",     # Customers/Suppliers
    ]
    
    # Headers for Dolibarr API
    headers = {
        "DOLAPIKEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🧪 Testing Dolibarr API endpoints:")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            # Clean endpoint
            endpoint = endpoint.lstrip('/')
            
            # Build full URL
            if endpoint in ["status", "explorer/swagger"]:
                # These endpoints might be at root level
                test_urls = [
                    f"{base_url}/{endpoint}",
                    f"{base_url.replace('/api/index.php', '')}/{endpoint}",
                    f"{base_url.replace('/api/index.php', '/api')}/{endpoint}"
                ]
            else:
                test_urls = [f"{base_url}/{endpoint}"]
            
            success = False
            for url in test_urls:
                try:
                    print(f"\n📍 Testing: {url}")
                    
                    async with session.get(url, headers=headers, timeout=10) as response:
                        status = response.status
                        text = await response.text()
                        
                        print(f"   Status: {status}")
                        
                        if status == 200:
                            print(f"   ✅ Success!")
                            if text:
                                # Try to parse response
                                try:
                                    import json
                                    data = json.loads(text)
                                    if isinstance(data, dict):
                                        print(f"   Response keys: {list(data.keys())[:5]}")
                                    elif isinstance(data, list):
                                        print(f"   Response: List with {len(data)} items")
                                except:
                                    print(f"   Response preview: {text[:100]}...")
                            success = True
                            break
                        elif status == 401:
                            print(f"   ❌ Authentication failed - check API key")
                        elif status == 403:
                            print(f"   ❌ Access forbidden - check permissions")
                        elif status == 404:
                            print(f"   ❌ Endpoint not found")
                        else:
                            print(f"   ⚠️ Unexpected status: {status}")
                            print(f"   Response: {text[:200]}...")
                            
                except aiohttp.ClientError as e:
                    print(f"   ❌ Connection error: {e}")
                except Exception as e:
                    print(f"   ❌ Unexpected error: {e}")
            
            if success:
                print(f"   ✨ Endpoint {endpoint} is working!")
            else:
                print(f"   ⚠️ Endpoint {endpoint} not accessible")
    
    print("\n" + "=" * 50)
    print("\n📝 Recommendations:")
    print("1. Check if Dolibarr Web Services API REST module is enabled")
    print("2. Verify API key is correct and has proper permissions")
    print("3. Ensure URL format: https://domain.com/api/index.php")
    
    return True


async def test_swagger_discovery():
    """Try to discover API endpoints via Swagger/OpenAPI."""
    
    base_url = os.getenv("DOLIBARR_URL", "")
    api_key = os.getenv("DOLIBARR_API_KEY", "")
    
    if not base_url or not api_key:
        return
    
    print("\n🔍 Attempting Swagger/OpenAPI discovery:")
    print("=" * 50)
    
    headers = {
        "DOLAPIKEY": api_key,
        "Accept": "application/json"
    }
    
    # Possible Swagger/OpenAPI URLs
    swagger_urls = [
        base_url.replace('/api/index.php', '/api/explorer'),
        base_url.replace('/api/index.php', '/api/swagger.json'),
        base_url.replace('/api/index.php', '/api/openapi.json'),
        base_url.replace('/api/index.php', '/api/v2/swagger.json'),
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in swagger_urls:
            try:
                print(f"Testing: {url}")
                async with session.get(url, headers=headers, timeout=5) as response:
                    if response.status == 200:
                        print(f"✅ Found API documentation at: {url}")
                        break
            except:
                pass


if __name__ == "__main__":
    print("🚀 Dolibarr API Connection Test")
    print("================================\n")
    
    try:
        asyncio.run(test_dolibarr_connection())
        asyncio.run(test_swagger_discovery())
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
