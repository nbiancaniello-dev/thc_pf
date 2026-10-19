from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user

@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser"
        }
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text

@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "different_user",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"

@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data