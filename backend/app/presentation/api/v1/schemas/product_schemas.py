from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    category_id: int
    unit_of_measure: str = Field(min_length=1, max_length=32)
    cost_price: Decimal = Field(ge=0)
    sale_price: Decimal = Field(ge=0)
    min_stock: Decimal = Field(ge=0)
    description: str | None = None
    is_active: bool = True


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    category_id: int
    unit_of_measure: str
    cost_price: Decimal
    sale_price: Decimal
    current_stock: Decimal
    min_stock: Decimal
    description: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}
