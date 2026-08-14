"""Idempotent demo data seed: admin user, categories, products, partners."""

from decimal import Decimal

from app.domain.entities.category import Category
from app.domain.entities.partner import Partner
from app.domain.entities.product import Product
from app.domain.entities.user import User
from app.domain.enums import PartnerType
from app.infrastructure.config import get_settings
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.password_hasher import BcryptPasswordHasher

CATEGORIES = ["Granos", "Abarrotes", "Aseo", "Bebidas"]

PRODUCTS = [
    # sku, name, category, unit, cost, sale, stock, min_stock
    ("GRA-001", "Arroz Diana 500g", "Granos", "unidad", "1800", "2500", "120", "20"),
    ("GRA-002", "Frijol Rojo 500g", "Granos", "unidad", "2200", "3000", "80", "15"),
    ("GRA-003", "Lenteja 500g", "Granos", "unidad", "2000", "2800", "10", "15"),
    ("GRA-004", "Maiz Trillado 1kg", "Granos", "unidad", "1500", "2200", "60", "10"),
    ("ABA-001", "Aceite Girasol 1L", "Abarrotes", "unidad", "6500", "8500", "40", "10"),
    ("ABA-002", "Azucar Blanca 1kg", "Abarrotes", "unidad", "2800", "3800", "8", "10"),
    ("ABA-003", "Sal Refisal 500g", "Abarrotes", "unidad", "900", "1500", "70", "10"),
    ("ASE-001", "Jabon en Polvo 1kg", "Aseo", "unidad", "5500", "7500", "25", "8"),
    ("ASE-002", "Detergente Liquido 1L", "Aseo", "unidad", "7000", "9500", "5", "8"),
    ("BEB-001", "Gaseosa Cola 1.5L", "Bebidas", "unidad", "3200", "4500", "50", "12"),
]

PARTNERS = [
    (PartnerType.PROVEEDOR, "Distribuidora El Trigal", "900123456-1", "3001234567"),
    (PartnerType.CLIENTE, "Consumidor Final Frecuente", None, "3009876543"),
    (PartnerType.AMBOS, "Comercializadora La Cosecha", "900654321-2", "3005556677"),
]


def run() -> None:
    settings = get_settings()
    hasher = BcryptPasswordHasher()

    with SqlAlchemyUnitOfWork() as uow:
        if uow.users.get_by_email(settings.admin_email) is None:
            uow.users.add(
                User(
                    id=None,
                    email=settings.admin_email,
                    password_hash=hasher.hash(settings.admin_password),
                    full_name=settings.admin_full_name,
                )
            )
            print(f"Usuario admin creado: {settings.admin_email}")

        category_ids: dict[str, int] = {}
        for name in CATEGORIES:
            existing = uow.categories.get_by_name(name)
            if existing is None:
                existing = uow.categories.add(Category(id=None, name=name))
                print(f"Categoria creada: {name}")
            category_ids[name] = existing.id

        for sku, name, cat_name, unit, cost, sale, stock, min_stock in PRODUCTS:
            if uow.products.get_by_sku(sku) is None:
                uow.products.add(
                    Product(
                        id=None,
                        sku=sku,
                        name=name,
                        category_id=category_ids[cat_name],
                        unit_of_measure=unit,
                        cost_price=Decimal(cost),
                        sale_price=Decimal(sale),
                        current_stock=Decimal(stock),
                        min_stock=Decimal(min_stock),
                    )
                )
                print(f"Producto creado: {sku} - {name}")

        existing_partner_names = {p.name for p in uow.partners.list()}
        for ptype, name, document_id, phone in PARTNERS:
            if name not in existing_partner_names:
                uow.partners.add(
                    Partner(id=None, type=ptype, name=name, document_id=document_id, phone=phone)
                )
                print(f"Tercero creado: {name}")

        uow.commit()

    print("Seed completado.")


if __name__ == "__main__":
    run()
