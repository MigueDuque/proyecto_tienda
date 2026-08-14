from pydantic import BaseModel, Field

from app.domain.enums import PartnerType


class PartnerCreateRequest(BaseModel):
    type: PartnerType
    name: str = Field(min_length=1, max_length=255)
    document_id: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    is_active: bool = True


class PartnerResponse(BaseModel):
    id: int
    type: PartnerType
    name: str
    document_id: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}
