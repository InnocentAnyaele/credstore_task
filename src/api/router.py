from fastapi import APIRouter, HTTPException, Depends, Request

from src.api.schemas import CreateProductRequest, ProductResponse, VerifyProductResponse
from src.api.container import Container
from src.use_cases import CreateProductUseCase, VerifyProductUseCase, GetProductUseCase

router = APIRouter(prefix="/api/v1/products", tags=["products"])


def get_container(request: Request) -> Container:
    # Try to get from app state (lifespan managed)
    if hasattr(request.app.state, "container"):
        return request.app.state.container

    # Fallback to creating a new container for this request (for tests/environments where lifespan didn't run)
    from src.api.app import MYSQL_URL, MONGO_URL, MONGO_DB

    return Container(MYSQL_URL, MONGO_URL, MONGO_DB)


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    request: CreateProductRequest, container: Container = Depends(get_container)
):
    use_case: CreateProductUseCase = container.get_create_product_use_case()

    product = await use_case.execute(
        name=request.name,
        price=request.price,
        currency=request.currency,
        category=request.category,
        stock_quantity=request.stock_quantity,
        assets=request.assets,
    )

    return ProductResponse(
        product_id=product.product_id,
        name=product.name,
        price=product.price,
        currency=product.currency,
        status=product.status.value,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.post("/{product_id}/verify", response_model=VerifyProductResponse)
async def verify_product(
    product_id: str, container: Container = Depends(get_container)
):
    use_case: VerifyProductUseCase = container.get_verify_product_use_case()

    try:
        product = await use_case.execute(product_id)

        message = (
            "Product verified and activated"
            if product.status.value == "active"
            else "Product verification failed"
        )

        return VerifyProductResponse(
            product_id=product.product_id, status=product.status.value, message=message
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, container: Container = Depends(get_container)):
    use_case: GetProductUseCase = container.get_get_product_use_case()

    try:
        product = await use_case.execute(product_id)

        return ProductResponse(
            product_id=product.product_id,
            name=product.name,
            price=product.price,
            currency=product.currency,
            status=product.status.value,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
