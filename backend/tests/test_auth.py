import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_auth_signup_login_me():
    unique_email = f"user_{uuid.uuid4().hex[:8]}@emvest.local"
    password = "SecurePassword123!"

    # 1. Signup
    signup_payload = {
        "email": unique_email,
        "full_name": "Test Trader",
        "password": password,
    }
    signup_res = client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201
    signup_data = signup_res.json()
    assert "access_token" in signup_data
    token = signup_data["access_token"]
    assert signup_data["user"]["email"] == unique_email

    # 2. Login
    login_payload = {
        "email": unique_email,
        "password": password,
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    # 3. Read current user /me
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == unique_email
    assert me_data["full_name"] == "Test Trader"

