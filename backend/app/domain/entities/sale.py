from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.enums import PaymentMethod


@dataclass
class SaleItem:
    id: int | None
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    unit_cost: Decimal
    subtotal: Decimal
    sale_id: int | None = None


@dataclass
class Sale:
    id: int | None
    payment_method: PaymentMethod
    subtotal: Decimal
    total: Decimal
    partner_id: int | None = None
    items: list[SaleItem] = field(default_factory=list)
    date: datetime | None = None
