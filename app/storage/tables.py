import json, uuid
from datetime import datetime, timezone
from azure.data.tables.aio import TableServiceClient
from azure.identity.aio import DefaultAzureCredential
from app.config import get_settings


async def _svc():
    s = get_settings(); cred = DefaultAzureCredential()
    return TableServiceClient(f"https://{s.storage_account_name}.table.core.windows.net", credential=cred), cred


async def insert_event(event_type: str, contact_id: str | None, step_id: str | None, data: dict | None = None) -> dict:
    s = get_settings(); svc, cred = await _svc()
    now = datetime.now(timezone.utc).isoformat()
    entity = {"PartitionKey": s.campaign_id, "RowKey": f"{now}_{uuid.uuid4().hex}", "event_type": event_type, "contact_id": contact_id or "", "step_id": step_id or "", "data": json.dumps(data or {}, ensure_ascii=False), "ts": now}
    try:
        await svc.get_table_client(s.table_events).create_entity(entity)
        return entity
    finally:
        await svc.close(); await cred.close()


async def list_events(limit: int = 200, contact_id: str | None = None, event_type: str | None = None) -> list[dict]:
    s = get_settings(); svc, cred = await _svc()
    filters = [f"PartitionKey eq '{s.campaign_id}'"]
    if contact_id: filters.append(f"contact_id eq '{contact_id}'")
    if event_type: filters.append(f"event_type eq '{event_type}'")
    try:
        out = []
        async for e in svc.get_table_client(s.table_events).query_entities(" and ".join(filters), results_per_page=limit):
            item = dict(e)
            if item.get("data"):
                try: item["data"] = json.loads(item["data"])
                except Exception: pass
            out.append(item)
            if len(out) >= limit: break
        return out
    finally:
        await svc.close(); await cred.close()


async def list_prospects(limit: int = 100, q: str | None = None) -> list[dict]:
    s = get_settings(); svc, cred = await _svc()
    try:
        out = []
        async for e in svc.get_table_client(s.table_prospects).query_entities(f"PartitionKey eq '{s.campaign_id}'", results_per_page=limit):
            d = dict(e)
            if not q or q.lower() in json.dumps(d, ensure_ascii=False).lower():
                out.append(d)
            if len(out) >= limit: break
        return out
    finally:
        await svc.close(); await cred.close()


async def update_prospect(contact_id: str, fields: dict) -> None:
    s = get_settings(); svc, cred = await _svc()
    try:
        ent = {"PartitionKey": s.campaign_id, "RowKey": contact_id, **fields}
        await svc.get_table_client(s.table_prospects).upsert_entity(ent, mode="Merge")
    finally:
        await svc.close(); await cred.close()
