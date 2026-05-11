import asyncio, json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.storage.tables import list_events

router = APIRouter(tags=["sse"])

@router.get("/events")
async def events():
    async def gen():
        seen = set()
        while True:
            for e in await list_events(limit=50):
                rk = e.get("RowKey")
                if rk not in seen:
                    seen.add(rk)
                    yield {"event": "kpi.updated", "data": json.dumps(e, default=str)}
            await asyncio.sleep(5)
    return EventSourceResponse(gen())
