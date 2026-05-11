from fastapi import APIRouter
from app.storage.cosmos import get_campaign

router = APIRouter(prefix="/api/console", tags=["console-main"])

@router.get("/main")
async def main():
    c = await get_campaign()
    return {"campaign_id": c.get("campaign_id"), "name": c.get("name"), "status": c.get("status"), "objective": c.get("scope_brief", {}).get("objective"), "flow_svg_url": f"/api/launch/campaigns/{c.get('campaign_id')}/flow.svg", "channels": c.get("channels", {})}
