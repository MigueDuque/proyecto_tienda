from fastapi import APIRouter, Depends

from app.application.use_cases.dashboard.get_summary import GetDashboardSummaryUseCase
from app.presentation.api.v1.deps import get_current_user, get_dashboard_summary_use_case
from app.presentation.api.v1.schemas.dashboard_schemas import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(use_case: GetDashboardSummaryUseCase = Depends(get_dashboard_summary_use_case)):
    return use_case.execute()
