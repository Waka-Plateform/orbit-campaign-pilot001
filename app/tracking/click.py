import base64
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.storage.tables import insert_event

router = APIRouter(tags=["tracking"])

@router.get("/track/click/{step_id}")
async def click_track(step_id: str, u: str, request: Request, contact_id: str | None = None):
    url = base64.urlsafe_b64decode(u.encode()).decode()
    await insert_event("email_click", contact_id, step_id, {"url": url, "ip": request.client.host if request.client else None, "user_agent": request.headers.get("user-agent")})
    return RedirectResponse(url, status_code=302)
