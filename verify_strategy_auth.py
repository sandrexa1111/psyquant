
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch

# SIMPLE VERIFICATION SCRIPT

def mock_get_current_user():
    user = MagicMock()
    user.id = "test-user-id"
    return user

def run():
    print("Starting Verification...")
    
    # 1. Check Protection
    client = TestClient(app)
    # Ensure no override
    app.dependency_overrides = {}
    
    try:
        resp = client.get("/ai/skill-score")
        if resp.status_code == 401:
            print("✅ /ai/skill-score is Protected (401)")
        else:
            print(f"❌ /ai/skill-score FAIL: {resp.status_code}")
    except Exception as e:
        print(f"Error checking protection: {e}")

    # 2. Check Logic
    app.dependency_overrides["routers.auth.get_current_user"] = mock_get_current_user
    
    # Manually start patches
    p1 = patch("services.strategy_dna_service.StrategyDNAService.get_fingerprints")
    p2 = patch("services.strategy_dna_service.StrategyDNAService._fetch_market_context")
    p4 = patch("config.api.submit_order")
    
    mock_get_fp = p1.start()
    mock_market = p2.start()
    mock_submit = p4.start()
    
    try:
        # Scenario: Strategy Mismatch
        mock_get_fp.return_value = [{
            "strategy_name": "Dip Buy",
            "feature_vector": {"avg_rsi": 30, "avg_position_value": 10000}
        }]
        
        # Current Market: RSI 80 (Overbought)
        mock_market.return_value = {"price": 100, "rsi": 80}
        
        print("Submitting Mismatch Order...")
        resp = client.post("/trade/order", json={
            "symbol": "TSLA",
            "qty": 100, 
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
            "override_risk": True # Bypass risk firewall to test strategy
        }, headers={"Authorization": "Bearer mock"})
        
        if resp.status_code == 400 and "STRATEGY_MISMATCH" in str(resp.json()):
            print("✅ Strategy Mismatch Triggered Correctly!")
            print(f"   Message: {resp.json()['detail']['message']}")
        else:
            print(f"❌ Mismatch Failed. Status: {resp.status_code}, Body: {resp.json()}")
            
    except Exception as e:
        print(f"Logic Test Error: {e}")
    finally:
        p1.stop()
        p2.stop()
        p4.stop()

if __name__ == "__main__":
    run()
