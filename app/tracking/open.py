import base64
from fastapi import APIRouter, Request, Response
from app.storage.tables import insert_event

router = APIRouter(tags=["tracking"])
GIF = base64.b64decode("R0lGODlhAQABAPAAAP///wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==")

@router.get("/track/open/{step_id}")
async def open_track(step_id: str, request: Request, contact_id: str | None = None):
    await insert_event("email_open", contact_id, step_id, {"ip": request.client.host if request.client else None, "user_agent": request.headers.get("user-agent")})
    return Response(GIF, media_type="image/gif")
