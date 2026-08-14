def _create_category(client, auth_headers, name="Granos"):
    response = client.post("/api/v1/categories", json={"name": name}, headers=auth_headers)
    assert response.status_code == 201
    return response.json()["id"]


def test_create_and_list_product(client, auth_headers):
    category_id = _create_category(client, auth_headers)

    create_response = client.post(
        "/api/v1/products",
        json={
            "sku": "GRA-001",
            "name": "Arroz Diana 500g",
            "category_id": category_id,
            "unit_of_measure": "unidad",
            "cost_price": "1800",
            "sale_price": "2500",
            "min_stock": "10",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    product = create_response.json()
    assert product["sku"] == "GRA-001"
    assert product["current_stock"] == "0"

    list_response = client.get("/api/v1/products", headers=auth_headers)
    assert list_response.status_code == 200
    assert any(p["sku"] == "GRA-001" for p in list_response.json())


def test_create_product_with_duplicate_sku_returns_409(client, auth_headers):
    category_id = _create_category(client, auth_headers)
    payload = {
        "sku": "GRA-001",
        "name": "Arroz Diana 500g",
        "category_id": category_id,
        "unit_of_measure": "unidad",
        "cost_price": "1800",
        "sale_price": "2500",
        "min_stock": "10",
    }
    assert client.post("/api/v1/products", json=payload, headers=auth_headers).status_code == 201
    duplicate = client.post("/api/v1/products", json=payload, headers=auth_headers)
    assert duplicate.status_code == 409


def test_create_product_with_unknown_category_returns_404(client, auth_headers):
    payload = {
        "sku": "GRA-001",
        "name": "Arroz Diana 500g",
        "category_id": 999,
        "unit_of_measure": "unidad",
        "cost_price": "1800",
        "sale_price": "2500",
        "min_stock": "10",
    }
    response = client.post("/api/v1/products", json=payload, headers=auth_headers)
    assert response.status_code == 404
