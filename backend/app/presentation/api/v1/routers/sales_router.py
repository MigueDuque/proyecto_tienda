from fastapi import APIRouter, Depends

from app.application.use_cases.sales.register_sale import (
    GetSaleUseCase,
    ListSalesUseCase,
    RegisterSaleInput,
    RegisterSaleUseCase,
    SaleItemInput,
)
from app.presentation.api.v1.deps import (
    get_current_user,
    get_get_sale_use_case,
    get_list_sales_use_case,
    get_register_sale_use_case,
)
from app.presentation.api.v1.schemas.sale_schemas import SaleCreateRequest, SaleResponse

router = APIRouter(prefix="/sales", tags=["sales"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[SaleResponse])
def list_sales(use_case: ListSalesUseCase = Depends(get_list_sales_use_case)):
    return use_case.execute()


@router.post("", response_model=SaleResponse, status_code=201)
def create_sale(
    payload: SaleCreateRequest,
    use_case: RegisterSaleUseCase = Depends(get_register_sale_use_case),
):
    data = RegisterSaleInput(
        partner_id=payload.partner_id,
        payment_method=payload.payment_method,
        items=[
            SaleItemInput(
                product_id=item.product_id, quantity=item.quantity, unit_price=item.unit_price
            )
            for item in payload.items
        ],
    )
    return use_case.execute(data)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, use_case: GetSaleUseCase = Depends(get_get_sale_use_case)):
    return use_case.execute(sale_id)
