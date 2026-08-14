from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities.category import Category
from app.domain.exceptions import DuplicateError, NotFoundError


class CreateCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, name: str, description: str | None) -> Category:
        with self._uow as uow:
            if uow.categories.get_by_name(name) is not None:
                raise DuplicateError("Categoria", "name", name)
            category = uow.categories.add(Category(id=None, name=name, description=description))
            uow.commit()
            return category


class UpdateCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, category_id: int, name: str, description: str | None) -> Category:
        with self._uow as uow:
            existing = uow.categories.get_by_id(category_id)
            if existing is None:
                raise NotFoundError("Categoria", category_id)
            duplicate = uow.categories.get_by_name(name)
            if duplicate is not None and duplicate.id != category_id:
                raise DuplicateError("Categoria", "name", name)
            existing.name = name
            existing.description = description
            updated = uow.categories.update(existing)
            uow.commit()
            return updated


class DeleteCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, category_id: int) -> None:
        with self._uow as uow:
            if uow.categories.get_by_id(category_id) is None:
                raise NotFoundError("Categoria", category_id)
            uow.categories.delete(category_id)
            uow.commit()


class GetCategoryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, category_id: int) -> Category:
        with self._uow as uow:
            category = uow.categories.get_by_id(category_id)
            if category is None:
                raise NotFoundError("Categoria", category_id)
            return category


class ListCategoriesUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self) -> list[Category]:
        with self._uow as uow:
            return uow.categories.list()
