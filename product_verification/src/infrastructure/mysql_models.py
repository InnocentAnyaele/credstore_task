from sqlalchemy import Column, String, Float, Integer, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class ProductStatusEnum(str, enum.Enum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    REJECTED = "rejected"


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    category = Column(String(255), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    assets = Column(JSON, nullable=False)
    status = Column(
        SQLEnum(ProductStatusEnum),
        nullable=False,
        default=ProductStatusEnum.PENDING_VERIFICATION,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
