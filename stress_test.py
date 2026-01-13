import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def log_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}: {details}")

def run_stress_test():
    print("🔥 Starting System Robustness & Error Test 🔥\n")

    # 1. Malformed Order (Missing Fields)
    try:
        res = requests.post(f"{BASE_URL}/trade/order", json={"symbol": "AAPL"})
        # Expect 422 Unprocessable Entity (FastAPI default validation)
        log_result("Malformed JSON", res.status_code == 422, f"Got {res.status_code}")
    except Exception as e:
        log_result("Malformed JSON", False, str(e))

    # 2. Invalid Symbol
    # Sim adapter might generally accept strings, but let's see if empty string fails
    try:
        res = requests.post(f"{BASE_URL}/trade/order", json={
            "symbol": "", "qty": 1, "side": "buy", "type": "market"
        })
        # Expect 400 or 422 or handled error
        log_result("Empty Symbol", res.status_code in [400, 422], f"Got {res.status_code} - {res.text}")
    except Exception as e:
        log_result("Empty Symbol", False, str(e))

    # 3. Insufficient Funds
    # Cash is $100k. Try buying $1B
    try:
        res = requests.post(f"{BASE_URL}/trade/order", json={
            "symbol": "AAPL", "qty": 10000000, "side": "buy", "type": "market"
        })
        # Expect 400 Bad Request
        log_result("Insufficient Funds", res.status_code == 400, f"Got {res.status_code} - {res.text}")
    except Exception as e:
        log_result("Insufficient Funds", False, str(e))

    # 4. Invalid Analytics Period
    try:
        res = requests.get(f"{BASE_URL}/analytics/metrics?period=INVALID")
        # Expect 400 or 500 (if not handled)
        # Ideally should be 400.
        log_result("Invalid Period", res.status_code != 500, f"Got {res.status_code}")
    except Exception as e:
        log_result("Invalid Period", False, str(e))

    # 5. Method Not Allowed
    try:
        res = requests.get(f"{BASE_URL}/trade/order") # Should be POST
        log_result("Method Not Allowed", res.status_code == 405, f"Got {res.status_code}")
    except Exception as e:
        log_result("Method Not Allowed", False, str(e))
        
    print("\n-------------------------------------------")
    print("Test Complete.")

if __name__ == "__main__":
    run_stress_test()
