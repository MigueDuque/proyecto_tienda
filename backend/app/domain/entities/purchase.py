from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.enums import PaymentMethod


@dataclass
class PurchaseItem:
    id: int | None
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    subtotal: Decimal
    purchase_id: int | None = None


@dataclass
class Purchase:
    id: int | None
    partner_id: int
    payment_method: PaymentMethod
    subtotal: Decimal
    total: Decimal
    items: list[PurchaseItem] = field(default_factory=list)
    date: datetime | None = None
