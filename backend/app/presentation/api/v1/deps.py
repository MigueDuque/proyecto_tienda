from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.interfaces import PasswordHasher, TokenService
from app.application.unit_of_work import AbstractUnitOfWork
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.categories.category_use_cases import (
    CreateCategoryUseCase,
    DeleteCategoryUseCase,
    GetCategoryUseCase,
    ListCategoriesUseCase,
    UpdateCategoryUseCase,
)
from app.application.use_cases.inventory.inventory_use_cases import (
    AdjustStockUseCase,
    GetKardexUseCase,
    ListInventoryMovementsUseCase,
)
from app.application.use_cases.partners.partner_use_cases import (
    CreatePartnerUseCase,
    DeletePartnerUseCase,
    GetPartnerUseCase,
    ListPartnersUseCase,
    UpdatePartnerUseCase,
)
from app.application.use_cases.products.product_use_cases import (
    CreateProductUseCase,
    DeleteProductUseCase,
    GetProductUseCase,
    ListLowStockProductsUseCase,
    ListProductsUseCase,
    UpdateProductUseCase,
)
from app.application.use_cases.purchases.register_purchase import (
    GetPurchaseUseCase,
    ListPurchasesUseCase,
    RegisterPurchaseUseCase,
)
from app.application.use_cases.sales.register_sale import (
    GetSaleUseCase,
    ListSalesUseCase,
    RegisterSaleUseCase,
)
from app.domain.entities.user import User
from app.domain.exceptions import InvalidCredentialsError
from app.infrastructure.config import Settings, get_settings
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.jwt_handler import JwtTokenService
from app.infrastructure.security.password_hasher import BcryptPasswordHasher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_uow() -> Generator[AbstractUnitOfWork, None, None]:
    yield SqlAlchemyUnitOfWork()


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


def get_token_service(settings: Settings = Depends(get_settings)) -> TokenService:
    return JwtTokenService(settings)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    uow: AbstractUnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
) -> User:
    try:
        subject = token_service.decode_subject(token)
        with uow as u:
            user = u.users.get_by_id(int(subject))
    except (InvalidCredentialsError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# --- Auth ---
def get_login_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> LoginUseCase:
    return LoginUseCase(uow, password_hasher, token_service)


# --- Categories ---
def get_create_category_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> CreateCategoryUseCase:
    return CreateCategoryUseCase(uow)


def get_update_category_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> UpdateCategoryUseCase:
    return UpdateCategoryUseCase(uow)


def get_delete_category_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> DeleteCategoryUseCase:
    return DeleteCategoryUseCase(uow)


def get_get_category_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> GetCategoryUseCase:
    return GetCategoryUseCase(uow)


def get_list_categories_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> ListCategoriesUseCase:
    return ListCategoriesUseCase(uow)


# --- Products ---
def get_create_product_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> CreateProductUseCase:
    return CreateProductUseCase(uow)


def get_update_product_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> UpdateProductUseCase:
    return UpdateProductUseCase(uow)


def get_delete_product_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> DeleteProductUseCase:
    return DeleteProductUseCase(uow)


def get_get_product_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> GetProductUseCase:
    return GetProductUseCase(uow)


def get_list_products_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> ListProductsUseCase:
    return ListProductsUseCase(uow)


def get_list_low_stock_products_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> ListLowStockProductsUseCase:
    return ListLowStockProductsUseCase(uow)


# --- Partners ---
def get_create_partner_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> CreatePartnerUseCase:
    return CreatePartnerUseCase(uow)


def get_update_partner_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> UpdatePartnerUseCase:
    return UpdatePartnerUseCase(uow)


def get_delete_partner_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> DeletePartnerUseCase:
    return DeletePartnerUseCase(uow)


def get_get_partner_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> GetPartnerUseCase:
    return GetPartnerUseCase(uow)


def get_list_partners_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> ListPartnersUseCase:
    return ListPartnersUseCase(uow)


# --- Purchases ---
def get_register_purchase_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> RegisterPurchaseUseCase:
    return RegisterPurchaseUseCase(uow)


def get_list_purchases_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> ListPurchasesUseCase:
    return ListPurchasesUseCase(uow)


def get_get_purchase_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> GetPurchaseUseCase:
    return GetPurchaseUseCase(uow)


# --- Sales ---
def get_register_sale_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> RegisterSaleUseCase:
    return RegisterSaleUseCase(uow)


def get_list_sales_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> ListSalesUseCase:
    return ListSalesUseCase(uow)


def get_get_sale_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> GetSaleUseCase:
    return GetSaleUseCase(uow)


# --- Inventory ---
def get_adjust_stock_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> AdjustStockUseCase:
    return AdjustStockUseCase(uow)


def get_get_kardex_use_case(uow: AbstractUnitOfWork = Depends(get_uow)) -> GetKardexUseCase:
    return GetKardexUseCase(uow)


def get_list_inventory_movements_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> ListInventoryMovementsUseCase:
    return ListInventoryMovementsUseCase(uow)
