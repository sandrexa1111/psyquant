"""
Journal API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.journal_service import JournalService

router = APIRouter(prefix="/journal", tags=["journal"])

# Demo user ID (in production, use auth)
DEMO_USER_ID = "00000000-0000-0000-0000-000000000000"

# --- Pydantic Models ---

class JournalEntryCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    trade_id: Optional[str] = None

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class JournalEntryResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    tags: Optional[List[str]] = []
    sentiment_score: Optional[float] = None
    ai_feedback: Optional[str] = None
    trade_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# --- Endpoints ---

@router.post("/", response_model=JournalEntryResponse)
async def create_entry(entry: JournalEntryCreate):
    service = JournalService()
    try:
        result = service.create_entry(
            user_id=DEMO_USER_ID,
            title=entry.title,
            content=entry.content,
            tags=entry.tags,
            trade_id=entry.trade_id
        )
        return JournalEntryResponse(**result)
    finally:
        service.close()

@router.get("/", response_model=List[JournalEntryResponse])
async def list_entries(limit: int = 50, offset: int = 0):
    service = JournalService()
    try:
        results = service.get_user_entries(DEMO_USER_ID, limit, offset)
        return [JournalEntryResponse(**r) for r in results]
    finally:
        service.close()

@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_entry(entry_id: str):
    service = JournalService()
    try:
        result = service.get_entry(entry_id)
        if not result:
            raise HTTPException(status_code=404, detail="Entry not found")
        return JournalEntryResponse(**result)
    finally:
        service.close()

@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_entry(entry_id: str, update: JournalEntryUpdate):
    service = JournalService()
    try:
        result = service.update_entry(
            entry_id=entry_id,
            title=update.title,
            content=update.content,
            tags=update.tags
        )
        if not result:
            raise HTTPException(status_code=404, detail="Entry not found")
        return JournalEntryResponse(**result)
    finally:
        service.close()

@router.delete("/{entry_id}")
async def delete_entry(entry_id: str):
    service = JournalService()
    try:
        success = service.delete_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entry not found")
        return {"status": "success", "message": "Entry deleted"}
    finally:
        service.close()

@router.post("/{entry_id}/analyze", response_model=JournalEntryResponse)
async def analyze_entry(entry_id: str):
    service = JournalService()
    try:
        result = service.analyze_entry(entry_id)
        return JournalEntryResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()
