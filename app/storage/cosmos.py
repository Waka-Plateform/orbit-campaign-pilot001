from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential
from app.config import get_settings


async def _container():
    s = get_settings()
    if not s.cosmos_endpoint:
        raise RuntimeError("COSMOS_ENDPOINT is required")
    cred = DefaultAzureCredential()
    client = CosmosClient(s.cosmos_endpoint, credential=cred)
    return client, cred, client.get_database_client(s.cosmos_database).get_container_client(s.cosmos_container)


async def get_campaign() -> dict:
    s = get_settings(); client, cred, c = await _container()
    try:
        return await c.read_item(s.campaign_id, partition_key=s.campaign_id)
    finally:
        await client.close(); await cred.close()


async def patch_campaign(ops: list[dict]) -> dict:
    s = get_settings(); client, cred, c = await _container()
    try:
        return await c.patch_item(s.campaign_id, partition_key=s.campaign_id, patch_operations=ops)
    finally:
        await client.close(); await cred.close()


async def set_channel_config(channel: str, config: dict) -> dict:
    return await patch_campaign([{"op": "set", "path": f"/channels/{channel}/config", "value": config}])


async def set_schedule(schedule: dict) -> dict:
    return await patch_campaign([{"op": "set", "path": "/schedule", "value": schedule}])


async def set_runtime_state(runtime_state: dict) -> dict:
    return await patch_campaign([{"op": "set", "path": "/runtime_state", "value": runtime_state}])
