from dataclasses import dataclass
from decimal import Decimal

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities.product import Product
from app.domain.exceptions import DuplicateError, NotFoundError


@dataclass
class ProductInput:
    sku: str
    name: str
    category_id: int
    unit_of_measure: str
    cost_price: Decimal
    sale_price: Decimal
    min_stock: Decimal
    description: str | None = None
    is_active: bool = True


class CreateProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, data: ProductInput) -> Product:
        with self._uow as uow:
            if uow.categories.get_by_id(data.category_id) is None:
                raise NotFoundError("Categoria", data.category_id)
            if uow.products.get_by_sku(data.sku) is not None:
                raise DuplicateError("Producto", "sku", data.sku)
            product = Product(
                id=None,
                sku=data.sku,
                name=data.name,
                category_id=data.category_id,
                unit_of_measure=data.unit_of_measure,
                cost_price=data.cost_price,
                sale_price=data.sale_price,
                current_stock=Decimal("0"),
                min_stock=data.min_stock,
                description=data.description,
                is_active=data.is_active,
            )
            created = uow.products.add(product)
            uow.commit()
            return created


class UpdateProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, product_id: int, data: ProductInput) -> Product:
        with self._uow as uow:
            existing = uow.products.get_by_id(product_id)
            if existing is None:
                raise NotFoundError("Producto", product_id)
            if uow.categories.get_by_id(data.category_id) is None:
                raise NotFoundError("Categoria", data.category_id)
            duplicate = uow.products.get_by_sku(data.sku)
            if duplicate is not None and duplicate.id != product_id:
                raise DuplicateError("Producto", "sku", data.sku)
            existing.sku = data.sku
            existing.name = data.name
            existing.category_id = data.category_id
            existing.unit_of_measure = data.unit_of_measure
            existing.cost_price = data.cost_price
            existing.sale_price = data.sale_price
            existing.min_stock = data.min_stock
            existing.description = data.description
            existing.is_active = data.is_active
            updated = uow.products.update(existing)
            uow.commit()
            return updated


class DeleteProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, product_id: int) -> None:
        with self._uow as uow:
            if uow.products.get_by_id(product_id) is None:
                raise NotFoundError("Producto", product_id)
            uow.products.delete(product_id)
            uow.commit()


class GetProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, product_id: int) -> Product:
        with self._uow as uow:
            product = uow.products.get_by_id(product_id)
            if product is None:
                raise NotFoundError("Producto", product_id)
            return product


class ListProductsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, category_id: int | None = None, only_active: bool = False) -> list[Product]:
        with self._uow as uow:
            return uow.products.list(category_id=category_id, only_active=only_active)


class ListLowStockProductsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self) -> list[Product]:
        with self._uow as uow:
            return uow.products.list_low_stock()
