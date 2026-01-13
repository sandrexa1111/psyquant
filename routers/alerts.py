from fastapi import APIRouter, HTTPException, Depends
from database.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_alerts(db: Session = Depends(get_db)):
    return []

@router.post("/")
async def create_alert(db: Session = Depends(get_db)):
    return {"message": "Alert created"}

@router.patch("/{id}")
async def update_alert(id: str, db: Session = Depends(get_db)):
    return {"message": "Alert updated"}

@router.delete("/{id}")
async def delete_alert(id: str, db: Session = Depends(get_db)):
    return {"message": "Alert deleted"}
