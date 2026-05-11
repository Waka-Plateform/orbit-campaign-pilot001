from fastapi import APIRouter, Request
from app.storage.tables import insert_event

router = APIRouter(prefix="/webhooks/sms", tags=["webhooks-sms"])

@router.post("/event")
async def sms_event(request: Request):
    payload = await request.json(); items = payload if isinstance(payload, list) else [payload]
    for e in items:
        data = e.get("data", e); direction = data.get("direction", "").lower(); status = (data.get("deliveryStatus") or data.get("status") or "").lower()
        typ = "sms_in" if direction == "incoming" else "sms_delivered" if "deliver" in status else "sms_failed" if "fail" in status else "sms_event"
        await insert_event(typ, data.get("from") or data.get("to"), data.get("step_id") or "B", data)
    return {"ok": True, "count": len(items)}
