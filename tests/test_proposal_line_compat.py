import pytest
from unittest.mock import AsyncMock

from dolibarr_mcp.config import Config
from dolibarr_mcp.client import DolibarrClient
from dolibarr_mcp.client.exceptions import DolibarrAPIError, DolibarrValidationError


@pytest.fixture
def client() -> DolibarrClient:
    config = Config(
        dolibarr_url="https://test.dolibarr.com/api/index.php",
        api_key="test_key",
    )
    return DolibarrClient(config)


@pytest.mark.asyncio
async def test_add_proposal_line_prefers_singular_endpoint(client: DolibarrClient) -> None:
    client.request = AsyncMock(return_value={"id": 10})

    await client.add_proposal_line(
        proposal_id=3235,
        desc="Fase 1",
        qty=1,
        subprice=100,
        product_id=55,
    )

    client.request.assert_awaited_once_with(
        "POST",
        "proposals/3235/line",
        data={"desc": "Fase 1", "qty": 1, "subprice": 100, "fk_product": 55},
    )


@pytest.mark.asyncio
async def test_add_proposal_line_falls_back_to_plural_endpoint(client: DolibarrClient) -> None:
    client.request = AsyncMock(
        side_effect=[
            DolibarrAPIError("Not Implemented", status_code=501),
            {"id": 11},
        ]
    )

    result = await client.add_proposal_line(
        proposal_id=3235,
        desc="Fase 1",
        qty=1,
        subprice=100,
    )

    assert result == {"id": 11}
    assert client.request.await_count == 2
    assert client.request.await_args_list[0].args[1] == "proposals/3235/line"
    assert client.request.await_args_list[1].args[1] == "proposals/3235/lines"


@pytest.mark.asyncio
async def test_raw_api_rewrites_proposal_lines_single_payload(client: DolibarrClient) -> None:
    client.request = AsyncMock(return_value={"id": 12})

    await client.dolibarr_raw_api(
        method="POST",
        endpoint="proposals/3235/lines",
        data={"desc": "Fase 1", "qty": 1, "subprice": 100},
    )

    client.request.assert_awaited_once_with(
        "POST",
        "proposals/3235/line",
        params=None,
        data={"desc": "Fase 1", "qty": 1, "subprice": 100},
    )


@pytest.mark.asyncio
async def test_raw_api_keeps_proposal_lines_for_bulk_payload(client: DolibarrClient) -> None:
    client.request = AsyncMock(return_value={"ok": True})

    bulk_payload = [{"desc": "Fase 1", "qty": 1, "subprice": 100}]
    await client.dolibarr_raw_api(
        method="POST",
        endpoint="proposals/3235/lines",
        data=bulk_payload,  # type: ignore[arg-type]
    )

    client.request.assert_awaited_once_with(
        "POST",
        "proposals/3235/lines",
        params=None,
        data=bulk_payload,  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_update_proposal_requires_non_empty_payload(client: DolibarrClient) -> None:
    client.request = AsyncMock(return_value={"ok": True})

    with pytest.raises(DolibarrValidationError):
        await client.update_proposal(3235)

    client.request.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_proposal_fallback_after_server_error(client: DolibarrClient) -> None:
    current = {
        "socid": 401,
        "note_public": "Anterior",
        "duree_validite": 30,
        "cond_reglement_id": 1,
    }
    client.request = AsyncMock(
        side_effect=[
            DolibarrAPIError("Server error", status_code=500),
            current,
            {"id": 3235, "note_public": "Nuevo texto"},
        ]
    )

    result = await client.update_proposal(3235, note_public="Nuevo texto")

    assert result["id"] == 3235
    assert client.request.await_count == 3
    assert client.request.await_args_list[0].args[:2] == ("PUT", "proposals/3235")
    assert client.request.await_args_list[1].args[:2] == ("GET", "proposals/3235")
    assert client.request.await_args_list[2].args[:2] == ("PUT", "proposals/3235")

    fallback_payload = client.request.await_args_list[2].kwargs["data"]
    assert fallback_payload["socid"] == 401
    assert fallback_payload["note_public"] == "Nuevo texto"
    assert fallback_payload["duree_validite"] == 30


@pytest.mark.asyncio
async def test_update_proposal_line_falls_back_to_singular_endpoint(client: DolibarrClient) -> None:
    client.request = AsyncMock(
        side_effect=[
            DolibarrAPIError("Not Implemented", status_code=501),
            {"ok": True},
        ]
    )

    result = await client.update_proposal_line(3235, 99, qty=2)

    assert result == {"ok": True}
    assert client.request.await_args_list[0].args[1] == "proposals/3235/lines/99"
    assert client.request.await_args_list[1].args[1] == "proposals/3235/line/99"


@pytest.mark.asyncio
async def test_delete_proposal_line_falls_back_to_singular_endpoint(client: DolibarrClient) -> None:
    client.request = AsyncMock(
        side_effect=[
            DolibarrAPIError("Not Implemented", status_code=501),
            {"ok": True},
        ]
    )

    result = await client.delete_proposal_line(3235, 99)

    assert result == {"ok": True}
    assert client.request.await_args_list[0].args[1] == "proposals/3235/lines/99"
    assert client.request.await_args_list[1].args[1] == "proposals/3235/line/99"
