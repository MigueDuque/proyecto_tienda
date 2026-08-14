from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.product import Product
from app.domain.exceptions import NotFoundError
from app.domain.repositories.product_repository import ProductRepository
from app.infrastructure.db.models.product_model import ProductModel


def _to_domain(model: ProductModel) -> Product:
    return Product(
        id=model.id,
        sku=model.sku,
        name=model.name,
        category_id=model.category_id,
        unit_of_measure=model.unit_of_measure,
        cost_price=model.cost_price,
        sale_price=model.sale_price,
        current_stock=model.current_stock,
        min_stock=model.min_stock,
        description=model.description,
        is_active=model.is_active,
    )


class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, product: Product) -> Product:
        model = ProductModel(
            sku=product.sku,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            unit_of_measure=product.unit_of_measure,
            cost_price=product.cost_price,
            sale_price=product.sale_price,
            current_stock=product.current_stock,
            min_stock=product.min_stock,
            is_active=product.is_active,
        )
        self._session.add(model)
        self._session.flush()
        return _to_domain(model)

    def update(self, product: Product) -> Product:
        model = self._session.get(ProductModel, product.id)
        if model is None:
            raise NotFoundError("Producto", product.id)
        model.sku = product.sku
        model.name = product.name
        model.description = product.description
        model.category_id = product.category_id
        model.unit_of_measure = product.unit_of_measure
        model.cost_price = product.cost_price
        model.sale_price = product.sale_price
        model.current_stock = product.current_stock
        model.min_stock = product.min_stock
        model.is_active = product.is_active
        self._session.flush()
        return _to_domain(model)

    def delete(self, product_id: int) -> None:
        model = self._session.get(ProductModel, product_id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def get_by_id(self, product_id: int) -> Product | None:
        model = self._session.get(ProductModel, product_id)
        return _to_domain(model) if model else None

    def get_by_sku(self, sku: str) -> Product | None:
        stmt = select(ProductModel).where(ProductModel.sku == sku)
        model = self._session.execute(stmt).scalar_one_or_none()
        return _to_domain(model) if model else None

    def list_low_stock(self) -> list[Product]:
        stmt = (
            select(ProductModel)
            .where(ProductModel.current_stock < ProductModel.min_stock)
            .where(ProductModel.is_active.is_(True))
            .order_by(ProductModel.name)
        )
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(m) for m in models]

    def list(self, category_id: int | None = None, only_active: bool = False) -> list[Product]:
        stmt = select(ProductModel)
        if category_id is not None:
            stmt = stmt.where(ProductModel.category_id == category_id)
        if only_active:
            stmt = stmt.where(ProductModel.is_active.is_(True))
        stmt = stmt.order_by(ProductModel.name)
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(m) for m in models]
