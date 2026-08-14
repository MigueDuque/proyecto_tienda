from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.enums import JournalEntryReferenceType


@dataclass
class JournalEntryLine:
    id: int | None
    account_id: int
    debit: Decimal
    credit: Decimal
    description: str | None = None
    journal_entry_id: int | None = None


@dataclass
class JournalEntry:
    id: int | None
    description: str
    reference_type: JournalEntryReferenceType
    reference_id: int | None = None
    lines: list[JournalEntryLine] = field(default_factory=list)
    date: datetime | None = None

    def total_debit(self) -> Decimal:
        return sum((line.debit for line in self.lines), Decimal("0"))

    def total_credit(self) -> Decimal:
        return sum((line.credit for line in self.lines), Decimal("0"))
