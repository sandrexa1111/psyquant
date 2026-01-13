from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from database.database import get_db
from sqlalchemy.orm import Session
from database.models import User
import jwt
import config

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode JWT with Verification
        # Using config.JWT_SECRET which defaults to a dev key if env not set
        # In PROD, JWT_SECRET must be set in Environment
        payload = jwt.decode(
            token, 
            config.JWT_SECRET, 
            algorithms=[config.JWT_ALGORITHM], 
            options={"verify_signature": True}
        )
        
        user_id: str = payload.get("sub")
        # print(f"DEBUG: Decoded user_id: {user_id}")
        
        if user_id is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError as e:
        print(f"DEBUG: JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"DEBUG: Unexpected Auth Error: {e}")
        raise
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"DEBUG: Creating new user {user_id}")
        # Setup temporary auto-create for dev if missing?
        # Or just raise error. For MVP safety let's just return a basic user shell if not in DB?
        # No, better to error or create.
        # Let's create if not exists for smooth onboarding
        user = User(id=user_id, email=payload.get("email", "unknown"), full_name=payload.get("user_metadata", {}).get("full_name", "Unknown"))
        db.add(user)
        db.commit()
    else:
        print(f"DEBUG: Found existing user {user_id}")
        
    return user



class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    # TODO: Implement registration logic
    return {"message": "Register endpoint"}

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # TODO: Implement login logic (JWT)
    return {"token": "fake-jwt-token"}

@router.post("/refresh")
async def refresh_token():
    return {"message": "Refresh endpoint"}

@router.post("/logout")
async def logout():
    return {"message": "Logout endpoint"}
