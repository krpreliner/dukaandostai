import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import init_db, SessionLocal
from app.database.models import User, Store, StoreMember, Product, Customer
from app.auth.security import create_access_token

client = TestClient(app)

TEST_RUN_ID = uuid.uuid4().hex[:6]
TEST_EMAIL = f"owner_{TEST_RUN_ID}@example.com"
STAFF_EMAIL = f"staff_{TEST_RUN_ID}@example.com"

@pytest.fixture(scope="module")
def setup_test_env():
    init_db()
    db = SessionLocal()
    yield db
    db.close()


def test_01_user_registration_success(setup_test_env):
    """Test successful user registration creates user, store workspace, and tokens."""
    payload = {
        "email": TEST_EMAIL,
        "password": "SecurePassword123!",
        "full_name": "Test Store Owner",
        "store_name": "Gupta Provision Store",
        "store_location": "Dhanbad, Jharkhand"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == TEST_EMAIL
    assert len(data["stores"]) >= 1
    assert data["stores"][0]["role"] == "OWNER"
    assert data["stores"][0]["name"] == "Gupta Provision Store"


def test_02_user_registration_duplicate_email(setup_test_env):
    """Test registering with an existing email returns 400 Bad Request."""
    payload = {
        "email": TEST_EMAIL,
        "password": "AnotherPassword123!",
        "full_name": "Duplicate Tester",
        "store_name": "Duplicate Store"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_03_user_login_success(setup_test_env):
    """Test valid user login returns access and refresh tokens."""
    payload = {
        "email": TEST_EMAIL,
        "password": "SecurePassword123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == TEST_EMAIL


def test_04_user_login_invalid_password(setup_test_env):
    """Test login with incorrect password returns 401 Unauthorized."""
    payload = {
        "email": TEST_EMAIL,
        "password": "WrongPassword999!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_05_get_current_profile(setup_test_env):
    """Test /api/auth/me returns profile and store memberships."""
    # First login to get token
    login_res = client.post("/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": "SecurePassword123!"
    })
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == TEST_EMAIL
    assert len(data["stores"]) >= 1


def test_06_token_refresh(setup_test_env):
    """Test token refresh returns new access token."""
    login_res = client.post("/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": "SecurePassword123!"
    })
    refresh_tok = login_res.json()["refresh_token"]

    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_tok})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_07_create_store_workspace(setup_test_env):
    """Test authenticated user creating an additional store workspace."""
    login_res = client.post("/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": "SecurePassword123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/auth/stores", json={
        "name": "Gupta Branch 2",
        "location": "Bokaro, Jharkhand"
    }, headers=headers)
    assert create_res.status_code == 200
    data = create_res.json()
    assert data["status"] == "SUCCESS"
    assert data["store"]["name"] == "Gupta Branch 2"
    assert data["store"]["role"] == "OWNER"


def test_08_rbac_and_store_member_assignment(setup_test_env):
    """Test store owner assigning a staff member with VIEWER role."""
    # Register a second user to become staff
    client.post("/api/auth/register", json={
        "email": STAFF_EMAIL,
        "password": "StaffPassword123!",
        "full_name": "Rohan Kumar",
        "store_name": "Rohan Store"
    })

    # Owner login
    login_res = client.post("/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": "SecurePassword123!"
    })
    owner_token = login_res.json()["access_token"]
    store_id = login_res.json()["stores"][0]["store_id"]
    headers = {"Authorization": f"Bearer {owner_token}"}

    # Add staff_member as VIEWER to owner's store
    add_res = client.post(
        f"/api/auth/stores/{store_id}/members",
        json={"email": STAFF_EMAIL, "role": "VIEWER"},
        headers=headers
    )
    assert add_res.status_code == 200

    # Retrieve members list
    members_res = client.get(f"/api/auth/stores/{store_id}/members", headers=headers)
    assert members_res.status_code == 200
    members = members_res.json()
    emails = [m["email"] for m in members]
    assert STAFF_EMAIL in emails


def test_09_multi_tenant_data_isolation(setup_test_env):
    """
    Test strict multi-tenant data isolation:
    Store STORE_001 records must not be returned when querying with a different X-Store-Id.
    """
    db = setup_test_env

    # Verify STORE_001 has products
    store_1_products = db.query(Product).filter(Product.store_id == "STORE_001").all()
    assert len(store_1_products) > 0

    # Query with a non-existent or separate store ID
    tenant_2_id = "STORE_ISOLATED_TEST_99"
    response = client.get("/api/products", headers={"X-Store-Id": tenant_2_id})
    assert response.status_code == 200
    tenant_2_products = response.json()
    # Should be empty because no products were created for tenant 2
    assert len(tenant_2_products) == 0

    # Now query default STORE_001
    response_1 = client.get("/api/products", headers={"X-Store-Id": "STORE_001"})
    assert response_1.status_code == 200
    assert len(response_1.json()) == len(store_1_products)
