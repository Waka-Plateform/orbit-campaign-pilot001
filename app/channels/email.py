from fastapi import APIRouter, Body
from azure.identity.aio import DefaultAzureCredential
from azure.mgmt.resource.resources.aio import ResourceManagementClient
from azure.mgmt.resource.subscriptions.aio import SubscriptionClient
from azure.mgmt.communication.aio import CommunicationServiceManagementClient
from azure.mgmt.communication.models import EmailServiceResource, SenderUsernameResource
from app.storage.cosmos import set_channel_config

router = APIRouter(prefix="/api/channels/email", tags=["channels-email"])

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

@router.get("/{sub}/{rg}/email-services")
async def email_services(sub: str, rg: str):
    cred = DefaultAzureCredential(); client = CommunicationServiceManagementClient(cred, sub)
    try: return {"items": [x.as_dict() async for x in client.email_services.list_by_resource_group(rg)]}
    finally: await client.close(); await cred.close()

@router.get("/{svc}/domains")
async def domains(svc: str, subscription_id: str, resource_group: str):
    cred = DefaultAzureCredential(); client = CommunicationServiceManagementClient(cred, subscription_id)
    try: return {"items": [x.as_dict() async for x in client.domains.list_by_email_service_resource(resource_group, svc)]}
    finally: await client.close(); await cred.close()

@router.get("/{svc}/{domain}/senders")
async def senders(svc: str, domain: str, subscription_id: str, resource_group: str):
    cred = DefaultAzureCredential(); client = CommunicationServiceManagementClient(cred, subscription_id)
    try: return {"items": [x.as_dict() async for x in client.sender_usernames.list_by_domains(resource_group, svc, domain)]}
    finally: await client.close(); await cred.close()

@router.post("/select")
async def select(body: dict = Body(...)):
    await set_channel_config("email", body); return {"ok": True, "config": body}

@router.post("/{svc}/domains/create")
async def create_domain(svc: str, body: dict = Body(...)):
    cred = DefaultAzureCredential(); client = CommunicationServiceManagementClient(cred, body["email_subscription_id"])
    try:
        poller = await client.domains.begin_create_or_update(body["email_resource_group"], svc, body["email_domain"], EmailServiceResource(location="global"))
        return (await poller.result()).as_dict()
    finally: await client.close(); await cred.close()

@router.post("/{svc}/{domain}/senders/create")
async def create_sender(svc: str, domain: str, body: dict = Body(...)):
    cred = DefaultAzureCredential(); client = CommunicationServiceManagementClient(cred, body["email_subscription_id"])
    try:
        res = await client.sender_usernames.create_or_update(body["email_resource_group"], svc, domain, body["email_sender_username"], SenderUsernameResource(display_name=body.get("email_display_name")))
        return res.as_dict()
    finally: await client.close(); await cred.close()
