from fastapi import APIRouter, Depends

from app.application.use_cases.products.product_use_cases import (
    CreateProductUseCase,
    DeleteProductUseCase,
    GetProductUseCase,
    ListLowStockProductsUseCase,
    ListProductsUseCase,
    ProductInput,
    UpdateProductUseCase,
)
from app.presentation.api.v1.deps import (
    get_create_product_use_case,
    get_current_user,
    get_delete_product_use_case,
    get_get_product_use_case,
    get_list_low_stock_products_use_case,
    get_list_products_use_case,
    get_update_product_use_case,
)
from app.presentation.api.v1.schemas.product_schemas import ProductCreateRequest, ProductResponse

router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)])


def _to_input(payload: ProductCreateRequest) -> ProductInput:
    return ProductInput(
        sku=payload.sku,
        name=payload.name,
        category_id=payload.category_id,
        unit_of_measure=payload.unit_of_measure,
        cost_price=payload.cost_price,
        sale_price=payload.sale_price,
        min_stock=payload.min_stock,
        description=payload.description,
        is_active=payload.is_active,
    )


@router.get("", response_model=list[ProductResponse])
def list_products(
    category_id: int | None = None,
    only_active: bool = False,
    use_case: ListProductsUseCase = Depends(get_list_products_use_case),
):
    return use_case.execute(category_id=category_id, only_active=only_active)


@router.get("/low-stock", response_model=list[ProductResponse])
def list_low_stock_products(
    use_case: ListLowStockProductsUseCase = Depends(get_list_low_stock_products_use_case),
):
    return use_case.execute()


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    payload: ProductCreateRequest,
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
):
    return use_case.execute(_to_input(payload))


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, use_case: GetProductUseCase = Depends(get_get_product_use_case)):
    return use_case.execute(product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductCreateRequest,
    use_case: UpdateProductUseCase = Depends(get_update_product_use_case),
):
    return use_case.execute(product_id, _to_input(payload))


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int, use_case: DeleteProductUseCase = Depends(get_delete_product_use_case)
):
    use_case.execute(product_id)
