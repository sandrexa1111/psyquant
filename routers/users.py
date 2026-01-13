from fastapi import APIRouter, HTTPException, Depends
from database.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me")
async def read_users_me(db: Session = Depends(get_db)):
    # TODO: Return current user profile
    return {"username": "currentuser"}

@router.patch("/me/profile")
async def update_user_profile(db: Session = Depends(get_db)):
    return {"message": "Update profile"}

@router.get("/me/subscription")
async def get_subscription(db: Session = Depends(get_db)):
    return {"tier": "free"}
