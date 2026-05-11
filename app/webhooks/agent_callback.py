from fastapi import APIRouter, Request
from app.storage.tables import insert_event

router = APIRouter(prefix="/webhooks/agent", tags=["webhooks-agent"])

@router.post("/{agent_id}")
async def agent_callback(agent_id: str, request: Request):
    data = await request.json(); typ = data.get("event_type") or "agent_session_completed"
    await insert_event(typ, data.get("contact_id"), data.get("step_id"), {"agent_id": agent_id, **data})
    return {"ok": True}
