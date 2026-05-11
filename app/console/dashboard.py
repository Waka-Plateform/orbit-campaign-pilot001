from fastapi import APIRouter
from app.storage.tables import list_events

router = APIRouter(prefix="/api/console", tags=["console-dashboard"])

@router.get("/dashboard")
async def dashboard(metric: str | None = None, period: str | None = None):
    events = await list_events(limit=1000)
    total_sent = len([e for e in events if e.get("event_type") == "email_sent"])
    delivered = len([e for e in events if e.get("event_type") == "email_delivered"])
    bounced = len([e for e in events if e.get("event_type") in ("email_bounced", "email_failed")])
    delivery_rate = delivered / total_sent if total_sent else 0
    return {"metric": metric or "email_delivery_rate", "period": period, "email_sent": total_sent, "email_delivered": delivered, "email_bounced": bounced, "delivery_rate": delivery_rate, "target": 0.90}
