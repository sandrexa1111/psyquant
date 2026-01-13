"""
Pattern Alerts API Router
Provides endpoints for behavioral pattern detection and alert management.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.behavior_alerts_service import BehaviorAlertsService

router = APIRouter(prefix="/alerts", tags=["behavioral-alerts"])

# Demo user ID (in production, use auth)
DEMO_USER_ID = "00000000-0000-0000-0000-000000000000"


# ============================================================================
# Request/Response Models
# ============================================================================

class AcknowledgeRequest(BaseModel):
    feedback: Optional[str] = None  # 'helpful', 'not_helpful', 'false_alarm'


class PreTradeCheckRequest(BaseModel):
    symbol: Optional[str] = None
    side: Optional[str] = None
    qty: Optional[float] = None
    rsi: Optional[float] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/patterns")
async def get_behavior_patterns():
    """
    Get all detected behavioral patterns for the user.
    These are personalized patterns like 'You overtrade after 2 losses'.
    """
    service = BehaviorAlertsService()
    try:
        patterns = service.get_user_patterns(DEMO_USER_ID)
        return {
            'patterns': patterns,
            'total': len(patterns),
            'message': f"Found {len(patterns)} behavioral patterns" if patterns else "No patterns detected yet. Keep trading to discover your patterns."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.post("/patterns/detect")
async def detect_patterns():
    """
    Run pattern detection algorithms on user's trade history.
    This analyzes all trades and discovers behavioral patterns.
    """
    service = BehaviorAlertsService()
    try:
        detected = service.detect_all_patterns(DEMO_USER_ID)
        return {
            'detected': detected,
            'patterns_found': len(detected),
            'message': f"Detected {len(detected)} new/updated patterns" if detected else "No patterns detected. More trading data needed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/active")
async def get_active_alerts():
    """
    Get all unacknowledged alerts for the user.
    These are warnings that the user hasn't dismissed yet.
    """
    service = BehaviorAlertsService()
    try:
        alerts = service.get_active_alerts(DEMO_USER_ID)
        return {
            'alerts': alerts,
            'total': len(alerts),
            'has_critical': any(a['severity'] == 'critical' for a in alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.post("/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str, request: AcknowledgeRequest = None):
    """
    Mark an alert as acknowledged/dismissed.
    Optionally provide feedback on whether the alert was helpful.
    """
    service = BehaviorAlertsService()
    try:
        feedback = request.feedback if request else None
        success = service.acknowledge_alert(alert_id, feedback)
        if success:
            return {"status": "acknowledged", "alert_id": alert_id}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.post("/pre-trade-check")
async def pre_trade_check(request: PreTradeCheckRequest):
    """
    Check if current trading conditions match any known negative patterns.
    Call this before executing a trade to get warnings.
    
    Returns warnings like:
    - "Warning: You tend to overtrade after losses. You've had 2 losses recently."
    - "Warning: Your worst trades happen when RSI is between 40-50. Current RSI: 45"
    """
    service = BehaviorAlertsService()
    try:
        context = {
            'symbol': request.symbol,
            'side': request.side,
            'qty': request.qty,
            'rsi': request.rsi,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        result = service.check_pre_trade_warning(DEMO_USER_ID, context)
        
        if result and result.get('has_warning'):
            return {
                'proceed_with_caution': True,
                'warnings': result['warnings'],
                'highest_severity': result.get('highest_severity', 'warning'),
                'recommendation': "Consider reviewing these patterns before proceeding."
            }
        else:
            return {
                'proceed_with_caution': False,
                'warnings': [],
                'message': "No pattern warnings for current conditions."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/summary")
async def get_alerts_summary():
    """
    Get a summary of patterns and alerts for dashboard display.
    """
    service = BehaviorAlertsService()
    try:
        patterns = service.get_user_patterns(DEMO_USER_ID)
        alerts = service.get_active_alerts(DEMO_USER_ID)
        
        # Count by severity
        severity_counts = {'info': 0, 'warning': 0, 'critical': 0}
        for p in patterns:
            sev = p.get('severity', 'info')
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        return {
            'total_patterns': len(patterns),
            'active_alerts': len(alerts),
            'severity_breakdown': severity_counts,
            'top_patterns': patterns[:3],
            'needs_attention': len(alerts) > 0 or severity_counts['critical'] > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()
