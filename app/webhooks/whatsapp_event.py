from fastapi import APIRouter, Request
from app.storage.tables import log_event

router = APIRouter(prefix='/webhooks/whatsapp', tags=['webhooks-whatsapp'])

@router.post('/event')
async def whatsapp_event(request: Request):
    payload = await request.json()
    events = payload if isinstance(payload, list) else [payload]
    for item in events:
        data = item.get('data', item)
        direction = data.get('direction', '')
        status = str(data.get('status') or '').lower()
        event_type = 'whatsapp_in' if direction.lower() == 'incoming' else 'whatsapp_delivered' if 'delivered' in status else 'whatsapp_event'
        await log_event(event_type, contact_id=data.get('from') or data.get('to'), step_id=data.get('step_id'), provider_message_id=data.get('messageId'), payload=data)
    return {'ok': True}
