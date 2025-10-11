# Dolibarr MCP Tests

This directory contains the test suite for the Dolibarr MCP Server.

## Test Structure

- `test_config.py` - Configuration and environment tests
- `test_dolibarr_client.py` - API client unit tests
- `test_crud_operations.py` - Complete CRUD integration tests

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/dolibarr_mcp --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_config.py::TestConfig::test_env_loading
```

## Test Requirements

All test dependencies are included in the main `requirements.txt`:
- pytest
- pytest-asyncio
- pytest-cov

## Environment Setup

Create a `.env` file in the root directory with test credentials:
```
DOLIBARR_URL=https://test.dolibarr.com
DOLIBARR_API_KEY=test_api_key
LOG_LEVEL=DEBUG
```

## Writing Tests

Follow these patterns for consistency:

```python
import pytest
from dolibarr_mcp import DolibarrClient

class TestDolibarrClient:
    @pytest.fixture
    def client(self):
        return DolibarrClient(url="https://test.com", api_key="test")
    
    def test_example(self, client):
        assert client is not None
```
