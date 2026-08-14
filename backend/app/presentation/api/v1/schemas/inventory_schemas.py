from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.domain.enums import MovementReferenceType, MovementType


class StockAdjustmentRequest(BaseModel):
    product_id: int
    quantity_delta: Decimal
    notes: str | None = None


class InventoryMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: MovementType
    quantity: Decimal
    unit_cost: Decimal
    balance_after: Decimal
    reference_type: MovementReferenceType
    reference_id: int
    notes: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
