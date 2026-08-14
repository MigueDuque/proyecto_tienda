from tests.integration.conftest import ADMIN_EMAIL, ADMIN_PASSWORD


def test_login_with_valid_credentials_returns_token(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_me_with_valid_token_returns_current_user(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == ADMIN_EMAIL


def test_protected_endpoint_without_token_returns_401(client):
    response = client.get("/api/v1/products")
    assert response.status_code == 401
