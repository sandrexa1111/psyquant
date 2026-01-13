from config import api
import time

print("Running Snapshot Test...")
print("Running Snapshot Test...")
# Ensure we are in simulation mode by just trying to reset
try:
    # Reset to be clean
    if hasattr(api, 'reset_account'):
        api.reset_account(100000)
    else:
        print("API does not support reset_account. Are we in Sim mode?")
    
    # Submit Market Order
    print("Submitting Market Order...")
    order = api.submit_order(symbol="SPY", qty=1, side="buy", type="market")
    print(f"Order Submitted: {order['id']} Status: {order['status']}")
    
    # Check if snapshot exists
    if order['status'] == 'filled':
        sid = order['id']
        snap = api.get_trade_snapshot(sid)
        if snap:
            print("✅ Snapshot found!")
            print(f"Keys: {snap.keys()}")
            print(f"News items: {len(snap.get('news', []))}")
        else:
            print("❌ No snapshot found for filled order.")
    else:
        print("⚠️ Order not filled immediately.")

except Exception as e:
    print(f"❌ Error: {e}")
