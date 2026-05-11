from fastapi import APIRouter
from app.integrations import compeak
from app.storage.cosmos import set_channel_config

router = APIRouter(prefix='/api/channels/voice', tags=['channels-voice'])

@router.get('/compeak/accounts')
async def accounts():
    return {'items': await compeak.list_accounts()}

@router.get('/compeak/{account}/numbers')
async def numbers(account: str):
    return {'items': await compeak.list_numbers(account)}

@router.get('/compeak/{account}/trunks')
async def trunks(account: str):
    return {'items': await compeak.list_trunks(account)}

@router.post('/compeak/numbers/purchase')
async def purchase_number(payload: dict):
    from app.config import get_secret
    import httpx
    base = await get_secret('compeak-api-base-url')
    token = await get_secret(payload.get('voice_kv_credentials_ref', 'compeak-api-token'))
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(f'{base.rstrip("/")}/numbers/purchase', headers={'Authorization': f'Bearer {token}'}, json=payload)
        res.raise_for_status()
        return {'ok': True, 'result': res.json()}

@router.post('/compeak/trunk/provision')
async def provision_trunk(payload: dict):
    from app.config import get_secret
    import httpx
    base = await get_secret('compeak-api-base-url')
    token = await get_secret(payload.get('voice_kv_credentials_ref', 'compeak-api-token'))
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(f'{base.rstrip("/")}/trunks', headers={'Authorization': f'Bearer {token}'}, json=payload)
        res.raise_for_status()
        return {'ok': True, 'result': res.json()}

@router.post('/select')
async def select(payload: dict):
    required = ['voice_provider','voice_compeak_account_id','voice_inbound_number','voice_trunk_id','voice_kv_credentials_ref']
    missing = [k for k in required if not payload.get(k)]
    if missing:
        return {'ok': False, 'missing': missing}
    await set_channel_config('voice', payload)
    return {'ok': True, 'config': payload}
