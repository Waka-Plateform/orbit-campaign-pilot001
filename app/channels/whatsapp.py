from fastapi import APIRouter
from azure.mgmt.subscription.aio import SubscriptionClient
from azure.mgmt.resource.resources.aio import ResourceManagementClient
from app.config import credential
from app.storage.cosmos import set_channel_config

router = APIRouter(prefix='/api/channels/whatsapp', tags=['channels-whatsapp'])

async def _resources(sub: str):
    return ResourceManagementClient(credential(), sub)

@router.get('/subscriptions')
async def subscriptions():
    client = SubscriptionClient(credential())
    try:
        return {'items': [{'subscription_id': s.subscription_id, 'display_name': s.display_name} async for s in client.subscriptions.list()]}
    finally:
        await client.close()

@router.get('/{sub}/resource-groups')
async def resource_groups(sub: str):
    client = await _resources(sub)
    try:
        return {'items': [{'name': rg.name, 'location': rg.location, 'id': rg.id} async for rg in client.resource_groups.list()]}
    finally:
        await client.close()

@router.get('/{sub}/{rg}/messages-services')
async def messages_services(sub: str, rg: str):
    client = await _resources(sub)
    try:
        return {'items': [{'id': r.id, 'name': r.name, 'location': r.location, 'type': r.type} async for r in client.resources.list_by_resource_group(rg, filter="resourceType eq 'Microsoft.Communication/messagesServices'")]}
    finally:
        await client.close()

@router.get('/{svc}/channels')
async def channels(svc: str, sub: str, rg: str):
    client = await _resources(sub)
    try:
        items = []
        async for r in client.resources.list_by_resource_group(rg, filter="resourceType eq 'Microsoft.Communication/messagesServices/channels'"):
            if f'/messagesServices/{svc}/' in r.id:
                items.append({'id': r.id, 'name': r.name, 'properties': getattr(r, 'properties', {})})
        return {'items': items}
    finally:
        await client.close()

@router.post('/{svc}/channels/register')
async def register_channel(svc: str, payload: dict):
    sub, rg, channel_id = payload['whatsapp_subscription_id'], payload['whatsapp_resource_group'], payload['whatsapp_channel_id']
    client = await _resources(sub)
    try:
        params = {'location': 'global', 'properties': payload.get('properties', {})}
        poller = await client.resources.begin_create_or_update(rg, 'Microsoft.Communication', '', 'messagesServices/channels', f'{svc}/{channel_id}', '2023-04-01', params)
        res = await poller.result()
        return {'ok': True, 'id': res.id, 'name': res.name}
    finally:
        await client.close()

@router.post('/select')
async def select(payload: dict):
    required = ['whatsapp_subscription_id','whatsapp_resource_group','whatsapp_messages_service_id','whatsapp_channel_id']
    missing = [k for k in required if not payload.get(k)]
    if missing:
        return {'ok': False, 'missing': missing}
    await set_channel_config('whatsapp', payload)
    return {'ok': True, 'config': payload}
