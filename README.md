# Dolibarr MCP Server

A professional Model Context Protocol (MCP) Server for complete management of Dolibarr ERP/CRM systems.

## 🚀 Overview

This MCP Server enables complete management of your Dolibarr ERP/CRM through AI applications like Claude Desktop. With specialized tools, you can manage all aspects of your business - from customers and products to invoices, orders, and contacts.

## ✨ Features

- **💼 Complete ERP/CRM Management** - Tools for all business areas
- **👥 Customer & Contact Management** - Full CRM functionality
- **📦 Product & Service Management** - Complete inventory control
- **💰 Financial Management** - Invoices, orders, and payments
- **🏗️ MCP Protocol Compliance** for seamless AI integration
- **⚡ Async/Await Architecture** for maximum performance
- **🛡️ Comprehensive Error Handling** and validation
- **🔧 Production-Ready** with complete test suite
- **🐳 Docker Support** for easy deployment

## 🛠️ Available Tools

### 👥 Customer Management (Third Parties)
- `get_customers` - Retrieve and filter customers
- `get_customer_by_id` - Get specific customer details
- `create_customer` - Create new customers
- `update_customer` - Edit customer data
- `delete_customer` - Remove customers

### 📦 Product Management
- `get_products` - List all products
- `get_product_by_id` - Get specific product details
- `create_product` - Create new products/services
- `update_product` - Edit product information
- `delete_product` - Remove products

### 💰 Invoice Management
- `get_invoices` - Retrieve and filter invoices
- `get_invoice_by_id` - Get specific invoice details
- `create_invoice` - Create new invoices
- `update_invoice` - Edit invoice information
- `delete_invoice` - Remove invoices

### 📋 Order Management
- `get_orders` - Retrieve and filter orders
- `get_order_by_id` - Get specific order details
- `create_order` - Create new orders
- `update_order` - Edit order information
- `delete_order` - Remove orders

### 👤 Contact Management
- `get_contacts` - List all contacts
- `get_contact_by_id` - Get specific contact details
- `create_contact` - Create new contacts
- `update_contact` - Edit contact information
- `delete_contact` - Remove contacts

### 👤 User Management
- `get_users` - List system users
- `get_user_by_id` - Get specific user details
- `create_user` - Create new users
- `update_user` - Edit user information
- `delete_user` - Remove users

### ⚙️ System Administration
- `test_connection` - Test API connection
- `get_status` - System status and version
- `dolibarr_raw_api` - Direct API access for advanced operations

## 📋 Installation

### ⚠️ Recommended Installation (Virtual Environment)

**This approach prevents module conflicts and ensures reliable installation:**

#### Windows:
```powershell
# Clone repository
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp

# Create virtual environment
python -m venv venv_dolibarr

# Activate virtual environment
.\venv_dolibarr\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Verify installation
python -c "import dolibarr_mcp; print('✅ Installation successful')"

# Note the Python path for Claude Desktop configuration
Write-Host "Python Path: $((Get-Command python).Source)"
```

#### Linux/macOS:
```bash
# Clone repository
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp

# Create virtual environment
python3 -m venv venv_dolibarr

# Activate virtual environment
source venv_dolibarr/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Verify installation
python -c "import dolibarr_mcp; print('✅ Installation successful')"

# Note the Python path for Claude Desktop configuration
which python
```

### 🐳 Docker Installation

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or using Docker directly
docker build -t dolibarr-mcp .
docker run -d \
  -e DOLIBARR_URL=https://your-dolibarr.com \
  -e DOLIBARR_API_KEY=your_api_key \
  -p 8080:8080 \
  dolibarr-mcp
```

### ⚙️ Configuration

Create a `.env` file based on `.env.example`:

```bash
# Dolibarr Configuration
DOLIBARR_URL=https://your-dolibarr.example.com
DOLIBARR_API_KEY=YOUR_API_KEY

# Logging
LOG_LEVEL=INFO
```

## 🎯 Usage

### 🤖 With Claude Desktop

#### Using Virtual Environment (Recommended)

Add this configuration to `claude_desktop_config.json`:

**Windows:**
```json
{
  "mcpServers": {
    "dolibarr": {
      "command": "C:\\\\path\\\\to\\\\dolibarr-mcp\\\\venv_dolibarr\\\\Scripts\\\\python.exe",
      "args": ["-m", "dolibarr_mcp.dolibarr_mcp_server"],
      "cwd": "C:\\\\path\\\\to\\\\dolibarr-mcp",
      "env": {
        "DOLIBARR_URL": "https://your-dolibarr.example.com",
        "DOLIBARR_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

**Linux/macOS:**
```json
{
  "mcpServers": {
    "dolibarr": {
      "command": "/path/to/dolibarr-mcp/venv_dolibarr/bin/python",
      "args": ["-m", "dolibarr_mcp.dolibarr_mcp_server"],
      "cwd": "/path/to/dolibarr-mcp",
      "env": {
        "DOLIBARR_URL": "https://your-dolibarr.example.com",
        "DOLIBARR_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

### 💻 CLI Usage

```bash
# Activate virtual environment first (if using venv)
source venv_dolibarr/bin/activate  # Linux/macOS
.\venv_dolibarr\Scripts\Activate.ps1  # Windows

# With environment variables
dolibarr-mcp

# With direct parameters
dolibarr-mcp --url https://your-dolibarr.com --api-key YOUR_API_KEY

# Debug mode
dolibarr-mcp --log-level DEBUG
```

## 💡 Example Usage

### Customer Management
```
"Show me all customers in Dolibarr"
"Create a new customer named 'Acme Corp' with email info@acme.com"
"Update customer ID 5 with new phone number +1234567890"
"Find customers in France"
```

### Product Management
```
"List all products with stock levels"
"Create a new product 'Consulting Service' with price $150"
"Update product ID 10 to set new price $200"
"Show me products with low stock"
```

### Invoice Management
```
"Show all unpaid invoices"
"Create an invoice for customer 'Acme Corp'"
"Get invoice details for invoice ID 100"
"Update invoice due date to next month"
```

### Contact Management
```
"List all contacts for customer ID 5"
"Create a new contact John Doe for Acme Corp"
"Update contact email for John Doe"
"Find all contacts with role 'Manager'"
```

## 🔧 Troubleshooting

### ❌ Common Issues

#### "ModuleNotFoundError: No module named 'dolibarr_mcp'"

**Solution:** Use virtual environment and ensure package is installed:
```bash
# Check if in virtual environment
python -c "import sys; print(sys.prefix)"

# Reinstall package
pip install -e .

# Verify installation
python -c "import dolibarr_mcp; print('Module found')"
```

#### API Connection Issues

**Check API Configuration:**
```bash
# Test connection with curl
curl -X GET "https://your-dolibarr.com/api/index.php/status" \
  -H "DOLAPIKEY: YOUR_API_KEY"
```

#### Permission Errors

Ensure your API key has necessary permissions in Dolibarr:
1. Go to Dolibarr Admin → API/Web Services
2. Check API key permissions
3. Enable required modules (API REST module)

### 🔍 Debug Mode

Enable debug logging in Claude Desktop configuration:
```json
{
  "mcpServers": {
    "dolibarr": {
      "command": "path/to/python",
      "args": ["-m", "dolibarr_mcp.dolibarr_mcp_server"],
      "cwd": "path/to/dolibarr-mcp",
      "env": {
        "DOLIBARR_URL": "https://your-dolibarr.example.com",
        "DOLIBARR_API_KEY": "YOUR_API_KEY",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## 📊 Project Structure

```
dolibarr-mcp/
├── src/dolibarr_mcp/              # Main Package
│   ├── dolibarr_mcp_server.py     # MCP Server
│   ├── dolibarr_client.py         # Dolibarr API Client
│   ├── config.py                  # Configuration Management
│   └── cli.py                     # Command Line Interface
├── tests/                         # Test Suite
│   ├── test_config.py             # Unit Tests
│   └── test_dolibarr_client.py    # Integration Tests
├── docker/                        # Docker Configuration
│   ├── Dockerfile                 # Container Definition
│   └── docker-compose.yml         # Compose Configuration
├── venv_dolibarr/                 # Virtual Environment (after setup)
├── README.md                      # Documentation
├── CHANGELOG.md                   # Version History
├── pyproject.toml                 # Package Configuration
└── requirements.txt               # Dependencies
```

## 📖 API Documentation

### Dolibarr API

Complete Dolibarr API documentation:
- **[Dolibarr REST API Wiki](https://wiki.dolibarr.org/index.php?title=Module_Web_Services_API_REST_(developer))**
- **[Dolibarr Integration Guide](https://wiki.dolibarr.org/index.php?title=Interfaces_Dolibarr_toward_foreign_systems)**

### Authentication

```bash
curl -X GET "https://your-dolibarr.com/api/index.php/status" \
  -H "DOLAPIKEY: YOUR_API_KEY"
```

### Important Endpoints

- **Third Parties**: `/api/index.php/thirdparties`
- **Products**: `/api/index.php/products`
- **Invoices**: `/api/index.php/invoices`
- **Orders**: `/api/index.php/orders`
- **Contacts**: `/api/index.php/contacts`
- **Users**: `/api/index.php/users`
- **Status**: `/api/index.php/status`

## 🧪 Development

### 🏗️ Development Environment

```bash
# Activate virtual environment
source venv_dolibarr/bin/activate  # Linux/macOS
.\venv_dolibarr\Scripts\Activate.ps1  # Windows

# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/dolibarr_mcp --cov-report=html

# Run integration tests
python tests/test_dolibarr_client.py
```

## 📖 Resources

- **[Dolibarr Official Documentation](https://www.dolibarr.org/documentation-home)**
- **[Model Context Protocol Specification](https://modelcontextprotocol.io/)**
- **[Claude Desktop MCP Integration](https://docs.anthropic.com/)**
- **[GitHub Repository](https://github.com/latinogino/dolibarr-mcp)**

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**🎯 Manage your complete Dolibarr ERP/CRM through natural language with Claude Desktop!**
