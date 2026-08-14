from fastapi import APIRouter, Depends

from app.application.use_cases.categories.category_use_cases import (
    CreateCategoryUseCase,
    DeleteCategoryUseCase,
    GetCategoryUseCase,
    ListCategoriesUseCase,
    UpdateCategoryUseCase,
)
from app.presentation.api.v1.deps import (
    get_create_category_use_case,
    get_current_user,
    get_delete_category_use_case,
    get_get_category_use_case,
    get_list_categories_use_case,
    get_update_category_use_case,
)
from app.presentation.api.v1.schemas.category_schemas import (
    CategoryCreateRequest,
    CategoryResponse,
)

router = APIRouter(
    prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[CategoryResponse])
def list_categories(use_case: ListCategoriesUseCase = Depends(get_list_categories_use_case)):
    return use_case.execute()


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    payload: CategoryCreateRequest,
    use_case: CreateCategoryUseCase = Depends(get_create_category_use_case),
):
    return use_case.execute(payload.name, payload.description)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int, use_case: GetCategoryUseCase = Depends(get_get_category_use_case)
):
    return use_case.execute(category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryCreateRequest,
    use_case: UpdateCategoryUseCase = Depends(get_update_category_use_case),
):
    return use_case.execute(category_id, payload.name, payload.description)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int, use_case: DeleteCategoryUseCase = Depends(get_delete_category_use_case)
):
    use_case.execute(category_id)
