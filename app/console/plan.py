from fastapi import APIRouter, Body
from app.storage.cosmos import get_campaign, set_schedule
from app.orchestrator.runner import tick

router = APIRouter(prefix="/api/console", tags=["console-plan"])

@router.get("/plan")
async def get_plan():
    return (await get_campaign()).get("schedule", {})

@router.post("/plan")
async def post_plan(schedule: dict = Body(...)):
    await set_schedule(schedule); return {"ok": True, "schedule": schedule}

@router.post("/plan/start")
async def start():
    c = await get_campaign(); s = c.get("schedule", {}); s["paused"] = False
    await set_schedule(s); return await tick()

@router.post("/plan/pause")
async def pause():
    c = await get_campaign(); s = c.get("schedule", {}); s["paused"] = True
    await set_schedule(s); return {"ok": True, "status": "paused"}

@router.post("/plan/resume")
async def resume():
    c = await get_campaign(); s = c.get("schedule", {}); s["paused"] = False
    await set_schedule(s); return {"ok": True, "status": "running"}

@router.post("/plan/stop")
async def stop():
    c = await get_campaign(); s = c.get("schedule", {}); s["paused"] = True; s["stopped"] = True
    await set_schedule(s); return {"ok": True, "status": "stopped"}
