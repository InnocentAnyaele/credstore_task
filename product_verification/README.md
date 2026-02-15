# Product Verification System

A FastAPI application implementing clean layered architecture with product verification workflow.

## Setup

1. Start databases:
```bash
docker-compose up -d
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run application:
```bash
python main.py
```

## API Endpoints

- POST `/api/v1/products` - Create product
- POST `/api/v1/products/{product_id}/verify` - Verify product
- GET `/api/v1/products/{product_id}` - Get product

## Testing

Run all tests:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_verification_policy.py -v
pytest tests/test_integration.py -v
```

## Example Usage

Create product:
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15",
    "price": 999.99,
    "currency": "USD",
    "category": "Electronics",
    "stock_quantity": 50,
    "assets": ["image1.jpg"]
  }'
```

Verify product:
```bash
curl -X POST http://localhost:8000/api/v1/products/{product_id}/verify
```

Get product:
```bash
curl http://localhost:8000/api/v1/products/{product_id}
```
