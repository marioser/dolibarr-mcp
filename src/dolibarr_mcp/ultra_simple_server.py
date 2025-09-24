"""Ultra-simple Dolibarr server - COMPLETELY SELF-CONTAINED - Zero external dependencies issues."""

import json
import sys
import os
import logging
from typing import Any, Dict, List, Optional

# EVERYTHING is self-contained in this single file to avoid import issues

# ============================================================================
# SELF-CONTAINED CONFIGURATION CLASS
# ============================================================================

class UltraSimpleConfig:
    """Ultra-simple configuration - completely self-contained."""
    
    def __init__(self):
        # Load .env manually
        self.load_env()
        
        self.dolibarr_url = os.getenv("DOLIBARR_URL", "")
        self.api_key = os.getenv("DOLIBARR_API_KEY", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Validate and fix URL
        if not self.dolibarr_url or "your-dolibarr-instance" in self.dolibarr_url:
            print("⚠️  DOLIBARR_URL not configured in .env file", file=sys.stderr)
            self.dolibarr_url = "https://your-dolibarr-instance.com/api/index.php"
        
        if not self.api_key or "your_dolibarr_api_key" in self.api_key:
            print("⚠️  DOLIBARR_API_KEY not configured in .env file", file=sys.stderr)
            self.api_key = "placeholder_api_key"
        
        # Ensure URL format
        if self.dolibarr_url and not self.dolibarr_url.endswith('/api/index.php'):
            if '/api' not in self.dolibarr_url:
                self.dolibarr_url = self.dolibarr_url.rstrip('/') + '/api/index.php'
            elif not self.dolibarr_url.endswith('/index.php'):
                self.dolibarr_url = self.dolibarr_url.rstrip('/') + '/index.php'
    
    def load_env(self):
        """Load .env file manually - no python-dotenv needed."""
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

# ============================================================================
# SELF-CONTAINED API CLIENT
# ============================================================================

class UltraSimpleAPIError(Exception):
    """Simple API error exception."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UltraSimpleAPIClient:
    """Ultra-simple Dolibarr client - completely self-contained."""
    
    def __init__(self, config: UltraSimpleConfig):
        self.config = config
        self.base_url = config.dolibarr_url.rstrip('/')
        self.api_key = config.api_key
        self.logger = logging.getLogger(__name__)
        
        # We'll use requests when needed, imported inside methods
        
    def _build_url(self, endpoint: str) -> str:
        """Build full API URL."""
        endpoint = endpoint.lstrip('/')
        
        # Special handling for status endpoint
        if endpoint == "status":
            base = self.base_url.replace('/index.php', '')
            return f"{base}/status"
        
        return f"{self.base_url}/{endpoint}"
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Dolibarr API."""
        # Import requests here to avoid import issues
        try:
            import requests
        except ImportError:
            raise UltraSimpleAPIError("requests library not available. Please run setup_ultra.bat")
        
        url = self._build_url(endpoint)
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            headers = {
                "DOLAPIKEY": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Dolibarr-MCP-Ultra/1.0"
            }
            
            kwargs = {
                "params": params or {},
                "timeout": 30,
                "headers": headers
            }
            
            if data and method.upper() in ["POST", "PUT"]:
                kwargs["json"] = data
            
            response = requests.request(method, url, **kwargs)
            
            # Handle error responses
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "error" in error_data:
                        error_msg = str(error_data["error"])
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.reason}"
                except:
                    error_msg = f"HTTP {response.status_code}: {response.reason}"
                
                raise UltraSimpleAPIError(error_msg, response.status_code)
            
            # Try to parse JSON response
            try:
                return response.json()
            except:
                return {"raw_response": response.text}
        
        except requests.RequestException as e:
            # For status endpoint, try alternative
            if endpoint == "status":
                try:
                    alt_url = f"{self.base_url.replace('/api/index.php', '')}/setup/modules"
                    alt_response = requests.get(alt_url, headers=headers, timeout=10)
                    if alt_response.status_code == 200:
                        return {
                            "success": 1,
                            "dolibarr_version": "API Available",
                            "api_version": "1.0"
                        }
                except:
                    pass
            
            raise UltraSimpleAPIError(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise UltraSimpleAPIError(f"Unexpected error: {str(e)}")
    
    # API Methods
    def get_status(self) -> Dict[str, Any]:
        """Get API status."""
        try:
            return self._make_request("GET", "status")
        except UltraSimpleAPIError:
            try:
                result = self._make_request("GET", "users?limit=1")
                if result is not None:
                    return {
                        "success": 1,
                        "dolibarr_version": "API Working",
                        "api_version": "1.0"
                    }
            except:
                pass
            raise UltraSimpleAPIError("Cannot connect to Dolibarr API. Please check your configuration.")
    
    def get_users(self, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of users."""
        params = {"limit": limit}
        if page > 1:
            params["page"] = page
        result = self._make_request("GET", "users", params=params)
        return result if isinstance(result, list) else []
    
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get specific user by ID."""
        return self._make_request("GET", f"users/{user_id}")
    
    def create_user(self, **kwargs) -> Dict[str, Any]:
        """Create a new user."""
        return self._make_request("POST", "users", data=kwargs)
    
    def update_user(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing user."""
        return self._make_request("PUT", f"users/{user_id}", data=kwargs)
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete a user."""
        return self._make_request("DELETE", f"users/{user_id}")
    
    def get_customers(self, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of customers."""
        params = {"limit": limit}
        if page > 1:
            params["page"] = page
        result = self._make_request("GET", "thirdparties", params=params)
        return result if isinstance(result, list) else []
    
    def get_customer_by_id(self, customer_id: int) -> Dict[str, Any]:
        """Get specific customer by ID."""
        return self._make_request("GET", f"thirdparties/{customer_id}")
    
    def create_customer(self, name: str, **kwargs) -> Dict[str, Any]:
        """Create a new customer."""
        data = {
            "name": name,
            "status": kwargs.get("status", 1),
            "client": 1 if kwargs.get("type", 1) in [1, 3] else 0,
            "fournisseur": 1 if kwargs.get("type", 1) in [2, 3] else 0,
            "country_id": kwargs.get("country_id", 1),
        }
        for field in ["email", "phone", "address", "town", "zip"]:
            if field in kwargs:
                data[field] = kwargs[field]
        return self._make_request("POST", "thirdparties", data=data)
    
    def update_customer(self, customer_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing customer."""
        return self._make_request("PUT", f"thirdparties/{customer_id}", data=kwargs)
    
    def delete_customer(self, customer_id: int) -> Dict[str, Any]:
        """Delete a customer."""
        return self._make_request("DELETE", f"thirdparties/{customer_id}")
    
    def get_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of products."""
        params = {"limit": limit}
        result = self._make_request("GET", "products", params=params)
        return result if isinstance(result, list) else []
    
    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get specific product by ID."""
        return self._make_request("GET", f"products/{product_id}")
    
    def create_product(self, label: str, price: float, **kwargs) -> Dict[str, Any]:
        """Create a new product."""
        import time
        ref = kwargs.get("ref", f"PROD-{int(time.time())}")
        data = {
            "ref": ref,
            "label": label,
            "price": price,
            "price_ttc": price,
        }
        for field in ["description", "stock"]:
            if field in kwargs:
                data[field] = kwargs[field]
        return self._make_request("POST", "products", data=data)
    
    def update_product(self, product_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing product."""
        return self._make_request("PUT", f"products/{product_id}", data=kwargs)
    
    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete a product."""
        return self._make_request("DELETE", f"products/{product_id}")
    
    def raw_api(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make raw API call."""
        return self._make_request(method, endpoint, params=params, data=data)

# ============================================================================
# ULTRA-SIMPLE SERVER
# ============================================================================

class UltraSimpleServer:
    """Ultra-simple server - completely self-contained."""
    
    def __init__(self, name: str = "dolibarr-mcp-ultra"):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.client = None
        
    def init_client(self):
        """Initialize the Dolibarr client."""
        if not self.client:
            config = UltraSimpleConfig()
            self.client = UltraSimpleAPIClient(config)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [
            "test_connection", "get_status", "get_users", "get_user_by_id",
            "create_user", "update_user", "delete_user", "get_customers",
            "get_customer_by_id", "create_customer", "update_customer",
            "delete_customer", "get_products", "get_product_by_id",
            "create_product", "update_product", "delete_product", "raw_api"
        ]
    
    def handle_tool_call(self, tool_name: str, arguments: dict) -> Dict[str, Any]:
        """Handle tool calls."""
        try:
            self.init_client()
            
            if tool_name == "test_connection":
                result = self.client.get_status()
                if 'success' not in result:
                    result = {"status": "success", "message": "API connection working", "data": result}
                return {"success": True, "data": result}
            elif tool_name == "get_status":
                result = self.client.get_status()
                return {"success": True, "data": result}
            elif tool_name == "get_users":
                result = self.client.get_users(
                    limit=arguments.get('limit', 100),
                    page=arguments.get('page', 1)
                )
                return {"success": True, "data": result}
            elif tool_name == "get_user_by_id":
                result = self.client.get_user_by_id(arguments['user_id'])
                return {"success": True, "data": result}
            elif tool_name == "create_user":
                result = self.client.create_user(**arguments)
                return {"success": True, "data": result}
            elif tool_name == "update_user":
                user_id = arguments.pop('user_id')
                result = self.client.update_user(user_id, **arguments)
                return {"success": True, "data": result}
            elif tool_name == "delete_user":
                result = self.client.delete_user(arguments['user_id'])
                return {"success": True, "data": result}
            elif tool_name == "get_customers":
                result = self.client.get_customers(
                    limit=arguments.get('limit', 100),
                    page=arguments.get('page', 1)
                )
                return {"success": True, "data": result}
            elif tool_name == "get_customer_by_id":
                result = self.client.get_customer_by_id(arguments['customer_id'])
                return {"success": True, "data": result}
            elif tool_name == "create_customer":
                result = self.client.create_customer(**arguments)
                return {"success": True, "data": result}
            elif tool_name == "update_customer":
                customer_id = arguments.pop('customer_id')
                result = self.client.update_customer(customer_id, **arguments)
                return {"success": True, "data": result}
            elif tool_name == "delete_customer":
                result = self.client.delete_customer(arguments['customer_id'])
                return {"success": True, "data": result}
            elif tool_name == "get_products":
                result = self.client.get_products(limit=arguments.get('limit', 100))
                return {"success": True, "data": result}
            elif tool_name == "get_product_by_id":
                result = self.client.get_product_by_id(arguments['product_id'])
                return {"success": True, "data": result}
            elif tool_name == "create_product":
                result = self.client.create_product(**arguments)
                return {"success": True, "data": result}
            elif tool_name == "update_product":
                product_id = arguments.pop('product_id')
                result = self.client.update_product(product_id, **arguments)
                return {"success": True, "data": result}
            elif tool_name == "delete_product":
                result = self.client.delete_product(arguments['product_id'])
                return {"success": True, "data": result}
            elif tool_name == "raw_api":
                result = self.client.raw_api(**arguments)
                return {"success": True, "data": result}
            else:
                return {"error": f"Unknown tool: {tool_name}", "type": "unknown_tool"}
        
        except UltraSimpleAPIError as e:
            return {"error": f"Dolibarr API Error: {str(e)}", "type": "api_error"}
        except Exception as e:
            self.logger.error(f"Tool execution error: {e}")
            return {"error": f"Tool execution failed: {str(e)}", "type": "internal_error"}
    
    def format_response(self, content: Dict[str, Any]) -> str:
        """Format response as JSON string."""
        return json.dumps(content, indent=2, ensure_ascii=False)
    
    def run_interactive(self):
        """Run server in interactive mode."""
        print("🚀 Ultra-Simple Dolibarr MCP Server (Maximum Windows Compatibility)", file=sys.stderr)
        print("✅ ZERO compiled extensions - NO .pyd files!", file=sys.stderr)
        print("✅ Completely self-contained - no import issues!", file=sys.stderr)
        print("", file=sys.stderr)
        
        # Test configuration
        try:
            config = UltraSimpleConfig()
            
            if "your-dolibarr-instance" in config.dolibarr_url:
                print("⚠️  DOLIBARR_URL not configured in .env file", file=sys.stderr)
                print("📝 Please edit .env with your Dolibarr credentials", file=sys.stderr)
            elif "placeholder_api_key" in config.api_key:
                print("⚠️  DOLIBARR_API_KEY not configured in .env file", file=sys.stderr)
                print("📝 Please edit .env with your Dolibarr API key", file=sys.stderr)
            else:
                print("🧪 Testing Dolibarr API connection...", file=sys.stderr)
                test_result = self.handle_tool_call("test_connection", {})
                if test_result.get("success"):
                    print("✅ Dolibarr API connection successful!", file=sys.stderr)
                else:
                    print(f"⚠️  API test result: {test_result}", file=sys.stderr)
                    
        except Exception as e:
            print(f"⚠️  Configuration error: {e}", file=sys.stderr)
        
        print("", file=sys.stderr)
        print("📋 Available Tools:", file=sys.stderr)
        tools = self.get_available_tools()
        for i, tool in enumerate(tools, 1):
            print(f"  {i:2}. {tool}", file=sys.stderr)
        
        print("", file=sys.stderr)
        print("💡 Interactive Testing Mode:", file=sys.stderr)
        print("   Type 'list' to see all tools", file=sys.stderr)
        print("   Type 'test <tool_name>' to test a tool", file=sys.stderr)
        print("   Type 'help' for more commands", file=sys.stderr)
        print("   Type 'exit' to quit", file=sys.stderr)
        print("", file=sys.stderr)
        
        while True:
            try:
                command = input("dolibarr-ultra> ").strip()
                
                if command == "exit":
                    break
                elif command == "list":
                    print("Available tools:")
                    for i, tool in enumerate(tools, 1):
                        print(f"  {i:2}. {tool}")
                elif command == "help":
                    print("Commands:")
                    print("  list                    - Show all available tools")
                    print("  test <tool_name>        - Test a specific tool")
                    print("  config                  - Show current configuration")
                    print("  exit                    - Quit the server")
                    print("")
                    print("Quick tests available:")
                    print("  test test_connection    - Test API connection")
                    print("  test get_status         - Get Dolibarr status")
                    print("  test get_users          - Get first 5 users")
                    print("  test get_customers      - Get first 5 customers")
                    print("  test get_products       - Get first 5 products")
                elif command == "config":
                    config = UltraSimpleConfig()
                    print(f"Configuration:")
                    print(f"  URL: {config.dolibarr_url}")
                    print(f"  API Key: {'*' * min(len(config.api_key), 10)}...")
                    print(f"  Log Level: {config.log_level}")
                elif command.startswith("test "):
                    tool_name = command[5:].strip()
                    
                    if tool_name == "test_connection":
                        result = self.handle_tool_call("test_connection", {})
                    elif tool_name == "get_status":
                        result = self.handle_tool_call("get_status", {})
                    elif tool_name == "get_users":
                        result = self.handle_tool_call("get_users", {"limit": 5})
                    elif tool_name == "get_customers":
                        result = self.handle_tool_call("get_customers", {"limit": 5})
                    elif tool_name == "get_products":
                        result = self.handle_tool_call("get_products", {"limit": 5})
                    else:
                        if tool_name in tools:
                            print(f"Tool '{tool_name}' requires parameters. Try one of the quick tests:")
                            print("  test_connection, get_status, get_users, get_customers, get_products")
                        else:
                            print(f"Unknown tool: {tool_name}")
                        continue
                    
                    print(self.format_response(result))
                elif command:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n👋 Goodbye!")

def main():
    """Main entry point."""
    server = UltraSimpleServer("dolibarr-mcp-ultra")
    server.run_interactive()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)
