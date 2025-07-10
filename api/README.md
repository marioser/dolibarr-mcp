# Dolibarr API Documentation - Complete Analysis
## Instance Information: db.ginos.cloud

**Dolibarr Version:** 21.0.1  
**API Base URL:** https://db.ginos.cloud/api/index.php  
**Authentication:** DOLAPIKEY header  
**Response Format:** JSON

## ✅ Confirmed Working Endpoints

### 1. **Status Endpoint**
- **URL:** `/status`
- **Method:** GET
- **Purpose:** API health check and version info
- **Response:** 
```json
{
  "success": {
    "code": 200,
    "dolibarr_version": "21.0.1",
    "access_locked": "0"
  }
}
```

### 2. **Users Endpoint**
- **URL:** `/users`
- **Method:** GET, POST, PUT, DELETE
- **Purpose:** User management
- **Parameters:** limit, sortfield, sortorder
- **Response:** Array of user objects with complete profile data
- **Fields Include:** id, login, lastname, firstname, email, admin, status, etc.
- **Status:** ✅ Fully functional with 4 users found

### 3. **Third Parties Endpoint** (Customers/Suppliers)
- **URL:** `/thirdparties`
- **Method:** GET, POST, PUT, DELETE
- **Purpose:** Customer/supplier management
- **Parameters:** limit, sortfield, sortorder, sqlfilters
- **Response:** Array of third party objects
- **Fields Include:** id, name, address, phone, email, status, type (client/supplier)
- **Status:** ✅ Fully functional with 1 test customer found

### 4. **Products Endpoint**
- **URL:** `/products`
- **Method:** GET, POST, PUT, DELETE
- **Purpose:** Product catalog management
- **Parameters:** limit, sortfield, sortorder
- **Response:** Array of product objects
- **Status:** ✅ Accessible but currently empty

### 5. **Invoices Endpoint**
- **URL:** `/invoices`
- **Method:** GET, POST, PUT, DELETE
- **Purpose:** Invoice management
- **Parameters:** limit, status filtering
- **Response:** Array of invoice objects
- **Status:** ✅ Accessible but currently empty

### 6. **Orders Endpoint**
- **URL:** `/orders`
- **Method:** GET, POST, PUT, DELETE
- **Purpose:** Order management
- **Parameters:** limit, status filtering
- **Response:** Array of order objects
- **Status:** ✅ Accessible but currently empty

### 7. **Contacts Endpoint**
- **URL:** `/contacts`
- **Method:** GET, POST, PUT, DELETE
- **Purpose:** Contact management
- **Parameters:** limit, thirdparty filtering
- **Response:** Array of contact objects
- **Status:** ✅ Accessible but currently empty

## ❌ Non-Working/Problematic Endpoints

### 1. **Setup Endpoint**
- **URL:** `/setup`
- **Status:** ❌ 404 Not Found
- **Note:** May require different path or parameters

### 2. **Documents Endpoint**
- **URL:** `/documents`
- **Status:** ❌ 400 Bad Request
- **Note:** Requires specific parameters (modulepart, filename, etc.)

## 🔍 API Patterns Identified

### Standard Query Parameters
All list endpoints support these parameters:
- `limit`: Number of records to return (default: 100)
- `sortfield`: Field to sort by
- `sortorder`: ASC or DESC
- `sqlfilters`: Advanced filtering using SQL-like syntax

### Authentication
- **Header:** `DOLAPIKEY: your_api_key`
- **Format:** Token-based authentication
- **Permission:** Tied to user permissions in Dolibarr

### Response Structure
- **Success:** Array of objects or single object
- **Error:** JSON with error details
- **HTTP Status Codes:** 200, 201, 400, 401, 403, 404, 500

### Data Structure Pattern
All business objects share common fields:
- `id`: Unique identifier
- `ref`: Reference number
- `status`/`statut`: Status code
- `date_creation`: Creation timestamp
- `user_creation_id`: Creator user ID
- `note_public`/`note_private`: Notes
- `array_options`: Custom fields

## 🏗️ Recommended MCP Server Structure

### Core Modules
1. **Customer Management** (`/thirdparties`)
   - get_customers()
   - get_customer_by_id()
   - create_customer()
   - update_customer()
   - delete_customer()

2. **Product Management** (`/products`)
   - get_products()
   - get_product_by_id()
   - create_product()
   - update_product()
   - delete_product()

3. **Invoice Management** (`/invoices`)
   - get_invoices()
   - get_invoice_by_id()
   - create_invoice()
   - update_invoice()
   - delete_invoice()

4. **Order Management** (`/orders`)
   - get_orders()
   - get_order_by_id()
   - create_order()
   - update_order()
   - delete_order()

5. **Contact Management** (`/contacts`)
   - get_contacts()
   - get_contact_by_id()
   - create_contact()
   - update_contact()
   - delete_contact()

6. **User Management** (`/users`)
   - get_users()
   - get_user_by_id()
   - create_user()
   - update_user()
   - delete_user()

### Additional Endpoints to Explore
Based on Dolibarr source code, these endpoints likely exist:
- `/projects` - Project management
- `/suppliers` - Supplier-specific operations
- `/warehouses` - Inventory management
- `/categories` - Category management
- `/members` - Membership management
- `/expensereports` - Expense reporting
- `/tickets` - Support tickets
- `/events` - Calendar events
- `/proposals` - Commercial proposals
- `/contracts` - Contract management
- `/agenda` - Agenda/calendar
- `/actioncomm` - Communication actions
- `/shipments` - Shipping management
- `/receptions` - Reception management
- `/mrp` - Manufacturing Resource Planning
- `/boms` - Bill of Materials
- `/stockmovements` - Stock movements
- `/bankaccounts` - Bank account management
- `/payments` - Payment management
- `/leaverequest` - Leave requests
- `/salaries` - Salary management

## 🔬 Testing Methodology Used

1. **Connection Test:** Verified API accessibility with `/status` endpoint
2. **Core Business Objects:** Tested major CRUD endpoints
3. **Parameter Testing:** Verified filtering and pagination
4. **Error Handling:** Documented error responses
5. **Data Structure Analysis:** Analyzed response formats

## 📝 Next Steps for MCP Development

1. **Create Base MCP Server Structure**
   - Follow prestashop-mcp reference pattern
   - Implement dolibarr_client.py with all discovered endpoints
   - Create MCP server with proper tool definitions

2. **Implement Core Functions**
   - Start with working endpoints (users, thirdparties, products, invoices, orders)
   - Add comprehensive error handling
   - Include proper parameter validation

3. **Test and Expand**
   - Test all CRUD operations
   - Discover additional endpoints through testing
   - Add advanced features (filtering, pagination, etc.)

4. **Documentation and Deployment**
   - Create comprehensive README
   - Add Docker containerization
   - Implement proper logging and monitoring

## 🎯 Immediate Development Priority

**High Priority Endpoints (Confirmed Working):**
1. Users management
2. Customer/Third party management  
3. Product management
4. Invoice management
5. Order management

**Medium Priority (Need Parameter Research):**
1. Document management
2. Contact management
3. Project management

**Low Priority (Discovery Required):**
1. Setup/configuration endpoints
2. Advanced modules (MRP, BOM, etc.)
3. Integration-specific endpoints