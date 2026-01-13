from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random
from datetime import datetime

router = APIRouter(prefix="/ai", tags=["ai"])

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    text: str
    embedded_data: Optional[Dict[str, Any]] = None
    suggested_actions: List[str] = []

@router.get("/skills")
def get_skills():
    """Get user trading skill breakdown"""
    # Mock data
    return {
        "overall": 72,
        "profitability": 65,
        "risk_management": 80,
        "timing": 45,
        "discipline": 85,
        "history": [
            {"date": "2023-10-01", "score": 60},
            {"date": "2023-11-01", "score": 65},
            {"date": "2023-12-01", "score": 72},
        ]
    }

@router.get("/biases")
def get_biases():
    """Get detected psychological biases"""
    # Mock data
    return [
        {
            "id": "1",
            "type": "FOMO",
            "severity": 75,
            "description": "Entering trades after a significant move.",
            "detected_count": 5,
            "impact": "High"
        },
        {
            "id": "2",
            "type": "Revenge Trading",
            "severity": 30,
            "description": "Trading immediately after a loss to recover.",
            "detected_count": 2,
            "impact": "Medium"
        }
    ]

# Keep chat endpoint as well
@router.post("/chat", response_model=ChatResponse)
def chat_with_coach(request: ChatRequest):
    """
    Mock AI Coach Chat Endpoint.
    """
    msg = request.message.lower()
    
    # Simple keyword-based mock logic
    if "why" in msg and "lose" in msg:
        return ChatResponse(
            text="I noticed you entered AAPL right after a 5% spike. This matches your 'FOMO' pattern which has a 30% win rate. Next time, wait for a pullback.",
            embedded_data={
                "type": "trade_card",
                "trade_id": "mock-trade-id",
                "symbol": "AAPL",
                "pnl": -23.50
            },
            suggested_actions=["View Trade Replay", "Create FOMO Alert"]
        )
    
    elif "weakness" in msg:
        return ChatResponse(
            text="Your biggest weakness is **Timing**. You tend to enter trades too late, missing the initial move. 34% of your trades are 'chasing' entries.",
            embedded_data={
                "type": "chart",
                "title": "Entry Timing Distribution",
                "data": [
                    {"name": "Too Early", "value": 34},
                    {"name": "Optimal", "value": 43},
                    {"name": "Too Late", "value": 23}
                ]
            },
            suggested_actions=["Practice Entries", "Set Rules"]
        )
        
    elif "hello" in msg or "hi" in msg:
        return ChatResponse(
            text="Hello! I'm your AI Trading Coach. I'm here to help you analyze your trades and improve your psychology. What's on your mind?",
            suggested_actions=["Why did I lose today?", "Analyze my last trade", "Show my weaknesses"]
        )

    else:
        return ChatResponse(
            text="That's an interesting question. I'm still analyzing your recent data. Could you try asking about a specific trade or pattern?",
            suggested_actions=["Analyze recent trades", "Show patterns"]
        )
