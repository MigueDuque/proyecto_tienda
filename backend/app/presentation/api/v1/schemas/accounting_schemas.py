from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import AccountType, JournalEntryReferenceType


class AccountResponse(BaseModel):
    id: int
    code: str
    name: str
    type: AccountType
    parent_id: int | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class AccountBalanceResponse(BaseModel):
    account_id: int
    balance: Decimal


class ManualEntryLineRequest(BaseModel):
    account_id: int
    debit: Decimal = Field(ge=0, default=Decimal("0"))
    credit: Decimal = Field(ge=0, default=Decimal("0"))
    description: str | None = None


class ManualEntryCreateRequest(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    lines: list[ManualEntryLineRequest] = Field(min_length=2)


class JournalEntryLineResponse(BaseModel):
    id: int
    account_id: int
    debit: Decimal
    credit: Decimal
    description: str | None = None

    model_config = {"from_attributes": True}


class JournalEntryResponse(BaseModel):
    id: int
    description: str
    reference_type: JournalEntryReferenceType
    reference_id: int | None = None
    date: datetime | None = None
    lines: list[JournalEntryLineResponse]

    model_config = {"from_attributes": True}
