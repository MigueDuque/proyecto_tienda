from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    DomainError,
    DuplicateError,
    InvalidCredentialsError,
    NotFoundError,
)
from app.infrastructure.config import get_settings
from app.presentation.api.v1.routers.auth_router import router as auth_router
from app.presentation.api.v1.routers.categories_router import router as categories_router
from app.presentation.api.v1.routers.inventory_router import router as inventory_router
from app.presentation.api.v1.routers.partners_router import router as partners_router
from app.presentation.api.v1.routers.products_router import router as products_router
from app.presentation.api.v1.routers.purchases_router import router as purchases_router
from app.presentation.api.v1.routers.sales_router import router as sales_router

settings = get_settings()

app = FastAPI(title="Granero API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _domain_error_status(exc: DomainError) -> int:
    if isinstance(exc, NotFoundError):
        return 404
    if isinstance(exc, DuplicateError):
        return 409
    if isinstance(exc, InvalidCredentialsError):
        return 401
    return 400


@app.exception_handler(DomainError)
def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=_domain_error_status(exc), content={"detail": str(exc)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(partners_router, prefix="/api/v1")
app.include_router(purchases_router, prefix="/api/v1")
app.include_router(sales_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
