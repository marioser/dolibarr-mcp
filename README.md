# Dolibarr MCP Server

Professional Model Context Protocol (MCP) server for comprehensive Dolibarr ERP integration with full CRUD operations and business intelligence capabilities.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-1.0.0-orange.svg)](https://modelcontextprotocol.io)

## 🚀 Quick Start

### Automated Setup (Recommended)

**For Windows:**
```bash
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp
setup.bat
```

**For Linux/Mac:**
```bash
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment (`venv_dolibarr`)
- Install all dependencies
- Create a `.env` configuration file
- Test the installation

### Manual Setup

```bash
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp

# Create virtual environment
python -m venv venv_dolibarr

# Activate virtual environment
# Windows:
venv_dolibarr\Scripts\activate
# Linux/Mac:
source venv_dolibarr/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## ⚙️ Configuration

Edit the `.env` file with your Dolibarr instance details:

```env
# Dolibarr API Configuration
DOLIBARR_URL=https://your-dolibarr-instance.com/api/index.php
DOLIBARR_API_KEY=your_dolibarr_api_key_here

# Logging Configuration
LOG_LEVEL=INFO
```

### Dolibarr API Setup

1. **Enable the API module** in Dolibarr:
   - Go to Home → Setup → Modules
   - Enable "Web Services API REST (developer)"

2. **Create an API key**:
   - Go to Home → Setup → API/Web services
   - Create a new API key for your user
   - Ensure the user has appropriate permissions

3. **Test the API**:
   ```bash
   curl -X GET "https://your-dolibarr-instance.com/api/index.php/status" \
     -H "DOLAPIKEY: your_api_key_here"
   ```

## 🏃‍♂️ Running the Server

### Development Mode

**Windows:**
```bash
venv_dolibarr\Scripts\python.exe -m dolibarr_mcp.dolibarr_mcp_server
```

**Linux/Mac:**
```bash
venv_dolibarr/bin/python -m dolibarr_mcp.dolibarr_mcp_server
```

### With Claude Desktop

Add to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dolibarr-mcp": {
      "command": "C:\\path\\to\\your\\dolibarr-mcp\\venv_dolibarr\\Scripts\\python.exe",
      "args": ["-m", "dolibarr_mcp.dolibarr_mcp_server"],
      "cwd": "C:\\path\\to\\your\\dolibarr-mcp",
      "env": {
        "DOLIBARR_URL": "https://your-dolibarr-instance.com/api/index.php",
        "DOLIBARR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Docker (Alternative)

```bash
docker-compose up
```

## 🚀 Features

### Complete ERP Management
- **Customer/Third Party Management**: Full CRUD operations for customers and suppliers
- **Product Catalog**: Comprehensive product management with inventory tracking
- **Invoice Management**: Create, update, and track invoices with line items
- **Order Processing**: Complete order lifecycle management
- **Contact Management**: Maintain detailed contact records
- **User Administration**: User account and permissions management

### Professional Grade
- **Asynchronous Operations**: High-performance async/await architecture
- **Error Handling**: Comprehensive error handling with detailed logging
- **Type Safety**: Full type hints with Pydantic validation
- **CLI Interface**: Professional command-line tools for testing and management
- **Raw API Access**: Direct access to any Dolibarr API endpoint

### MCP Integration
- **Tool-based Architecture**: Each operation exposed as an MCP tool
- **Schema Validation**: Proper input/output schema validation
- **Response Formatting**: Structured JSON responses
- **Error Propagation**: Meaningful error messages and status codes

## 📋 Prerequisites

- Python 3.8 or higher
- Dolibarr instance with API enabled
- Dolibarr API key with appropriate permissions

## 🛠️ Available Tools

The server exposes comprehensive tools for Dolibarr management:

#### System Tools
- `test_connection` - Test API connectivity
- `get_status` - Get system status and version

#### Customer Management
- `get_customers` - List customers/third parties
- `get_customer_by_id` - Get specific customer details
- `create_customer` - Create new customer
- `update_customer` - Update existing customer
- `delete_customer` - Delete customer

#### Product Management  
- `get_products` - List products
- `get_product_by_id` - Get specific product details
- `create_product` - Create new product
- `update_product` - Update existing product
- `delete_product` - Delete product

#### Invoice Management
- `get_invoices` - List invoices
- `get_invoice_by_id` - Get specific invoice details
- `create_invoice` - Create new invoice with line items
- `update_invoice` - Update existing invoice
- `delete_invoice` - Delete invoice

#### Order Management
- `get_orders` - List orders
- `get_order_by_id` - Get specific order details
- `create_order` - Create new order
- `update_order` - Update existing order
- `delete_order` - Delete order

#### Contact Management
- `get_contacts` - List contacts
- `get_contact_by_id` - Get specific contact details
- `create_contact` - Create new contact
- `update_contact` - Update existing contact
- `delete_contact` - Delete contact

#### User Management
- `get_users` - List users
- `get_user_by_id` - Get specific user details
- `create_user` - Create new user
- `update_user` - Update existing user
- `delete_user` - Delete user

#### Raw API Access
- `dolibarr_raw_api` - Make direct API calls to any endpoint

## 💻 Programmatic Usage

```python
import asyncio
from dolibarr_mcp import Config, DolibarrClient

async def main():
    config = Config.from_env()
    
    async with DolibarrClient(config) as client:
        # Get customers
        customers = await client.get_customers(limit=10)
        print(f"Found {len(customers)} customers")
        
        # Create a new customer
        new_customer = await client.create_customer(
            name="Test Company",
            email="test@company.com",
            phone="+1-555-0123"
        )
        print(f"Created customer: {new_customer}")
        
        # Get products
        products = await client.get_products(limit=5)
        print(f"Found {len(products)} products")

asyncio.run(main())
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=src/dolibarr_mcp
```

Test API connection:
```bash
# Windows:
venv_dolibarr\Scripts\python.exe -c "from dolibarr_mcp import Config, DolibarrClient; import asyncio; asyncio.run(DolibarrClient(Config()).get_status())"

# Linux/Mac:
venv_dolibarr/bin/python -c "from dolibarr_mcp import Config, DolibarrClient; import asyncio; asyncio.run(DolibarrClient(Config()).get_status())"
```

## 🏗️ Project Structure

```
dolibarr-mcp/
├── src/dolibarr_mcp/
│   ├── __init__.py              # Package exports
│   ├── config.py                # Configuration management
│   ├── cli.py                   # Command line interface
│   ├── dolibarr_client.py       # API client implementation
│   └── dolibarr_mcp_server.py   # MCP server implementation
├── tests/                       # Test suite
├── api/                         # API documentation
├── setup.py                     # Development setup script
├── setup.bat                    # Windows setup script
├── setup.sh                     # Linux/Mac setup script
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

## 🐳 Docker Support

Build and run with Docker:

```bash
# Build image
docker build -t dolibarr-mcp .

# Run with docker-compose
docker-compose up

# Run container directly
docker run -p 8080:8080 --env-file .env dolibarr-mcp
```

## 🔧 Troubleshooting

### Common Issues

**1. Virtual Environment Not Found**
```bash
# Make sure you created the virtual environment:
python -m venv venv_dolibarr

# And use the correct path in Claude Desktop config
```

**2. API Connection Failed**
```bash
# Test your API key and URL:
curl -X GET "https://your-dolibarr-instance.com/api/index.php/status" \
  -H "DOLAPIKEY: your_api_key_here"
```

**3. Module Import Errors**
```bash
# Install in development mode:
pip install -e .
```

**4. Permission Errors**
- Ensure your Dolibarr user has API access
- Check that the API module is enabled
- Verify user permissions for the operations you want to perform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/dolibarr-mcp.git
cd dolibarr-mcp

# Run setup script
python setup.py

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Dolibarr](https://www.dolibarr.org/) - The amazing open-source ERP/CRM
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification
- [Anthropic](https://www.anthropic.com/) - For the MCP standard

## 📞 Support

- 📖 [Documentation](https://github.com/latinogino/dolibarr-mcp#readme)
- 🐛 [Issue Tracker](https://github.com/latinogino/dolibarr-mcp/issues)
- 💬 [Discussions](https://github.com/latinogino/dolibarr-mcp/discussions)

## 🗺️ Roadmap

### Phase 1 (Completed) ✅
- [x] Core MCP server implementation
- [x] Full CRUD operations for main entities
- [x] Professional error handling
- [x] Automated setup scripts
- [x] Docker support
- [x] Comprehensive documentation

### Phase 2 (Next)
- [ ] Advanced filtering and search
- [ ] Webhook support
- [ ] Performance optimization
- [ ] Extended API coverage
- [ ] Unit tests

### Phase 3 (Future)
- [ ] Web UI for management
- [ ] Multi-instance support
- [ ] Caching layer
- [ ] Metrics and monitoring
- [ ] Plugin system

---

**Built with ❤️ for the Dolibarr community**
