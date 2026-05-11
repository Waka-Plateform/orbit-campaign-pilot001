from fastapi import APIRouter
from app.storage.cosmos import get_campaign

router = APIRouter(prefix='/api/console', tags=['console-channels'])

@router.get('/channels')
async def channels():
    campaign = await get_campaign()
    return campaign.get('channels', {})
