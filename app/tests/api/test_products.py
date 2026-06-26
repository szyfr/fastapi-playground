import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_products_empty(client: AsyncClient):
    response = await client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_create_product_validation_error(admin_client: AsyncClient):
    """Missing required fields should return 422."""
    response = await admin_client.post("/api/v1/products/", json={"name": "ab"})
    assert response.status_code == 422
    assert "errors" in response.json()


@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient):
    response = await client.get("/api/v1/products/999")
    assert response.status_code == 404
    assert response.json()["success"] is False
