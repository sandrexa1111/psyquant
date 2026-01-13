import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def get_account():
    try:
        res = requests.get(f"{BASE_URL}/account")
        if res.status_code != 200:
            print(f"⚠️ API Error ({res.status_code}): {res.text}")
            return None
        return res.json()
    except Exception as e:
        print(f"Error fetching account: {e}")
        return None

def set_mode(mode):
    print(f"👉 Switching to {mode}...")
    res = requests.post(f"{BASE_URL}/settings/mode/{mode}")
    if res.status_code == 200:
        print(f"✅ Switched to {mode}")
        time.sleep(1) # Wait for reload
    else:
        print(f"❌ Failed to switch: {res.text}")

def run_test():
    print("🧪 Starting Data Isolation Verification...")

    # 1. Switch to SIM
    set_mode("sim")
    sim_account = get_account()
    if sim_account and "cash" in sim_account:
        print(f"SIM Account Cash: ${sim_account.get('cash', 0):,.2f}")
    else:
        print(f"❌ Failed to get Sim account logic. Data: {sim_account}")

    # 2. Switch to PAPER
    set_mode("paper")
    paper_account = get_account()
    
    if paper_account and "cash" in paper_account:
        print(f"PAPER Account Cash: ${paper_account.get('cash', 0):,.2f}")
        
        # Compare
        if sim_account and paper_account:
            sim_cash = sim_account.get('cash')
            paper_cash = paper_account.get('cash')
            
            if sim_cash == paper_cash:
                print(f"⚠️ Cash amounts identical ({sim_cash}). Isolation unverified (or fallback occurred).")
            else:
                print("✅ Cash amounts differ. Isolation confirmed.")
            
            print(f"SIM ID/Status: {sim_account.get('status')}")
            print(f"PAPER ID/Status: {paper_account.get('status')}")
            
    else:
        print("⚠️ Could not fetch Paper account (Keys missing/invalid). This is expected if you haven't set keys.")
        print("   If keys are missing, the system falls back to SimAdapter, usually cleanly.")

    # 3. Switch back to SIM
    set_mode("sim")
    sim_account_2 = get_account()
    if sim_account_2 and sim_account:
         if sim_account_2.get('cash') == sim_account.get('cash'):
             print("✅ Simulation state preserved.")
         else:
             print("❌ Simulation state NOT preserved.")

if __name__ == "__main__":
    run_test()
