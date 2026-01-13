
import jwt
import config
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

# Minimal Script to verify JWT Fix only

def verify_jwt_fix():
    print("Verifying JWT Fix...")
    client = TestClient(app)
    
    # 1. Valid Token
    token = jwt.encode({"sub": "test-user"}, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    
    # We need to mock get_current_user internals or let it run.
    # Actually, we want to test that the router accepts this token.
    # But get_current_user also checks DB. So let's mock DB or just check if it passes decode.
    
    # We can test the auth dependency directly logic if we want, or via endpoint.
    # Let's hit a protected endpoint.
    
    # Mock DB query in auth to return a fake user so we don't need real DB
    with patch("routers.auth.get_db") as mock_db_dep:
         # This is hard to patch dependency inject, easier to patch SessionLocal in auth or just let it fail at DB step?
         # If it fails at DB step, it passed JWT step!
         # If it fails 401, it failed JWT step.
         
         # Let's try simple endpoint.
         try:
             resp = client.get("/ai/skill-score", headers={"Authorization": f"Bearer {token}"})
             # If 500 or anything other than 401, it likely passed JWT decode.
             # Ideally we want 200, so we need to mock DB.
             # But let's check negative case first.
         except:
             pass

    # Negative Test: Token signed with WRONG secret
    files_token = jwt.encode({"sub": "hacker"}, "wrong-secret", algorithm=config.JWT_ALGORITHM)
    resp = client.get("/ai/skill-score", headers={"Authorization": f"Bearer {files_token}"})
    
    if resp.status_code == 401:
        print("✅ SUCCESS: Token with wrong signature rejected (401).")
    else:
        print(f"❌ FAIL: Token with wrong signature accepted? Code: {resp.status_code}")

if __name__ == "__main__":
    verify_jwt_fix()
