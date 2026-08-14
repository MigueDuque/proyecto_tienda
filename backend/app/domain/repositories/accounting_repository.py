from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.entities.account import Account
from app.domain.entities.journal_entry import JournalEntry


class AccountRepository(ABC):
    @abstractmethod
    def add(self, account: Account) -> Account: ...

    @abstractmethod
    def get_by_id(self, account_id: int) -> Account | None: ...

    @abstractmethod
    def get_by_code(self, code: str) -> Account | None: ...

    @abstractmethod
    def list(self) -> list[Account]: ...

    @abstractmethod
    def get_balance(self, account_id: int) -> Decimal: ...


class JournalEntryRepository(ABC):
    @abstractmethod
    def add(self, entry: JournalEntry) -> JournalEntry: ...

    @abstractmethod
    def get_by_id(self, entry_id: int) -> JournalEntry | None: ...

    @abstractmethod
    def list_all(self) -> list[JournalEntry]: ...
