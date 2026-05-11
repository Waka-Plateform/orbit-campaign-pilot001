from fastapi import APIRouter, Request
from app.storage.tables import insert_event

router = APIRouter(prefix="/webhooks/email", tags=["webhooks-email"])

@router.post("/delivery")
async def email_delivery(request: Request):
    payload = await request.json(); items = payload if isinstance(payload, list) else [payload]
    for e in items:
        data = e.get("data", e); status = (data.get("deliveryStatus") or data.get("status") or "").lower()
        event_type = "email_delivered" if "deliver" in status else "email_bounced" if "bounce" in status else "email_failed" if "fail" in status else "email_event"
        await insert_event(event_type, data.get("recipient") or data.get("to"), data.get("step_id") or "A", data)
    return {"ok": True, "count": len(items)}
