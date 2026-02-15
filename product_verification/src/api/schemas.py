from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class CreateProductRequest(BaseModel):
    name: str
    price: float = Field(gt=0)
    currency: str
    category: str
    stock_quantity: int = Field(ge=0)
    assets: List[str]


class ProductResponse(BaseModel):
    product_id: str
    name: str
    price: float
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime


class VerifyProductResponse(BaseModel):
    product_id: str
    status: str
    message: str
