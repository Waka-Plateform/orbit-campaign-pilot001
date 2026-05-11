from fastapi import APIRouter, Body
from azure.identity.aio import DefaultAzureCredential
from azure.mgmt.resource.resources.aio import ResourceManagementClient
from azure.mgmt.resource.subscriptions.aio import SubscriptionClient
from azure.mgmt.communication.aio import CommunicationServiceManagementClient
from app.storage.cosmos import set_channel_config

router = APIRouter(prefix="/api/channels/sms", tags=["channels-sms"])

@router.get("/subscriptions")
async def subscriptions():
    cred = DefaultAzureCredential(); client = SubscriptionClient(cred)
    try: return {"items": [s.as_dict() async for s in client.subscriptions.list()]}
    finally: await client.close(); await cred.close()

@router.get("/{sub}/resource-groups")
async def resource_groups(sub: str):
    cred = DefaultAzureCredential(); client = ResourceManagementClient(cred, sub)
    try: return {"items": [rg.as_dict() async for rg in client.resource_groups.list()]}
    finally: await client.close(); await cred.close()

@router.get("/{sub}/{rg}/communication-services")
async def communication_services(sub: str, rg: str):
    cred = DefaultAzureCredential(); client = CommunicationServiceManagementClient(cred, sub)
    try: return {"items": [x.as_dict() async for x in client.communication_services.list_by_resource_group(rg)]}
    finally: await client.close(); await cred.close()

@router.get("/{svc}/phone-numbers")
async def phone_numbers(svc: str, subscription_id: str, resource_group: str):
    cred = DefaultAzureCredential(); client = CommunicationServiceManagementClient(cred, subscription_id)
    try: return {"items": [x.as_dict() async for x in client.phone_numbers.list_by_communication_service(resource_group, svc)]}
    finally: await client.close(); await cred.close()

@router.post("/{svc}/phone-numbers/purchase")
async def purchase_phone_number(svc: str, body: dict = Body(...)):
    cred = DefaultAzureCredential(); client = CommunicationServiceManagementClient(cred, body["sms_subscription_id"])
    try:
        poller = await client.phone_numbers.begin_create_or_update(body["sms_resource_group"], svc, body["sms_phone_number"], {"location": "global"})
        return (await poller.result()).as_dict()
    finally: await client.close(); await cred.close()

@router.post("/select")
async def select(body: dict = Body(...)):
    await set_channel_config("sms", body); return {"ok": True, "config": body}
