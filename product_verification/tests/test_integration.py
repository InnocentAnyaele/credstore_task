import pytest
from httpx import AsyncClient
from src.api.app import app


@pytest.mark.asyncio
async def test_create_and_verify_product_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/products",
            json={
                "name": "iPhone 15",
                "price": 999.99,
                "currency": "USD",
                "category": "Electronics",
                "stock_quantity": 50,
                "assets": ["image1.jpg", "image2.jpg"],
            },
        )

        assert create_response.status_code == 201
        created_product = create_response.json()
        assert created_product["status"] == "pending_verification"
        product_id = created_product["product_id"]

        verify_response = await client.post(
            f"/api/v1/products/{product_id}/verify"
        )

        assert verify_response.status_code == 200
        verified_product = verify_response.json()
        assert verified_product["status"] == "active"
        assert verified_product["product_id"] == product_id

        get_response = await client.get(f"/api/v1/products/{product_id}")

        assert get_response.status_code == 200
        final_product = get_response.json()
        assert final_product["status"] == "active"
        assert final_product["product_id"] == product_id


@pytest.mark.asyncio
async def test_create_and_verify_product_failure():
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/products",
            json={
                "name": "",
                "price": -10,
                "currency": "",
                "category": "",
                "stock_quantity": -5,
                "assets": [],
            },
        )

        assert create_response.status_code == 201
        created_product = create_response.json()
        assert created_product["status"] == "pending_verification"
        product_id = created_product["product_id"]

        verify_response = await client.post(
            f"/api/v1/products/{product_id}/verify"
        )

        assert verify_response.status_code == 200
        verified_product = verify_response.json()
        assert verified_product["status"] == "rejected"
        assert verified_product["product_id"] == product_id

        get_response = await client.get(f"/api/v1/products/{product_id}")

        assert get_response.status_code == 200
        final_product = get_response.json()
        assert final_product["status"] == "rejected"


@pytest.mark.asyncio
async def test_verify_nonexistent_product():
    async with AsyncClient(app=app, base_url="http://test") as client:
        verify_response = await client.post(
            "/api/v1/products/nonexistent-id/verify"
        )

        assert verify_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_product():
    async with AsyncClient(app=app, base_url="http://test") as client:
        get_response = await client.get("/api/v1/products/nonexistent-id")

        assert get_response.status_code == 404
