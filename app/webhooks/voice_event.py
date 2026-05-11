from fastapi import APIRouter, Request
from app.storage.tables import log_event

router = APIRouter(prefix='/webhooks/voice', tags=['webhooks-voice'])

@router.post('/event')
async def voice_event(request: Request):
    data = await request.json()
    event_type = 'voice_transcript' if data.get('transcript') else 'voice_call_completed'
    await log_event(event_type, contact_id=data.get('contact_id') or data.get('to'), step_id=data.get('step_id'), call_id=data.get('call_id'), payload=data)
    return {'ok': True}
