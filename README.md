# 🚀 Dolibarr MCP Server

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://github.com/anthropics/mcp)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**Professional Model Context Protocol server for complete Dolibarr ERP integration with AI assistants**

</div>

## 📌 Overview

The Dolibarr MCP Server provides a powerful bridge between AI assistants (like Claude) and your Dolibarr ERP system, enabling comprehensive business management through natural language. It implements the Model Context Protocol (MCP) to provide secure, efficient access to all Dolibarr modules.

## ✨ Features

### 🎯 Complete CRUD Operations
- **Customers/Third Parties**: Create, read, update, and delete customers
- **Products**: Full product catalog management
- **Invoices**: Complete invoice lifecycle management
- **Orders**: Order processing and management
- **Users**: User administration and access control
- **Contacts**: Contact information management
- **Raw API Access**: Direct access to any Dolibarr endpoint

### 🔧 Professional Architecture
- **Async/await** pattern for optimal performance
- **Type-safe** operations with comprehensive error handling
- **Secure** API key authentication
- **Docker-ready** for easy deployment
- **Comprehensive logging** for debugging and monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Dolibarr instance with API enabled
- Dolibarr API key

### Installation

#### Option 1: Using Python (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp

# Run the setup script
python setup.py

# Configure your credentials
cp .env.example .env
# Edit .env with your Dolibarr credentials
```

#### Option 2: Using Docker (Recommended for Production)

```bash
# Clone the repository
git clone https://github.com/latinogino/dolibarr-mcp.git
cd dolibarr-mcp

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Build and run with Docker Compose
docker-compose up -d
```

### Configuration

Create a `.env` file with your Dolibarr credentials:

```env
# Dolibarr API Configuration
DOLIBARR_URL=https://your-dolibarr-instance.com/api/index.php
DOLIBARR_API_KEY=your_api_key_here

# Logging Configuration
LOG_LEVEL=INFO
```

### Testing the Installation

Run the comprehensive test suite to verify everything is working:

```bash
# With Python
python test_dolibarr_mcp.py

# With Docker
docker-compose --profile test up dolibarr-mcp-test
```

## 🔌 Connecting to AI Assistants

### Claude Desktop Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "dolibarr": {
      "command": "python",
      "args": ["-m", "dolibarr_mcp"],
      "cwd": "/path/to/dolibarr-mcp",
      "env": {
        "DOLIBARR_URL": "https://your-dolibarr-instance.com/api/index.php",
        "DOLIBARR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## 📚 Available Tools

### Customer Management
- `get_customers` - List all customers
- `get_customer_by_id` - Get specific customer details
- `create_customer` - Create new customer
- `update_customer` - Update customer information
- `delete_customer` - Remove customer

### Product Management
- `get_products` - List all products
- `get_product_by_id` - Get product details
- `create_product` - Add new product
- `update_product` - Modify product
- `delete_product` - Remove product

### Invoice Management
- `get_invoices` - List invoices
- `get_invoice_by_id` - Get invoice details
- `create_invoice` - Create new invoice
- `update_invoice` - Update invoice
- `delete_invoice` - Delete invoice

### Order Management
- `get_orders` - List orders
- `get_order_by_id` - Get order details
- `create_order` - Create new order
- `update_order` - Update order
- `delete_order` - Delete order

### User Management
- `get_users` - List users
- `get_user_by_id` - Get user details
- `create_user` - Create new user
- `update_user` - Update user
- `delete_user` - Delete user

### Contact Management
- `get_contacts` - List contacts
- `get_contact_by_id` - Get contact details
- `create_contact` - Create new contact
- `update_contact` - Update contact
- `delete_contact` - Delete contact

### System Tools
- `test_connection` - Test API connectivity
- `get_status` - Get system status
- `dolibarr_raw_api` - Direct API access

## 💬 Example Usage with AI Assistant

Once connected, you can interact with your Dolibarr system using natural language:

```
User: "Create a new customer called 'Tech Innovations Ltd' with email tech@innovations.com"
Assistant: I'll create that customer for you in Dolibarr...
[Customer created successfully with ID: 1234]

User: "Show me all invoices from last month"
Assistant: Let me fetch the invoices for you...
[Lists invoices with details]

User: "Create a product called 'Premium Software License' priced at $299"
Assistant: I'll add that product to your catalog...
[Product created successfully]
```

## 🐳 Docker Deployment

### Build the Docker Image

```bash
docker build -t dolibarr-mcp:latest .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

### Run Tests in Docker

```bash
docker-compose --profile test up dolibarr-mcp-test
```

## 🧪 Development

### Project Structure

```
dolibarr-mcp/
├── src/
│   └── dolibarr_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── dolibarr_client.py
│       ├── dolibarr_mcp_server.py
│       └── cli.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

```bash
# Run the comprehensive test suite
python test_dolibarr_mcp.py

# Run with pytest (if installed)
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

- Python 3.8+
- Dependencies (automatically installed):
  - mcp>=1.0.0
  - aiohttp>=3.9.0
  - python-dotenv>=1.0.0
  - pydantic>=2.5.0
  - click>=8.1.0

## 🔐 Security Considerations

- Always use HTTPS for your Dolibarr instance
- Keep your API keys secure and never commit them to version control
- Use environment variables for sensitive configuration
- Regularly update dependencies for security patches
- Consider using Docker secrets for production deployments

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/latinogino/dolibarr-mcp/issues)
- **Documentation**: [Wiki](https://github.com/latinogino/dolibarr-mcp/wiki)
- **Dolibarr Documentation**: [Official Dolibarr Docs](https://wiki.dolibarr.org/)

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com/) for the MCP protocol
- [Dolibarr](https://www.dolibarr.org/) community for the excellent ERP system
- Contributors and testers

## 🚧 Roadmap

- [ ] Advanced search and filtering capabilities
- [ ] Bulk operations support
- [ ] Webhook integration
- [ ] Real-time notifications
- [ ] Multi-language support
- [ ] Advanced reporting tools
- [ ] Custom field support
- [ ] Module-specific tools (CRM, HRM, Project Management)

---

<div align="center">
Made with ❤️ for the Dolibarr and AI community
</div>
