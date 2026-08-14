from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import PaymentMethod


class PurchaseItemCreateRequest(BaseModel):
    product_id: int
    quantity: Decimal = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)


class PurchaseCreateRequest(BaseModel):
    partner_id: int
    payment_method: PaymentMethod
    items: list[PurchaseItemCreateRequest] = Field(min_length=1)


class PurchaseItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class PurchaseResponse(BaseModel):
    id: int
    partner_id: int
    payment_method: PaymentMethod
    subtotal: Decimal
    total: Decimal
    date: datetime | None = None
    items: list[PurchaseItemResponse]

    model_config = {"from_attributes": True}
