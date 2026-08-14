from decimal import Decimal

from pydantic import BaseModel

from app.presentation.api.v1.schemas.product_schemas import ProductResponse
from app.presentation.api.v1.schemas.purchase_schemas import PurchaseResponse
from app.presentation.api.v1.schemas.sale_schemas import SaleResponse


class DashboardSummaryResponse(BaseModel):
    sales_today_total: Decimal
    sales_month_total: Decimal
    cash_balance: Decimal
    low_stock_products: list[ProductResponse]
    recent_sales: list[SaleResponse]
    recent_purchases: list[PurchaseResponse]
