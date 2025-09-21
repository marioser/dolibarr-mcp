#!/usr/bin/env python3
"""
Test script for Dolibarr MCP Server
Tests all CRUD operations and API connectivity
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.dolibarr_mcp.config import Config
from src.dolibarr_mcp.dolibarr_client import DolibarrClient, DolibarrAPIError


async def test_connection(client):
    """Test basic API connection."""
    print("\n1. Testing API Connection...")
    try:
        result = await client.get_status()
        print("✅ API Connection successful")
        print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def test_customer_crud(client):
    """Test Customer CRUD operations."""
    print("\n2. Testing Customer CRUD Operations...")
    
    try:
        # CREATE
        print("   Creating customer...")
        customer = await client.create_customer(
            name="Test Company MCP",
            email="test@mcp-example.com",
            phone="+1234567890",
            address="123 Test Street",
            town="Test City",
            zip="12345"
        )
        customer_id = customer.get('id') or customer.get('rowid')
        print(f"   ✅ Created customer ID: {customer_id}")
        
        # READ
        print("   Reading customer...")
        retrieved = await client.get_customer_by_id(customer_id)
        print(f"   ✅ Retrieved customer: {retrieved.get('name')}")
        
        # UPDATE
        print("   Updating customer...")
        updated = await client.update_customer(
            customer_id,
            email="updated@mcp-example.com"
        )
        print(f"   ✅ Updated customer")
        
        # DELETE
        print("   Deleting customer...")
        await client.delete_customer(customer_id)
        print(f"   ✅ Deleted customer")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Customer CRUD failed: {e}")
        return False


async def test_product_crud(client):
    """Test Product CRUD operations."""
    print("\n3. Testing Product CRUD Operations...")
    
    try:
        # CREATE
        print("   Creating product...")
        product = await client.create_product(
            label="Test Product MCP",
            price=99.99,
            description="A test product created via MCP",
            stock=100
        )
        product_id = product.get('id') or product.get('rowid')
        print(f"   ✅ Created product ID: {product_id}")
        
        # READ
        print("   Reading product...")
        retrieved = await client.get_product_by_id(product_id)
        print(f"   ✅ Retrieved product: {retrieved.get('label')}")
        
        # UPDATE
        print("   Updating product...")
        updated = await client.update_product(
            product_id,
            price=149.99
        )
        print(f"   ✅ Updated product price")
        
        # DELETE
        print("   Deleting product...")
        await client.delete_product(product_id)
        print(f"   ✅ Deleted product")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Product CRUD failed: {e}")
        return False


async def test_list_operations(client):
    """Test listing operations."""
    print("\n4. Testing List Operations...")
    
    try:
        # List users
        print("   Listing users...")
        users = await client.get_users(limit=5)
        print(f"   ✅ Found {len(users)} users")
        
        # List customers
        print("   Listing customers...")
        customers = await client.get_customers(limit=5)
        print(f"   ✅ Found {len(customers)} customers")
        
        # List products
        print("   Listing products...")
        products = await client.get_products(limit=5)
        print(f"   ✅ Found {len(products)} products")
        
        # List invoices
        print("   Listing invoices...")
        invoices = await client.get_invoices(limit=5)
        print(f"   ✅ Found {len(invoices)} invoices")
        
        # List orders
        print("   Listing orders...")
        orders = await client.get_orders(limit=5)
        print(f"   ✅ Found {len(orders)} orders")
        
        # List contacts
        print("   Listing contacts...")
        contacts = await client.get_contacts(limit=5)
        print(f"   ✅ Found {len(contacts)} contacts")
        
        return True
        
    except Exception as e:
        print(f"   ❌ List operations failed: {e}")
        return False


async def test_raw_api(client):
    """Test raw API access."""
    print("\n5. Testing Raw API Access...")
    
    try:
        # Make a raw API call
        print("   Making raw API call to /users endpoint...")
        result = await client.dolibarr_raw_api(
            method="GET",
            endpoint="/users",
            params={"limit": 2}
        )
        print(f"   ✅ Raw API call successful")
        print(f"   Response type: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Raw API call failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 DOLIBARR MCP SERVER TEST SUITE")
    print("=" * 60)
    
    try:
        # Load configuration
        print("\n📋 Loading configuration...")
        config = Config()
        print(f"   API URL: {config.dolibarr_url}")
        print(f"   API Key: {'*' * 10 if config.api_key else 'NOT SET'}")
        
        if not config.api_key or config.api_key == "your_api_key_here":
            print("\n❌ ERROR: Please configure your Dolibarr API credentials in .env file")
            print("   Required variables:")
            print("   - DOLIBARR_URL: Your Dolibarr instance URL")
            print("   - DOLIBARR_API_KEY: Your API key")
            return
        
        # Create client and run tests
        async with DolibarrClient(config) as client:
            tests_passed = 0
            tests_total = 5
            
            # Run test suite
            if await test_connection(client):
                tests_passed += 1
            
            if await test_customer_crud(client):
                tests_passed += 1
            
            if await test_product_crud(client):
                tests_passed += 1
            
            if await test_list_operations(client):
                tests_passed += 1
            
            if await test_raw_api(client):
                tests_passed += 1
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)
            print(f"Tests Passed: {tests_passed}/{tests_total}")
            
            if tests_passed == tests_total:
                print("✅ ALL TESTS PASSED! The Dolibarr MCP Server is fully operational.")
            elif tests_passed > 0:
                print(f"⚠️ PARTIAL SUCCESS: {tests_passed} tests passed, {tests_total - tests_passed} failed.")
            else:
                print("❌ ALL TESTS FAILED. Please check your configuration and API access.")
            
            print("\n📌 Next Steps:")
            print("1. If all tests passed, your MCP server is ready for production use")
            print("2. Run the server: python -m dolibarr_mcp.dolibarr_mcp_server")
            print("3. Or use Docker: docker-compose up")
            print("4. Connect your AI assistant to the MCP server")
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
