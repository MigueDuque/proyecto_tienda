from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.enums import MovementReferenceType, MovementType


@dataclass
class InventoryMovement:
    id: int | None
    product_id: int
    movement_type: MovementType
    quantity: Decimal
    unit_cost: Decimal
    balance_after: Decimal
    reference_type: MovementReferenceType
    reference_id: int
    notes: str | None = None
    created_at: datetime | None = None
