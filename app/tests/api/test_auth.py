import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Password1",
        "password_confirmation": "Password1",
        "first_name": "Test",
        "last_name": "User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "email": "test@example.com",
        "password": "Password1",
        "password_confirmation": "Password1",
        "first_name": "Test",
        "last_name": "User",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "WrongPass1",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_password_validation(client: AsyncClient):
    """Weak password should be rejected."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "weakpass",      # No uppercase or digit
        "password_confirmation": "weakpass",
        "first_name": "Test",
        "last_name": "User",
    })
    assert response.status_code == 422
