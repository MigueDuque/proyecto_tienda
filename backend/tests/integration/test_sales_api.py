def _setup_product_with_stock(client, auth_headers):
    category_id = client.post(
        "/api/v1/categories", json={"name": "Granos"}, headers=auth_headers
    ).json()["id"]
    product = client.post(
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
    ).json()
    supplier = client.post(
        "/api/v1/partners",
        json={"type": "PROVEEDOR", "name": "Distribuidora El Trigal"},
        headers=auth_headers,
    ).json()

    purchase_response = client.post(
        "/api/v1/purchases",
        json={
            "partner_id": supplier["id"],
            "payment_method": "CONTADO",
            "items": [{"product_id": product["id"], "quantity": "20", "unit_cost": "1800"}],
        },
        headers=auth_headers,
    )
    assert purchase_response.status_code == 201
    return product["id"]


def test_full_sale_flow_updates_stock_and_creates_balanced_journal_entry(client, auth_headers):
    product_id = _setup_product_with_stock(client, auth_headers)

    sale_response = client.post(
        "/api/v1/sales",
        json={
            "payment_method": "CONTADO",
            "items": [{"product_id": product_id, "quantity": "5", "unit_price": "2500"}],
        },
        headers=auth_headers,
    )
    assert sale_response.status_code == 201
    assert sale_response.json()["total"] == "12500"

    product = client.get(f"/api/v1/products/{product_id}", headers=auth_headers).json()
    assert product["current_stock"] == "15"

    kardex = client.get(f"/api/v1/inventory/kardex/{product_id}", headers=auth_headers).json()
    assert [m["movement_type"] for m in kardex] == ["ENTRADA_COMPRA", "SALIDA_VENTA"]

    entries = client.get("/api/v1/accounting/journal-entries", headers=auth_headers).json()
    sale_entry = next(e for e in entries if e["reference_type"] == "SALE")
    total_debit = sum(float(line["debit"]) for line in sale_entry["lines"])
    total_credit = sum(float(line["credit"]) for line in sale_entry["lines"])
    assert total_debit == total_credit


def test_sale_with_insufficient_stock_returns_400(client, auth_headers):
    product_id = _setup_product_with_stock(client, auth_headers)

    response = client.post(
        "/api/v1/sales",
        json={
            "payment_method": "CONTADO",
            "items": [{"product_id": product_id, "quantity": "9999", "unit_price": "2500"}],
        },
        headers=auth_headers,
    )
    assert response.status_code == 400
