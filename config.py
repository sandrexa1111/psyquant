from services.alpaca_adapter import AlpacaAdapter
from services.local_sim_adapter import LocalSimAdapter
import os

# Configuration
from services.alpaca_adapter import AlpacaAdapter
from services.local_sim_adapter import LocalSimAdapter
from services.encryption import encryption
from database.database import SessionLocal
from database.models import User, AlpacaCredential
import os
import json


# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-for-dev-environment-only-change-in-prod")
JWT_ALGORITHM = "HS256"

USER_DATA_FILE = "user_data.json"

# DEMO user
DEMO_USER_ID = "00000000-0000-0000-0000-000000000000"

def get_trading_provider():
    # Read mode from JSON (until we move global app state to DB or per-user session)
    mode = "sim"
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                data = json.load(f)
                mode = data.get("mode", "sim")
        except:
            pass

    print(f"🔄 Initializing Trading Provider. Mode: {mode.upper()}")

    if mode == "sim":
        return LocalSimAdapter()
    
    # Paper/Live - Fetch keys from DB
    api_key = None
    secret_key = None
    base_url = "https://paper-api.alpaca.markets"
    
    try:
        db = SessionLocal()
        creds = db.query(AlpacaCredential).filter(AlpacaCredential.user_id == DEMO_USER_ID).first()
        if creds:
             api_key = encryption.decrypt(creds.api_key_id)
             secret_key = encryption.decrypt(creds.secret_key)
             if creds.account_type == "live":
                 base_url = "https://api.alpaca.markets"
        db.close()
    except Exception as e:
        print(f"⚠️ Error loading keys from DB: {e}")

    if api_key and secret_key:
        try:
            return AlpacaAdapter(api_key, secret_key, base_url)
        except Exception as e:
            print(f"❌ Failed to connect to Alpaca: {e}. Falling back to Sim.")
            return LocalSimAdapter()
    else:
        print("⚠️ No API Keys found in DB. Falling back to Sim.")
        return LocalSimAdapter()

class TradingProviderProxy:
    def __init__(self):
        self._provider = None
        self.reload()

    def reload(self):
        self._provider = get_trading_provider()
    
    def __getattr__(self, name):
        return getattr(self._provider, name)

api = TradingProviderProxy()
