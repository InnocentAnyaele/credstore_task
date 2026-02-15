from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4


class ProductStatus(str, Enum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    REJECTED = "rejected"


@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProductCreatedPendingVerification(DomainEvent):
    product_id: str = ""
    name: str = ""
    price: float = 0.0
    currency: str = ""


@dataclass
class ProductVerificationCompleted(DomainEvent):
    product_id: str = ""
    status: ProductStatus = ProductStatus.PENDING_VERIFICATION
    reasons: List[str] = field(default_factory=list)


class Product:
    def __init__(
        self,
        product_id: str,
        name: str,
        price: float,
        currency: str,
        category: str,
        stock_quantity: int,
        assets: List[str],
        status: ProductStatus = ProductStatus.PENDING_VERIFICATION,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.currency = currency
        self.category = category
        self.stock_quantity = stock_quantity
        self.assets = assets
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self._domain_events: List[DomainEvent] = []

    def transition_to_active(self) -> None:
        if self.status != ProductStatus.PENDING_VERIFICATION:
            raise ValueError(
                f"Cannot transition from {self.status} to active"
            )
        self.status = ProductStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def transition_to_rejected(self) -> None:
        if self.status != ProductStatus.PENDING_VERIFICATION:
            raise ValueError(
                f"Cannot transition from {self.status} to rejected"
            )
        self.status = ProductStatus.REJECTED
        self.updated_at = datetime.utcnow()

    def add_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def get_domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
