from copy import deepcopy

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities.category import Category
from app.domain.entities.inventory_movement import InventoryMovement
from app.domain.entities.partner import Partner
from app.domain.entities.product import Product
from app.domain.entities.purchase import Purchase
from app.domain.entities.sale import Sale
from app.domain.entities.user import User
from app.domain.enums import PartnerType


class InMemoryUserRepository:
    def __init__(self):
        self._items: dict[int, User] = {}
        self._next_id = 1

    def add(self, user: User) -> User:
        user.id = self._next_id
        self._next_id += 1
        self._items[user.id] = deepcopy(user)
        return deepcopy(user)

    def get_by_id(self, user_id: int) -> User | None:
        item = self._items.get(user_id)
        return deepcopy(item) if item else None

    def get_by_email(self, email: str) -> User | None:
        for item in self._items.values():
            if item.email == email:
                return deepcopy(item)
        return None


class InMemoryCategoryRepository:
    def __init__(self):
        self._items: dict[int, Category] = {}
        self._next_id = 1

    def add(self, category: Category) -> Category:
        category.id = self._next_id
        self._next_id += 1
        self._items[category.id] = deepcopy(category)
        return deepcopy(category)

    def update(self, category: Category) -> Category:
        self._items[category.id] = deepcopy(category)
        return deepcopy(category)

    def delete(self, category_id: int) -> None:
        self._items.pop(category_id, None)

    def get_by_id(self, category_id: int) -> Category | None:
        item = self._items.get(category_id)
        return deepcopy(item) if item else None

    def get_by_name(self, name: str) -> Category | None:
        for item in self._items.values():
            if item.name == name:
                return deepcopy(item)
        return None

    def list(self) -> list[Category]:
        return [deepcopy(i) for i in self._items.values()]


class InMemoryProductRepository:
    def __init__(self):
        self._items: dict[int, Product] = {}
        self._next_id = 1

    def add(self, product: Product) -> Product:
        product.id = self._next_id
        self._next_id += 1
        self._items[product.id] = deepcopy(product)
        return deepcopy(product)

    def update(self, product: Product) -> Product:
        self._items[product.id] = deepcopy(product)
        return deepcopy(product)

    def delete(self, product_id: int) -> None:
        self._items.pop(product_id, None)

    def get_by_id(self, product_id: int) -> Product | None:
        item = self._items.get(product_id)
        return deepcopy(item) if item else None

    def get_by_sku(self, sku: str) -> Product | None:
        for item in self._items.values():
            if item.sku == sku:
                return deepcopy(item)
        return None

    def list_low_stock(self) -> list[Product]:
        return [deepcopy(i) for i in self._items.values() if i.current_stock < i.min_stock]

    def list(self, category_id: int | None = None, only_active: bool = False) -> list[Product]:
        items = self._items.values()
        if category_id is not None:
            items = [i for i in items if i.category_id == category_id]
        if only_active:
            items = [i for i in items if i.is_active]
        return [deepcopy(i) for i in items]


class InMemoryPartnerRepository:
    def __init__(self):
        self._items: dict[int, Partner] = {}
        self._next_id = 1

    def add(self, partner: Partner) -> Partner:
        partner.id = self._next_id
        self._next_id += 1
        self._items[partner.id] = deepcopy(partner)
        return deepcopy(partner)

    def update(self, partner: Partner) -> Partner:
        self._items[partner.id] = deepcopy(partner)
        return deepcopy(partner)

    def delete(self, partner_id: int) -> None:
        self._items.pop(partner_id, None)

    def get_by_id(self, partner_id: int) -> Partner | None:
        item = self._items.get(partner_id)
        return deepcopy(item) if item else None

    def list(self, type: PartnerType | None = None) -> list[Partner]:
        items = self._items.values()
        if type is not None:
            items = [i for i in items if i.type == type]
        return [deepcopy(i) for i in items]


class InMemoryInventoryRepository:
    def __init__(self):
        self._items: list[InventoryMovement] = []
        self._next_id = 1

    def add_movement(self, movement: InventoryMovement) -> InventoryMovement:
        movement.id = self._next_id
        self._next_id += 1
        self._items.append(deepcopy(movement))
        return deepcopy(movement)

    def list_by_product(self, product_id: int) -> list[InventoryMovement]:
        return [deepcopy(i) for i in self._items if i.product_id == product_id]

    def list_all(self, product_id: int | None = None) -> list[InventoryMovement]:
        items = self._items
        if product_id is not None:
            items = [i for i in items if i.product_id == product_id]
        return [deepcopy(i) for i in items]


class InMemoryPurchaseRepository:
    def __init__(self):
        self._items: dict[int, Purchase] = {}
        self._next_id = 1
        self._next_item_id = 1

    def add(self, purchase: Purchase) -> Purchase:
        purchase.id = self._next_id
        self._next_id += 1
        for item in purchase.items:
            item.id = self._next_item_id
            item.purchase_id = purchase.id
            self._next_item_id += 1
        self._items[purchase.id] = deepcopy(purchase)
        return deepcopy(purchase)

    def get_by_id(self, purchase_id: int) -> Purchase | None:
        item = self._items.get(purchase_id)
        return deepcopy(item) if item else None

    def list_all(self) -> list[Purchase]:
        return [deepcopy(i) for i in self._items.values()]


class InMemorySaleRepository:
    def __init__(self):
        self._items: dict[int, Sale] = {}
        self._next_id = 1
        self._next_item_id = 1

    def add(self, sale: Sale) -> Sale:
        sale.id = self._next_id
        self._next_id += 1
        for item in sale.items:
            item.id = self._next_item_id
            item.sale_id = sale.id
            self._next_item_id += 1
        self._items[sale.id] = deepcopy(sale)
        return deepcopy(sale)

    def get_by_id(self, sale_id: int) -> Sale | None:
        item = self._items.get(sale_id)
        return deepcopy(item) if item else None

    def list_all(self) -> list[Sale]:
        return [deepcopy(i) for i in self._items.values()]


class InMemoryUnitOfWork(AbstractUnitOfWork):
    """Fake UoW for unit-testing use cases without a real database."""

    def __init__(self):
        self.users = InMemoryUserRepository()
        self.categories = InMemoryCategoryRepository()
        self.products = InMemoryProductRepository()
        self.partners = InMemoryPartnerRepository()
        self.inventory_movements = InMemoryInventoryRepository()
        self.purchases = InMemoryPurchaseRepository()
        self.sales = InMemorySaleRepository()
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass
