"""Backend unit tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from backend.database.database import init_db


@pytest.fixture(scope="session", autouse=True)
async def initialize_test_database():
    await init_db()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "ResearchGPT"


@pytest.mark.asyncio
async def test_signup_and_login(client):
    import uuid
    suffix = uuid.uuid4().hex[:8]
    email = f"test_{suffix}@example.com"
    username = f"user_{suffix}"
    
    signup_data = {
        "email": email,
        "username": username,
        "password": "testpassword123",
        "full_name": "Test User",
    }
    response = await client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 201
    user = response.json()
    assert user["email"] == email
    assert user["username"] == username

    login_data = {"email": email, "password": "testpassword123"}
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    response = await client.get("/api/v1/documents")
    assert response.status_code == 403 or response.status_code == 401
