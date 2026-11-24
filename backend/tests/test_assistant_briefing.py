import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.ai.tools import AssistantTools
from app.services.briefing_service import BriefingService
from app.services.assistant_service import AssistantService
from app.database.models import DailyBriefing, ChatMessage

@pytest.fixture(scope="module")
def client():
    init_db()
    return TestClient(app)

@pytest.fixture(scope="module")
def db_session():
    init_db()
    session = SessionLocal()
    yield session
    session.close()

def test_01_assistant_tools_deterministic_execution(db_session: Session):
    """Verify all deterministic assistant tools return verified business metrics from DB."""
    tools = AssistantTools(db_session, store_id="STORE_001")

    # 1. Sales summary
    sales = tools.get_sales_summary()
    assert sales["monthly_revenue_inr"] > 0
    assert sales["today_sales_inr"] > 0
    assert sales["total_transactions"] > 0

    # 2. Profit summary
    profit = tools.get_profit_summary()
    assert profit["gross_profit"] > 0
    assert profit["net_income"] == 8000.0 or profit["net_income"] > 0
    assert profit["target_income"] == 10000.0

    # 3. Inventory alerts
    inv = tools.get_inventory_alerts()
    assert "low_stock_count" in inv
    assert "low_stock_items" in inv

    # 4. Customer segments
    cust = tools.get_customer_segments()
    assert cust["total_customers"] == 120
    assert "inactive_dormant_customers" in cust
    assert "active_customers" in cust

    # 5. Marketing draft
    mkt = tools.generate_marketing_draft(offer_description="Special 5% discount on monthly ration for loyal customers", discount_pct=5.0)
    assert "message_hi" in mkt
    assert "message_en" in mkt
    assert len(mkt["message_hi"]) > 0

def test_02_briefing_service_generation(db_session: Session):
    """Verify AI Daily Business Briefing generates complete Hindi/Hinglish audio script and metrics."""
    svc = BriefingService(db_session, store_id="STORE_001")
    briefing = svc.generate_daily_briefing()

    assert briefing is not None
    assert briefing["briefing_date"] is not None
    assert "Sharma Ji" in briefing["greeting"]
    assert len(briefing["audio_script"]) > 0
    assert "बिक्री" in briefing["audio_script"] or "sales" in briefing["audio_script"].lower() or "bikri" in briefing["audio_script"].lower()
    assert len(briefing["growth_opportunities"]) > 0
    assert briefing["low_stock_count"] >= 0

def test_03_assistant_service_intent_and_tool_execution(db_session: Session):
    """Verify AssistantService parses user intent, executes deterministic tools, and returns response."""
    svc = AssistantService(db_session, store_id="STORE_001")
    
    # Stock alert query in Hinglish
    result = svc.process_chat_message(
        user_text="Sharma Ji ka stock status aur low stock items batao",
        session_id="TEST_SESSION_101"
    )

    assert result["role"] == "assistant"
    assert "get_inventory_alerts" in result["tools_used"]
    assert len(result["content"]) > 0
    assert len(result["suggested_actions"]) > 0

    # Retrieve history
    history = svc.get_chat_history(session_id="TEST_SESSION_101")
    assert len(history) >= 2  # user + assistant
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

    # Clear history
    deleted = svc.clear_chat_history(session_id="TEST_SESSION_101")
    assert deleted >= 2
    post_clear = svc.get_chat_history(session_id="TEST_SESSION_101")
    assert len(post_clear) == 0

def test_04_briefing_api_endpoints(client: TestClient):
    """Verify REST API endpoints for daily briefing."""
    # GET /api/briefing/latest
    res = client.get("/api/briefing/latest")
    assert res.status_code == 200
    data = res.json()
    assert "greeting" in data
    assert "audio_script" in data
    assert "today_sales" in data

    # POST /api/briefing/generate
    gen_res = client.post("/api/briefing/generate")
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert gen_data["briefing_date"] is not None

def test_05_assistant_api_endpoints(client: TestClient):
    """Verify REST API endpoints for conversational AI assistant."""
    session_id = "TEST_API_SESSION"

    # POST /api/assistant/chat
    chat_res = client.post(
        "/api/assistant/chat",
        json={"message": "Aaj kitna profit hua?", "session_id": session_id}
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["role"] == "assistant"
    assert "content" in chat_data
    assert len(chat_data["content"]) > 0

    # GET /api/assistant/history
    hist_res = client.get(f"/api/assistant/history?session_id={session_id}")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert len(hist_data) >= 2

    # DELETE /api/assistant/history
    del_res = client.delete(f"/api/assistant/history?session_id={session_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "SUCCESS"
