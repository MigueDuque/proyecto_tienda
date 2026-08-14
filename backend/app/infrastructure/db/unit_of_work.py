from sqlalchemy.orm import Session, sessionmaker

from app.application.unit_of_work import AbstractUnitOfWork
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.sqlalchemy_category_repository import (
    SqlAlchemyCategoryRepository,
)
from app.infrastructure.repositories.sqlalchemy_inventory_repository import (
    SqlAlchemyInventoryRepository,
)
from app.infrastructure.repositories.sqlalchemy_partner_repository import (
    SqlAlchemyPartnerRepository,
)
from app.infrastructure.repositories.sqlalchemy_product_repository import (
    SqlAlchemyProductRepository,
)
from app.infrastructure.repositories.sqlalchemy_purchase_repository import (
    SqlAlchemyPurchaseRepository,
)
from app.infrastructure.repositories.sqlalchemy_sale_repository import SqlAlchemySaleRepository
from app.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal):
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session)
        self.categories = SqlAlchemyCategoryRepository(self._session)
        self.products = SqlAlchemyProductRepository(self._session)
        self.partners = SqlAlchemyPartnerRepository(self._session)
        self.inventory_movements = SqlAlchemyInventoryRepository(self._session)
        self.purchases = SqlAlchemyPurchaseRepository(self._session)
        self.sales = SqlAlchemySaleRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)
        if self._session is not None:
            self._session.close()
            self._session = None

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
