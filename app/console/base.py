from fastapi import APIRouter, Query
from app.storage.tables import list_prospects

router = APIRouter(prefix="/api/console", tags=["console-base"])

@router.get("/base")
async def base(page: int = 1, audience: str | None = None, q: str | None = None):
    rows = await list_prospects(limit=100, q=q)
    return {"page": page, "audience": audience, "items": rows, "count": len(rows)}
