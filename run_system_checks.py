
import jwt
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
import json
import uuid
import config

# --- SETUP ---
client = TestClient(app)

def generate_token(user_id):
    # Matches routers/auth.py signature verification using config.JWT_SECRET
    payload = {
        "sub": user_id, 
        "email": f"{user_id}@test.com", 
        "user_metadata": {"full_name": "Test User"}
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

USER_A = "11111111-1111-1111-1111-111111111111"
USER_B = "22222222-2222-2222-2222-222222222222"
TOKEN_A = generate_token(USER_A)
TOKEN_B = generate_token(USER_B)

def banner(title):
    print(f"\n{'='*60}\n {title}\n{'='*60}")

def run_checks():
    
    # Global Patches
    p_market = patch("services.strategy_dna_service.StrategyDNAService._fetch_market_context")
    mock_market = p_market.start()
    mock_market.return_value = {"price": 100.0, "rsi": 85.0}
    
    p_submit = patch("config.api.submit_order")
    mock_submit = p_submit.start()
    mock_submit.return_value = {"id": str(uuid.uuid4()), "status": "filled"}
    
    p_fingerprints = patch("services.strategy_dna_service.StrategyDNAService.get_fingerprints")
    mock_get_fp = p_fingerprints.start()
    
    p_risk = patch("services.psych_risk_service.PsychRiskScoreService.calculate_prs")
    mock_prs = p_risk.start()
    
    try:
        # 1. STRATEGY MISMATCH
        banner("1. Strategy Mismatch Test")
        
        def get_fp_side_effect(user_id):
            if user_id == USER_A:
                return [{
                    "strategy_name": "Dip Buying", 
                    "feature_vector": {"avg_rsi": 30, "avg_position_value": 5000}
                }]
            return []
        mock_get_fp.side_effect = get_fp_side_effect
        mock_prs.return_value = {"score": 20, "risk_state": "low"}
        
        print(f"Action: User A buys at RSI 85 (Strategy expects RSI 30)")
        resp = client.post("/trade/order", json={
            "symbol": "BTC/USD", "qty": 0.5, "side": "buy", "type": "market", "time_in_force": "gtc"
        }, headers={"Authorization": f"Bearer {TOKEN_A}"})
        
        if resp.status_code == 400 and "STRATEGY_MISMATCH" in str(resp.json()):
            print("✅ SUCCESS: Blocked with STRATEGY_MISMATCH")
        else:
            print(f"❌ FAIL: Status {resp.status_code}, Body: {resp.json()}")

        # 2. FIREWALL TEST
        banner("2. Firewall Test")
        mock_prs.return_value = {"score": 90, "risk_state": "critical", "factors": {"stress": "high"}}
        
        print("Action: User A tries to trade with Risk Score 90")
        resp = client.post("/trade/order", json={
            "symbol": "BTC/USD", "qty": 0.5, "side": "buy", "type": "market", "time_in_force": "gtc"
        }, headers={"Authorization": f"Bearer {TOKEN_A}"})
        
        if resp.status_code == 403 and "RISK_FIREWALL_BLOCK" in str(resp.json()):
            print("✅ SUCCESS: Blocked with RISK_FIREWALL_BLOCK")
        else:
            print(f"❌ FAIL: Status {resp.status_code}, Body: {resp.json()}")

        # 3. MULTI-USER TEST
        banner("3. Multi-User Isolation Test")
        resp_a = client.get("/ai/strategy-dna", headers={"Authorization": f"Bearer {TOKEN_A}"})
        resp_b = client.get("/ai/strategy-dna", headers={"Authorization": f"Bearer {TOKEN_B}"})
        
        if len(resp_a.json().get('fingerprints', [])) > 0 and len(resp_b.json().get('fingerprints', [])) == 0:
            print("✅ SUCCESS: Isolation Confirmed.")
        else:
            print(f"❌ FAIL: Isolation broken or mocking issue.")

        # 4. TOKEN FAILURE
        banner("4. Token Failure Test")
        resp = client.get("/ai/skill-score")
        if resp.status_code == 401:
            print("✅ SUCCESS: Rejected with 401 Unauthorized")
        else:
            print(f"❌ FAIL: Accepted without token! Code: {resp.status_code}")
            
    except Exception as e:
        print(f"🔥 CRASH: {e}")
        import traceback
        traceback.print_exc()
    finally:
        p_market.stop()
        p_submit.stop()
        p_fingerprints.stop()
        p_risk.stop()

if __name__ == "__main__":
    run_checks()
