from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import PaymentMethod


class SaleItemCreateRequest(BaseModel):
    product_id: int
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class SaleCreateRequest(BaseModel):
    partner_id: int | None = None
    payment_method: PaymentMethod
    items: list[SaleItemCreateRequest] = Field(min_length=1)


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    unit_cost: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class SaleResponse(BaseModel):
    id: int
    partner_id: int | None = None
    payment_method: PaymentMethod
    subtotal: Decimal
    total: Decimal
    date: datetime | None = None
    items: list[SaleItemResponse]

    model_config = {"from_attributes": True}
