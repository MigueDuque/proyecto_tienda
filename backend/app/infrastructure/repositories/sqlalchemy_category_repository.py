from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.category import Category
from app.domain.exceptions import NotFoundError
from app.domain.repositories.category_repository import CategoryRepository
from app.infrastructure.db.models.category_model import CategoryModel


def _to_domain(model: CategoryModel) -> Category:
    return Category(id=model.id, name=model.name, description=model.description)


class SqlAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, category: Category) -> Category:
        model = CategoryModel(name=category.name, description=category.description)
        self._session.add(model)
        self._session.flush()
        return _to_domain(model)

    def update(self, category: Category) -> Category:
        model = self._session.get(CategoryModel, category.id)
        if model is None:
            raise NotFoundError("Categoria", category.id)
        model.name = category.name
        model.description = category.description
        self._session.flush()
        return _to_domain(model)

    def delete(self, category_id: int) -> None:
        model = self._session.get(CategoryModel, category_id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def get_by_id(self, category_id: int) -> Category | None:
        model = self._session.get(CategoryModel, category_id)
        return _to_domain(model) if model else None

    def get_by_name(self, name: str) -> Category | None:
        stmt = select(CategoryModel).where(CategoryModel.name == name)
        model = self._session.execute(stmt).scalar_one_or_none()
        return _to_domain(model) if model else None

    def list(self) -> list[Category]:
        stmt = select(CategoryModel).order_by(CategoryModel.name)
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(m) for m in models]
