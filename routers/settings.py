from fastapi import APIRouter, HTTPException, Depends
import os
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, AlpacaCredential, UserProfile
from services.encryption import encryption
from typing import Optional

router = APIRouter(prefix="/settings", tags=["settings"])

# For MVP/Demo, we use a single fixed user ID since we don't have full Auth middleware enforcing user context yet
DEMO_USER_ID = "00000000-0000-0000-0000-000000000000"

class ApiKeys(BaseModel):
    key_id: str
    secret_key: str
    mode: str = "paper" # 'paper' or 'live'

class SimResetRequest(BaseModel):
    balance: float = 100000.0

class SettingsResponse(BaseModel):
    status: str
    mode: str
    alpaca_connected: bool

def _get_or_create_user(db: Session):
    user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    if not user:
        # Create default demo user
        user = User(
            id=DEMO_USER_ID, 
            email="demo@quant.local", 
            hashed_password="hashed_demo_password",
            full_name="Demo Trader"
        )
        db.add(user)
        # Create profile
        profile = UserProfile(user_id=DEMO_USER_ID, experience_level="intermediate")
        db.add(profile)
        db.commit()
        db.refresh(user)
    return user

@router.post("/keys")
def save_keys(keys: ApiKeys, db: Session = Depends(get_db)):
    """
    Encrypt and save Alpaca API keys to Database.
    """
    try:
        user = _get_or_create_user(db)
        
        # Encrypt params
        encrypted_key = encryption.encrypt(keys.key_id)
        encrypted_secret = encryption.encrypt(keys.secret_key)
        
        # Check if creds exist
        creds = db.query(AlpacaCredential).filter(AlpacaCredential.user_id == user.id).first()
        if not creds:
            creds = AlpacaCredential(
                user_id=user.id,
                api_key_id=encrypted_key,
                secret_key=encrypted_secret,
                account_type="paper"
            )
            db.add(creds)
        else:
            creds.api_key_id = encrypted_key
            creds.secret_key = encrypted_secret
        
        # We assume creating keys implies switching to that mode? 
        # The frontend sends mode='paper' usually.
        # But we don't store "current mode" in User (based on schema)
        # Ah, we rely on implicit or maybe we should store generic prefs.
        # The schema doesn't have "current_mode" on User, but Onboarding implies it.
        # Let's assume we use local config or just return success.
        
        db.commit()
        
        # Hot Reload Provider (This still relies on config Loading Logic, which needs update too)
        from config import api
        api.reload()
        
        return {"status": "success", "message": "Keys encrypted and saved."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mode/{mode}")
def set_mode(mode: str, db: Session = Depends(get_db)):
    """
    Switch trading mode (sim or paper).
    For now, this persists to a local config file OR DB preference if we add it.
    Since schema is strict, we might assume mode is client-side or we add a preference table.
    For MVP simplicity, we'll keep the JSON file for *app configuration* (like active mode)
    but user data is in DB.
    """
    if mode not in ["sim", "paper", "live"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    # We still modify user_data.json for simple "global app state" regarding mode
    # Ideally this would be in the DB per user, but `config.py` is global.
    import json
    USER_DATA_FILE = "user_data.json"
    
    try:
        data = {}
        if os.path.exists(USER_DATA_FILE):
             with open(USER_DATA_FILE, 'r') as f:
                data = json.load(f)
        
        data["mode"] = mode
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
        from config import api
        api.reload()
        
        return {"status": "success", "mode": mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sim/reset")
def reset_sim(request: SimResetRequest, db: Session = Depends(get_db)):
    """
    Reset Simulation Account.
    """
    from config import api
    # TODO: Get real user from Auth. For now, rely on default or get form token if available.
    # Since we are in MVP, let's use the DEMO_USER_ID defined in this file if no Auth context.
    # But ideally we use Depends(get_current_user).
    
    # Try to call reset_account
    if hasattr(api, 'reset_account'):
        api.reset_account(request.balance, user_id=DEMO_USER_ID)
        return {"status": "success", "message": f"Simulation reset to ${request.balance:,.2f}"}
    else:
        raise HTTPException(status_code=400, detail="Current mode is not Simulation. Cannot reset.")

@router.get("/status", response_model=SettingsResponse)
def get_status(db: Session = Depends(get_db)):
    # Check DB for creds
    user = _get_or_create_user(db)
    creds = db.query(AlpacaCredential).filter(AlpacaCredential.user_id == user.id).first()
    
    # Check JSON for mode
    import json, os
    mode = "sim"
    if os.path.exists("user_data.json"):
        try:
            with open("user_data.json", 'r') as f:
                data = json.load(f)
                mode = data.get("mode", "sim")
        except:
            pass

    return {
        "status": "online",
        "mode": mode,
        "alpaca_connected": creds is not None
    }
