from abc import ABC, abstractmethod

from app.domain.entities.category import Category


class CategoryRepository(ABC):
    @abstractmethod
    def add(self, category: Category) -> Category: ...

    @abstractmethod
    def update(self, category: Category) -> Category: ...

    @abstractmethod
    def delete(self, category_id: int) -> None: ...

    @abstractmethod
    def get_by_id(self, category_id: int) -> Category | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> Category | None: ...

    @abstractmethod
    def list(self) -> list[Category]: ...
