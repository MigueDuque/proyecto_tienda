from fastapi import APIRouter, Depends

from app.application.use_cases.inventory.inventory_use_cases import (
    AdjustStockInput,
    AdjustStockUseCase,
    GetKardexUseCase,
    ListInventoryMovementsUseCase,
)
from app.presentation.api.v1.deps import (
    get_adjust_stock_use_case,
    get_current_user,
    get_get_kardex_use_case,
    get_list_inventory_movements_use_case,
)
from app.presentation.api.v1.schemas.inventory_schemas import (
    InventoryMovementResponse,
    StockAdjustmentRequest,
)

router = APIRouter(prefix="/inventory", tags=["inventory"], dependencies=[Depends(get_current_user)])


@router.get("/movements", response_model=list[InventoryMovementResponse])
def list_movements(
    product_id: int | None = None,
    use_case: ListInventoryMovementsUseCase = Depends(get_list_inventory_movements_use_case),
):
    return use_case.execute(product_id=product_id)


@router.get("/kardex/{product_id}", response_model=list[InventoryMovementResponse])
def get_kardex(product_id: int, use_case: GetKardexUseCase = Depends(get_get_kardex_use_case)):
    return use_case.execute(product_id)


@router.post("/adjustments", response_model=InventoryMovementResponse, status_code=201)
def create_adjustment(
    payload: StockAdjustmentRequest,
    use_case: AdjustStockUseCase = Depends(get_adjust_stock_use_case),
):
    data = AdjustStockInput(
        product_id=payload.product_id, quantity_delta=payload.quantity_delta, notes=payload.notes
    )
    return use_case.execute(data)
