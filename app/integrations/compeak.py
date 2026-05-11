import httpx
from app.config import get_secret


async def _headers(credentials_ref: str) -> dict:
    token = await get_secret(credentials_ref)
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


async def list_accounts() -> list[dict]:
    base = await get_secret('compeak-api-base-url')
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(f'{base.rstrip("/")}/accounts', headers=await _headers('compeak-api-token'))
        res.raise_for_status()
        return res.json().get('items', res.json())


async def list_numbers(account_id: str) -> list[dict]:
    base = await get_secret('compeak-api-base-url')
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(f'{base.rstrip("/")}/accounts/{account_id}/numbers', headers=await _headers('compeak-api-token'))
        res.raise_for_status()
        return res.json().get('items', res.json())


async def list_trunks(account_id: str) -> list[dict]:
    base = await get_secret('compeak-api-base-url')
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(f'{base.rstrip("/")}/accounts/{account_id}/trunks', headers=await _headers('compeak-api-token'))
        res.raise_for_status()
        return res.json().get('items', res.json())


async def create_call(channel_config: dict, to_phone: str, agent_id: str, script: dict) -> dict:
    base = await get_secret('compeak-api-base-url')
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            f'{base.rstrip("/")}/calls',
            headers=await _headers(channel_config['voice_kv_credentials_ref']),
            json={'accountId': channel_config['voice_compeak_account_id'], 'trunkId': channel_config['voice_trunk_id'], 'from': channel_config['voice_inbound_number'], 'to': to_phone, 'agentId': agent_id, 'script': script},
        )
        res.raise_for_status()
        return res.json()
