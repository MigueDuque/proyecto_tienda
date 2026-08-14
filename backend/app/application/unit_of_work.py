from abc import ABC, abstractmethod
from types import TracebackType

from app.domain.repositories.category_repository import CategoryRepository
from app.domain.repositories.inventory_repository import InventoryRepository
from app.domain.repositories.partner_repository import PartnerRepository
from app.domain.repositories.product_repository import ProductRepository
from app.domain.repositories.purchase_repository import PurchaseRepository
from app.domain.repositories.sale_repository import SaleRepository
from app.domain.repositories.user_repository import UserRepository


class AbstractUnitOfWork(ABC):
    """Groups repositories behind a single atomic transaction boundary.

    Use cases depend only on this interface, never on a raw DB session,
    so they can be unit-tested with an in-memory implementation.
    """

    users: UserRepository
    categories: CategoryRepository
    products: ProductRepository
    partners: PartnerRepository
    inventory_movements: InventoryRepository
    purchases: PurchaseRepository
    sales: SaleRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.rollback()  # commit() must be called explicitly by the use case

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...
