from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    id: int | None
    sku: str
    name: str
    category_id: int
    unit_of_measure: str
    cost_price: Decimal
    sale_price: Decimal
    current_stock: Decimal
    min_stock: Decimal
    description: str | None = None
    is_active: bool = True

    def is_below_min_stock(self) -> bool:
        return self.current_stock < self.min_stock
