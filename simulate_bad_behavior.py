import requests
import time
import random

BASE_URL = "http://127.0.0.1:8000"

def simulate_overtrading():
    print("🤖 Simulating OVERTRADING behavior...")
    
    # Rule: > 5 trades in 1 hour with negative P&L
    
    # We will execute 6 rapid market orders
    # Since prices are random logic in Sim, we can't guarantee loss easily via market order alone 
    # unless we manipulate the engine.
    # However, let's just spam trades. The random walk might give us losses.
    # Alternatively, we can inject history directly if we had a debug endpoint, 
    # but let's try the "spam" approach first.
    
    symbol = "AAPL"
    
    for i in range(8):
        side = "buy" if i % 2 == 0 else "sell"
        # Increase size to simulate revenge trading too?
        qty = 10 * (i + 1)
        
        print(f"  > Placing order {i+1}: {side.upper()} {qty} {symbol}")
        try:
            res = requests.post(f"{BASE_URL}/trade/order", json={
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": "market"
            })
            if res.status_code == 200:
                print("    Success")
            else:
                print(f"    Failed: {res.text}")
        except Exception as e:
            print(f"    Error: {e}")
            
        time.sleep(0.5)

    print("\n✅ Simulation complete. Checking for detected biases...")
    time.sleep(1)
    
    try:
        biases = requests.get(f"{BASE_URL}/ai/biases").json()
        print(f"\n🧠 DETECTED BIASES: {len(biases)}")
        for b in biases:
            print(f"  - [{b['severity']}] {b['name']}: {b['description']}")
            
        if not biases:
            print("  (No biases detected. Sim might have been profitable by chance!)")
            
    except Exception as e:
        print(f"Error fetching biases: {e}")

if __name__ == "__main__":
    simulate_overtrading()
