from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.account import Account
from app.domain.entities.journal_entry import JournalEntry, JournalEntryLine
from app.domain.enums import AccountType, JournalEntryReferenceType
from app.domain.repositories.accounting_repository import AccountRepository, JournalEntryRepository
from app.infrastructure.db.models.account_model import AccountModel
from app.infrastructure.db.models.journal_entry_model import (
    JournalEntryLineModel,
    JournalEntryModel,
)


def _account_to_domain(model: AccountModel) -> Account:
    return Account(
        id=model.id,
        code=model.code,
        name=model.name,
        type=AccountType(model.type),
        parent_id=model.parent_id,
        is_active=model.is_active,
    )


def _entry_to_domain(model: JournalEntryModel) -> JournalEntry:
    return JournalEntry(
        id=model.id,
        description=model.description,
        reference_type=JournalEntryReferenceType(model.reference_type),
        reference_id=model.reference_id,
        date=model.date,
        lines=[
            JournalEntryLine(
                id=line.id,
                journal_entry_id=line.journal_entry_id,
                account_id=line.account_id,
                debit=line.debit,
                credit=line.credit,
                description=line.description,
            )
            for line in model.lines
        ],
    )


class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, account: Account) -> Account:
        model = AccountModel(
            code=account.code,
            name=account.name,
            type=account.type.value,
            parent_id=account.parent_id,
            is_active=account.is_active,
        )
        self._session.add(model)
        self._session.flush()
        return _account_to_domain(model)

    def get_by_id(self, account_id: int) -> Account | None:
        model = self._session.get(AccountModel, account_id)
        return _account_to_domain(model) if model else None

    def get_by_code(self, code: str) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.code == code)
        model = self._session.execute(stmt).scalar_one_or_none()
        return _account_to_domain(model) if model else None

    def list(self) -> list[Account]:
        stmt = select(AccountModel).order_by(AccountModel.code)
        models = self._session.execute(stmt).scalars().all()
        return [_account_to_domain(m) for m in models]

    def get_balance(self, account_id: int) -> Decimal:
        stmt = select(
            func.coalesce(func.sum(JournalEntryLineModel.debit), 0)
            - func.coalesce(func.sum(JournalEntryLineModel.credit), 0)
        ).where(JournalEntryLineModel.account_id == account_id)
        result = self._session.execute(stmt).scalar_one()
        return Decimal(result)


class SqlAlchemyJournalEntryRepository(JournalEntryRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, entry: JournalEntry) -> JournalEntry:
        model = JournalEntryModel(
            description=entry.description,
            reference_type=entry.reference_type.value,
            reference_id=entry.reference_id,
            lines=[
                JournalEntryLineModel(
                    account_id=line.account_id,
                    debit=line.debit,
                    credit=line.credit,
                    description=line.description,
                )
                for line in entry.lines
            ],
        )
        self._session.add(model)
        self._session.flush()
        return _entry_to_domain(model)

    def get_by_id(self, entry_id: int) -> JournalEntry | None:
        stmt = (
            select(JournalEntryModel)
            .options(selectinload(JournalEntryModel.lines))
            .where(JournalEntryModel.id == entry_id)
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return _entry_to_domain(model) if model else None

    def list_all(self) -> list[JournalEntry]:
        stmt = (
            select(JournalEntryModel)
            .options(selectinload(JournalEntryModel.lines))
            .order_by(JournalEntryModel.date.desc(), JournalEntryModel.id.desc())
        )
        models = self._session.execute(stmt).scalars().all()
        return [_entry_to_domain(m) for m in models]
