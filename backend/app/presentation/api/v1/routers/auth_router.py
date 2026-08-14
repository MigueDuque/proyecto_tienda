from fastapi import APIRouter, Depends

from app.application.use_cases.auth.login import LoginUseCase
from app.domain.entities.user import User
from app.presentation.api.v1.deps import get_current_user, get_login_use_case
from app.presentation.api.v1.schemas.auth_schemas import LoginRequest, MeResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> TokenResponse:
    result = use_case.execute(payload.email, payload.password)
    return TokenResponse(access_token=result.access_token, token_type=result.token_type)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=current_user.id, email=current_user.email, full_name=current_user.full_name
    )
