from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import alpaca_trade_api as tradeapi
from database.models import User
from .auth import get_current_user

router = APIRouter(prefix="/trade", tags=["trade"])

# Access API client from main scope or re-init
# Using Re-init pattern for module independence
from config import api

from services.psych_risk_service import PsychRiskScoreService
from services.strategy_dna_service import StrategyDNAService

class OrderRequest(BaseModel):
    symbol: str
    qty: float
    side: str # 'buy' or 'sell'
    type: str # 'market' or 'limit'
    time_in_force: str = 'day'
    limit_price: Optional[float] = None
    override_risk: bool = False
    override_strategy: bool = False

@router.post("/order")
def submit_order(order: OrderRequest):
    """
    Submit an order to Alpaca Paper Trading.
    Includes Emotional Risk Firewall and Strategy DNA Pre-check.
    """
    try:
        # Validate side
        if order.side.lower() not in ['buy', 'sell']:
            raise HTTPException(status_code=400, detail="Invalid side. Must be 'buy' or 'sell'")

        # ----------------------------------------------------------------
        # 1. EMOTIONAL RISK FIREWALL
        # ----------------------------------------------------------------
        # Check if user is in a critical mental state (e.g. tilted)
        # We use a fresh service instance here
        risk_service = PsychRiskScoreService()
        try:
            # Calculate current risk score (fast check)
            risk_data = risk_service.calculate_prs(DEMO_USER_ID, lookback_days=30)
            
            if risk_data['risk_state'] == 'critical' and notorder.override_risk:
                # BLOCK THE TRADE
                raise HTTPException(
                    status_code=403, 
                    detail={
                        "code": "RISK_FIREWALL_BLOCK",
                        "message": "High Psychological Risk detected (Score: 85+). Trading blocked to prevent tilt.",
                        "risk_score": risk_data['score'],
                        "reason": "You are currently showing signs of severe emotional distress or tilt.",
                        "requires_override": True
                    }
                )
                        "message": f"Order blocked by Emotional Risk Firewall. Your Risk Score is {prs['score']} (Critical). Take a cooldown break.",
                        "risk_score": prs['score']
                    }
                )

        # 2. AI STRATEGY PRE-CHECK
        if not order.override_strategy:
            # Check Strategy Alignment
            compatibility = dna_service.check_order_compatibility(
                current_user.id, 
                order.symbol, 
                order.side, 
                order.type,
                order.qty
            )
            
        try:
            submitted_order = api.submit_order(**args)
        except ValueError as e:
            # Catch specific ValueErrors from the adapter (e.g., insufficient funds)
            raise HTTPException(status_code=400, detail=str(e))
        
        # Adapter returns dict, not object
        return submitted_order
    except HTTPException:
        raise
    except Exception as e:
        # API errors come as exceptions
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
def get_orders(status: str = 'open'):
    """
    Get list of orders (default: open).
    """
    try:
        orders = api.list_orders(status=status, limit=50, user_id=DEMO_USER_ID)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}/replay")
async def get_trade_replay(order_id: str, current_user: User = Depends(get_current_user)):
    """
    Get trade snapshot for replay.
    """
    try:
        snapshot = api.get_trade_snapshot(order_id)
        if not snapshot:
             raise HTTPException(status_code=404, detail="Snapshot not found")
        return snapshot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
