"""Tests for gzip response handling in modular client."""

import gzip
from unittest.mock import AsyncMock, patch

import pytest

from dolibarr_mcp.client.base import DolibarrClient
from dolibarr_mcp.config import Config


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.request")
async def test_modular_client_decodes_gzip_response_for_proposals(mock_request):
    """POST /proposals should parse gzip-compressed JSON responses."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Encoding": "gzip"}
    mock_response.charset = "utf-8"
    mock_response.url = "https://test.dolibarr.com/api/index.php/proposals"
    mock_response.read.return_value = gzip.compress(b'{"id": 321}')
    mock_request.return_value.__aenter__.return_value = mock_response

    config = Config(
        dolibarr_url="https://test.dolibarr.com/api/index.php",
        api_key="test_key",
    )

    async with DolibarrClient(config) as client:
        result = await client.request("POST", "proposals", data={"socid": 542})

    assert result["id"] == 321
