from fastapi import APIRouter, Body
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential
from app.config import get_settings
from app.storage.cosmos import set_channel_config

router = APIRouter(prefix="/api/channels", tags=["channels-agents"])

async def _list(agent_type: str):
    s = get_settings()
    if not s.conversations_cosmos_endpoint:
        raise RuntimeError("CONVERSATIONS_COSMOS_ENDPOINT is required to list Waka agents")
    cred = DefaultAzureCredential(); client = CosmosClient(s.conversations_cosmos_endpoint, credential=cred)
    try:
        c = client.get_database_client(s.conversations_database).get_container_client("Agents")
        items = [i async for i in c.query_items("SELECT * FROM c WHERE c.type=@type", parameters=[{"name":"@type","value":agent_type}], enable_cross_partition_query=True)]
        return {"items": items}
    finally: await client.close(); await cred.close()

@router.get("/text/agents")
async def text_agents(): return await _list("text")

@router.post("/text/select")
async def select_text(body: dict = Body(...)):
    await set_channel_config("web_text", body); return {"ok": True, "config": body}
