from fastapi import APIRouter, Depends

from app.application.use_cases.purchases.register_purchase import (
    GetPurchaseUseCase,
    ListPurchasesUseCase,
    PurchaseItemInput,
    RegisterPurchaseInput,
    RegisterPurchaseUseCase,
)
from app.presentation.api.v1.deps import (
    get_current_user,
    get_get_purchase_use_case,
    get_list_purchases_use_case,
    get_register_purchase_use_case,
)
from app.presentation.api.v1.schemas.purchase_schemas import PurchaseCreateRequest, PurchaseResponse

router = APIRouter(prefix="/purchases", tags=["purchases"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[PurchaseResponse])
def list_purchases(use_case: ListPurchasesUseCase = Depends(get_list_purchases_use_case)):
    return use_case.execute()


@router.post("", response_model=PurchaseResponse, status_code=201)
def create_purchase(
    payload: PurchaseCreateRequest,
    use_case: RegisterPurchaseUseCase = Depends(get_register_purchase_use_case),
):
    data = RegisterPurchaseInput(
        partner_id=payload.partner_id,
        payment_method=payload.payment_method,
        items=[
            PurchaseItemInput(
                product_id=item.product_id, quantity=item.quantity, unit_cost=item.unit_cost
            )
            for item in payload.items
        ],
    )
    return use_case.execute(data)


@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(purchase_id: int, use_case: GetPurchaseUseCase = Depends(get_get_purchase_use_case)):
    return use_case.execute(purchase_id)
