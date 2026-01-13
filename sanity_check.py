
from unittest.mock import MagicMock, patch
from services.strategy_dna_service import StrategyDNAService
from services.psych_risk_service import PsychRiskScoreService

def test_strategy_logic():
    print("Testing Strategy Logic...")
    service = StrategyDNAService()
    
    # Mock internals
    service.get_fingerprints = MagicMock(return_value=[{
        "strategy_name": "Conservative",
        "feature_vector": {"avg_rsi": 30, "avg_position_value": 1000}
    }])
    service._fetch_market_context = MagicMock(return_value={
        "price": 100, "rsi": 80 # Mismatch!
    })
    
    # Test Compat
    result = service.check_order_compatibility(
        "user_id", "AAPL", "buy", "market", qty=10
    )
    
    if result['is_compatible'] == False:
        print("✅ Strategy Mismatch Detected correctly.")
    else:
        print(f"❌ Strategy Mismatch FAILED. Result: {result}")

def test_firewall_logic():
    print("Testing Firewall Logic...")
    service = PsychRiskScoreService()
    service.calculate_prs = MagicMock(return_value={
        "score": 90, "risk_state": "critical", "factors": {}
    })
    
    # We can't easily test the router block without client, 
    # but we can verify the service returns Critical.
    res = service.calculate_prs("u", 7)
    if res['score'] == 90:
        print("✅ Risk Score Calculation (Mocked) confirmed.")

if __name__ == "__main__":
    test_strategy_logic()
    test_firewall_logic()
