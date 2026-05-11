import httpx
from app.config import get_secret


async def send_whatsapp(channel_config: dict, to_phone: str, body: str) -> dict:
    endpoint = channel_config.get('whatsapp_messages_service_endpoint')
    if not endpoint:
        raise RuntimeError('whatsapp channel is not configured')
    token = await get_secret('acs-whatsapp-token')
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            f"{endpoint.rstrip('/')}/messages:send",
            headers={'Authorization': f'Bearer {token}'},
            json={'channelId': channel_config['whatsapp_channel_id'], 'to': to_phone, 'content': body},
        )
        res.raise_for_status()
        data = res.json()
        return {'provider_message_id': data.get('id'), 'raw': data}
