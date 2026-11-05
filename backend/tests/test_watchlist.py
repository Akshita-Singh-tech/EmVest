from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_watchlist_crud_lifecycle():
    symbol = "SUNPHARMA"

    # 1. Clean up if already exists
    client.delete(f"/api/v1/watchlist/{symbol}")

    # 2. Add item to watchlist
    create_payload = {
        "symbol": symbol,
        "name": "Sun Pharmaceutical Industries Ltd",
        "sector": "Pharmaceuticals & Healthcare",
        "notes": "Strong specialty dermatology ramp-up.",
    }
    post_res = client.post("/api/v1/watchlist", json=create_payload)
    assert post_res.status_code == 201
    created = post_res.json()
    assert created["symbol"] == symbol
    assert created["sector"] == "Pharmaceuticals & Healthcare"

    # 3. Prevent duplicate addition
    dup_res = client.post("/api/v1/watchlist", json=create_payload)
    assert dup_res.status_code == 400

    # 4. List items and verify presence
    list_res = client.get("/api/v1/watchlist")
    assert list_res.status_code == 200
    items = list_res.json()
    symbols = [item["symbol"] for item in items]
    assert symbol in symbols

    # 5. Delete item
    del_res = client.delete(f"/api/v1/watchlist/{symbol}")
    assert del_res.status_code == 204

    # 6. Verify item removed
    list_res_after = client.get("/api/v1/watchlist")
    assert list_res_after.status_code == 200
    symbols_after = [item["symbol"] for item in list_res_after.json()]
    assert symbol not in symbols_after
