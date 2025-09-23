"""Professional Dolibarr API client with comprehensive CRUD operations."""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, quote

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from .config import Config


class DolibarrAPIError(Exception):
    """Custom exception for Dolibarr API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class DolibarrClient:
    """Professional Dolibarr API client with comprehensive functionality."""
    
    def __init__(self, config: Config):
        """Initialize the Dolibarr client."""
        self.config = config
        self.base_url = config.dolibarr_url.rstrip('/')
        self.api_key = config.api_key
        self.session: Optional[ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
        # Configure timeout
        self.timeout = ClientTimeout(total=30, connect=10)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session()
    
    async def start_session(self):
        """Start the HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "DOLAPIKEY": self.api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
    
    async def close_session(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _build_url(self, endpoint: str) -> str:
        """Build full API URL."""
        # Remove leading slash from endpoint
        endpoint = endpoint.lstrip('/')
        
        # Special handling for status endpoint
        if endpoint == "status":
            # Try different possible locations for status endpoint
            # Some Dolibarr versions have it at /api/status instead of /api/index.php/status
            base = self.base_url.replace('/index.php', '')
            return f"{base}/status"
        
        # For all other endpoints, use the standard format
        return f"{self.base_url}/{endpoint}"
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Dolibarr API."""
        if not self.session:
            await self.start_session()
        
        url = self._build_url(endpoint)
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            kwargs = {
                "params": params or {},
            }
            
            if data and method.upper() in ["POST", "PUT"]:
                kwargs["json"] = data
            
            async with self.session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                
                # Log response for debugging
                self.logger.debug(f"Response status: {response.status}")
                self.logger.debug(f"Response text: {response_text[:500]}...")
                
                # Try to parse JSON response
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {"raw_response": response_text}
                
                # Handle error responses
                if response.status >= 400:
                    error_msg = f"HTTP {response.status}: {response.reason}"
                    if isinstance(response_data, dict):
                        if "error" in response_data:
                            error_details = response_data["error"]
                            if isinstance(error_details, dict):
                                error_msg = error_details.get("message", error_msg)
                                if "code" in error_details:
                                    error_msg = f"{error_msg} (Code: {error_details['code']})"
                            else:
                                error_msg = str(error_details)
                        elif "message" in response_data:
                            error_msg = response_data["message"]
                    
                    raise DolibarrAPIError(
                        message=error_msg,
                        status_code=response.status,
                        response_data=response_data
                    )
                
                return response_data
                
        except aiohttp.ClientError as e:
            # For status endpoint, try alternative URL if first attempt fails
            if endpoint == "status" and not url.endswith("/api/status"):
                try:
                    # Try with /api/index.php/setup/modules as alternative
                    alt_url = f"{self.base_url}/setup/modules"
                    self.logger.debug(f"Status failed, trying alternative: {alt_url}")
                    
                    async with self.session.get(alt_url) as response:
                        if response.status == 200:
                            # Return a status-like response
                            return {
                                "success": 1,
                                "dolibarr_version": "API Available",
                                "api_version": "1.0"
                            }
                except:
                    pass
            
            raise DolibarrAPIError(f"HTTP client error: {endpoint}")
        except Exception as e:
            if isinstance(e, DolibarrAPIError):
                raise
            raise DolibarrAPIError(f"Unexpected error: {str(e)}")
    
    # ============================================================================
    # SYSTEM ENDPOINTS
    # ============================================================================
    
    async def get_status(self) -> Dict[str, Any]:
        """Get API status and version information."""
        try:
            # First try the standard status endpoint
            return await self._make_request("GET", "status")
        except DolibarrAPIError:
            # If status fails, try to get module list as a connectivity test
            try:
                result = await self._make_request("GET", "setup/modules")
                if result:
                    return {
                        "success": 1,
                        "dolibarr_version": "Connected",
                        "api_version": "1.0",
                        "modules_available": isinstance(result, (list, dict))
                    }
            except:
                pass
            
            # If all else fails, try a simple user list
            try:
                result = await self._make_request("GET", "users?limit=1")
                if result is not None:
                    return {
                        "success": 1,
                        "dolibarr_version": "API Working",
                        "api_version": "1.0"
                    }
            except:
                raise DolibarrAPIError("Cannot connect to Dolibarr API. Please check your configuration.")
    
    # ============================================================================
    # USER MANAGEMENT
    # ============================================================================
    
    async def get_users(self, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of users."""
        params = {"limit": limit}
        if page > 1:
            params["page"] = page
        
        result = await self._make_request("GET", "users", params=params)
        return result if isinstance(result, list) else []
    
    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get specific user by ID."""
        return await self._make_request("GET", f"users/{user_id}")
    
    async def create_user(self, **kwargs) -> Dict[str, Any]:
        """Create a new user."""
        return await self._make_request("POST", "users", data=kwargs)
    
    async def update_user(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing user."""
        return await self._make_request("PUT", f"users/{user_id}", data=kwargs)
    
    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete a user."""
        return await self._make_request("DELETE", f"users/{user_id}")
    
    # ============================================================================
    # CUSTOMER/THIRD PARTY MANAGEMENT
    # ============================================================================
    
    async def get_customers(self, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of customers/third parties."""
        params = {"limit": limit}
        if page > 1:
            params["page"] = page
        
        result = await self._make_request("GET", "thirdparties", params=params)
        return result if isinstance(result, list) else []
    
    async def get_customer_by_id(self, customer_id: int) -> Dict[str, Any]:
        """Get specific customer by ID."""
        return await self._make_request("GET", f"thirdparties/{customer_id}")
    
    async def create_customer(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        town: Optional[str] = None,
        zip: Optional[str] = None,
        country_id: int = 1,
        type: int = 1,  # 1=Customer, 2=Supplier, 3=Both
        status: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new customer/third party."""
        data = {
            "name": name,
            "status": status,
            "client": type if type in [1, 3] else 0,
            "fournisseur": 1 if type in [2, 3] else 0,
            "country_id": country_id,
            **kwargs
        }
        
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        if address:
            data["address"] = address
        if town:
            data["town"] = town
        if zip:
            data["zip"] = zip
        
        return await self._make_request("POST", "thirdparties", data=data)
    
    async def update_customer(self, customer_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing customer."""
        return await self._make_request("PUT", f"thirdparties/{customer_id}", data=kwargs)
    
    async def delete_customer(self, customer_id: int) -> Dict[str, Any]:
        """Delete a customer."""
        return await self._make_request("DELETE", f"thirdparties/{customer_id}")
    
    # ============================================================================
    # PRODUCT MANAGEMENT
    # ============================================================================
    
    async def get_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of products."""
        params = {"limit": limit}
        result = await self._make_request("GET", "products", params=params)
        return result if isinstance(result, list) else []
    
    async def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get specific product by ID."""
        return await self._make_request("GET", f"products/{product_id}")
    
    async def create_product(
        self,
        label: str,
        price: float,
        ref: Optional[str] = None,  # Product reference/SKU
        description: Optional[str] = None,
        stock: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new product.
        
        Args:
            label: Product name/label
            price: Product price
            ref: Product reference/SKU (required by Dolibarr, auto-generated if not provided)
            description: Product description
            stock: Initial stock quantity
            **kwargs: Additional product fields
        """
        import time
        
        # Generate ref if not provided (required field in Dolibarr)
        if ref is None:
            ref = f"PROD-{int(time.time())}"
        
        data = {
            "ref": ref,  # Required field
            "label": label,
            "price": price,
            "price_ttc": price,  # Price including tax (using same as price for simplicity)
            **kwargs
        }
        
        if description:
            data["description"] = description
        if stock is not None:
            data["stock"] = stock
        
        return await self._make_request("POST", "products", data=data)
    
    async def update_product(self, product_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing product."""
        return await self._make_request("PUT", f"products/{product_id}", data=kwargs)
    
    async def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete a product."""
        return await self._make_request("DELETE", f"products/{product_id}")
    
    # ============================================================================
    # INVOICE MANAGEMENT
    # ============================================================================
    
    async def get_invoices(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of invoices."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = await self._make_request("GET", "invoices", params=params)
        return result if isinstance(result, list) else []
    
    async def get_invoice_by_id(self, invoice_id: int) -> Dict[str, Any]:
        """Get specific invoice by ID."""
        return await self._make_request("GET", f"invoices/{invoice_id}")
    
    async def create_invoice(
        self,
        customer_id: int,
        lines: List[Dict[str, Any]],
        date: Optional[str] = None,
        due_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new invoice."""
        data = {
            "socid": customer_id,
            "lines": lines,
            **kwargs
        }
        
        if date:
            data["date"] = date
        if due_date:
            data["due_date"] = due_date
        
        return await self._make_request("POST", "invoices", data=data)
    
    async def update_invoice(self, invoice_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing invoice."""
        return await self._make_request("PUT", f"invoices/{invoice_id}", data=kwargs)
    
    async def delete_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Delete an invoice."""
        return await self._make_request("DELETE", f"invoices/{invoice_id}")
    
    # ============================================================================
    # ORDER MANAGEMENT
    # ============================================================================
    
    async def get_orders(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of orders."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = await self._make_request("GET", "orders", params=params)
        return result if isinstance(result, list) else []
    
    async def get_order_by_id(self, order_id: int) -> Dict[str, Any]:
        """Get specific order by ID."""
        return await self._make_request("GET", f"orders/{order_id}")
    
    async def create_order(self, customer_id: int, **kwargs) -> Dict[str, Any]:
        """Create a new order."""
        data = {"socid": customer_id, **kwargs}
        return await self._make_request("POST", "orders", data=data)
    
    async def update_order(self, order_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing order."""
        return await self._make_request("PUT", f"orders/{order_id}", data=kwargs)
    
    async def delete_order(self, order_id: int) -> Dict[str, Any]:
        """Delete an order."""
        return await self._make_request("DELETE", f"orders/{order_id}")
    
    # ============================================================================
    # CONTACT MANAGEMENT
    # ============================================================================
    
    async def get_contacts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of contacts."""
        params = {"limit": limit}
        result = await self._make_request("GET", "contacts", params=params)
        return result if isinstance(result, list) else []
    
    async def get_contact_by_id(self, contact_id: int) -> Dict[str, Any]:
        """Get specific contact by ID."""
        return await self._make_request("GET", f"contacts/{contact_id}")
    
    async def create_contact(self, **kwargs) -> Dict[str, Any]:
        """Create a new contact."""
        return await self._make_request("POST", "contacts", data=kwargs)
    
    async def update_contact(self, contact_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing contact."""
        return await self._make_request("PUT", f"contacts/{contact_id}", data=kwargs)
    
    async def delete_contact(self, contact_id: int) -> Dict[str, Any]:
        """Delete a contact."""
        return await self._make_request("DELETE", f"contacts/{contact_id}")
    
    # ============================================================================
    # RAW API CALL
    # ============================================================================
    
    async def dolibarr_raw_api(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make raw API call to any Dolibarr endpoint."""
        return await self._make_request(method, endpoint, params=params, data=data)
