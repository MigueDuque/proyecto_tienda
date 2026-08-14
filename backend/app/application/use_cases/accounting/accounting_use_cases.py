from dataclasses import dataclass, field
from decimal import Decimal

from app.application.services.accounting_service import AccountingService
from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities.account import Account
from app.domain.entities.journal_entry import JournalEntry, JournalEntryLine
from app.domain.enums import JournalEntryReferenceType
from app.domain.exceptions import InvalidOperationError, NotFoundError


@dataclass
class ManualEntryLineInput:
    account_id: int
    debit: Decimal
    credit: Decimal
    description: str | None = None


@dataclass
class RegisterManualEntryInput:
    description: str
    lines: list[ManualEntryLineInput] = field(default_factory=list)


class RegisterManualEntryUseCase:
    def __init__(self, uow: AbstractUnitOfWork, accounting: AccountingService | None = None):
        self._uow = uow
        self._accounting = accounting or AccountingService()

    def execute(self, data: RegisterManualEntryInput) -> JournalEntry:
        if len(data.lines) < 2:
            raise InvalidOperationError("El asiento manual debe tener al menos dos lineas")

        with self._uow as uow:
            for line in data.lines:
                if uow.accounts.get_by_id(line.account_id) is None:
                    raise NotFoundError("CuentaContable", line.account_id)

            entry = JournalEntry(
                id=None,
                description=data.description,
                reference_type=JournalEntryReferenceType.MANUAL,
                lines=[
                    JournalEntryLine(
                        id=None,
                        account_id=line.account_id,
                        debit=line.debit,
                        credit=line.credit,
                        description=line.description,
                    )
                    for line in data.lines
                ],
            )
            self._accounting.assert_balanced(entry)

            created = uow.journal_entries.add(entry)
            uow.commit()
            return created


class ListJournalEntriesUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self) -> list[JournalEntry]:
        with self._uow as uow:
            return uow.journal_entries.list_all()


class ListAccountsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self) -> list[Account]:
        with self._uow as uow:
            return uow.accounts.list()


class GetAccountBalanceUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, account_id: int) -> Decimal:
        with self._uow as uow:
            if uow.accounts.get_by_id(account_id) is None:
                raise NotFoundError("CuentaContable", account_id)
            return uow.accounts.get_balance(account_id)
