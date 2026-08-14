"""API integration tests run against an in-memory UnitOfWork (no real DB
needed), so they exercise the full FastAPI wiring - routing, schemas,
dependency injection, use cases - quickly and portably in CI.
"""

import pytest
from fastapi.testclient import TestClient

from app.domain.entities.user import User
from app.infrastructure.security.password_hasher import BcryptPasswordHasher
from app.main import app
from app.presentation.api.v1.deps import get_uow
from tests.unit.application.fakes.in_memory_uow import InMemoryUnitOfWork, seed_chart_of_accounts

ADMIN_EMAIL = "admin@granero-tests.com"
ADMIN_PASSWORD = "secret123"


@pytest.fixture()
def uow() -> InMemoryUnitOfWork:
    memory_uow = InMemoryUnitOfWork()
    seed_chart_of_accounts(memory_uow)
    hasher = BcryptPasswordHasher()
    memory_uow.users.add(
        User(
            id=None,
            email=ADMIN_EMAIL,
            password_hash=hasher.hash(ADMIN_PASSWORD),
            full_name="Admin Test",
        )
    )
    return memory_uow


@pytest.fixture()
def client(uow: InMemoryUnitOfWork):
    def override_get_uow():
        yield uow

    app.dependency_overrides[get_uow] = override_get_uow
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
