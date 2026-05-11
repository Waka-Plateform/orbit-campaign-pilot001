from fastapi import APIRouter, Body
from app.integrations.graph_mailbox import list_messages
from app.storage.tables import list_events, insert_event

router = APIRouter(prefix="/api/console/inbox", tags=["console-inbox"])

@router.get("/email")
async def inbox_email():
    return {"items": await list_messages()}

@router.get("/{channel}")
async def inbox_channel(channel: str):
    return {"items": await list_events(limit=200, event_type=f"{channel}_in")}

@router.post("/{msg_id}/reply")
async def reply(msg_id: str, body: dict = Body(...)):
    await insert_event("inbox_reply_requested", body.get("contact_id"), None, {"msg_id": msg_id, "body": body})
    return {"ok": True, "msg_id": msg_id}
