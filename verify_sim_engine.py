import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def reset_sim(balance):
    print(f"🔄 Resetting Sim to ${balance}...")
    res = requests.post(f"{BASE_URL}/settings/sim/reset", json={"balance": balance})
    print(res.json())

def get_account():
    res = requests.get(f"{BASE_URL}/account")
    return res.json()

def place_order(symbol, qty, side, type, limit_price=None):
    print(f"📝 Placing {type} {side} order for {qty} {symbol}...")
    payload = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": "day"
    }
    if limit_price:
        payload["limit_price"] = limit_price
        
    res = requests.post(f"{BASE_URL}/trade/order", json=payload)
    if res.status_code == 200:
        print("✅ Order Submitted")
        return res.json()
    else:
        print(f"❌ Order Failed: {res.text}")
        return None

def test_sim_features():
    # Ensure we are in SIM mode
    requests.post(f"{BASE_URL}/settings/mode/sim")
    time.sleep(1)

    # 1. Test Reset
    reset_sim(50000)
    account = get_account()
    if account['cash'] == 50000:
        print("✅ Reset Confirmed: $50,000")
    else:
        print(f"❌ Reset Failed. Cash: {account['cash']}")

    # 2. Test Limit Order (Should be pending if price is far away)
    # Price of AAPL is around 150-250. Let's bid $10. Should wait.
    order = place_order("AAPL", 10, "buy", "limit", limit_price=10.0)
    
    # Check status
    if order and order['status'] == 'new':
        print("✅ Limit Order Pending (Correct behavior)")
    elif order:
        print(f"❌ Limit Order Status Unexpected: {order['status']}")

    # 3. Test Market Order (Should fill with slippage)
    order_mkt = place_order("AAPL", 5, "buy", "market")
    if order_mkt and order_mkt['status'] == 'filled':
        print(f"✅ Market Order Filled @ ${order_mkt['filled_avg_price']:.2f} (Slippage applied)")
    else:
        print(f"❌ Market Order Failed: {order_mkt}")

if __name__ == "__main__":
    test_sim_features()
