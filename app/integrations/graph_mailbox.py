import httpx
from azure.identity.aio import DefaultAzureCredential
from app.config import get_settings

GRAPH = "https://graph.microsoft.com/v1.0"


async def _token() -> tuple[str, DefaultAzureCredential]:
    cred = DefaultAzureCredential()
    token = await cred.get_token("https://graph.microsoft.com/.default")
    return token.token, cred


async def list_messages(top: int = 25) -> list[dict]:
    s = get_settings(); token, cred = await _token()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(f"{GRAPH}/users/{s.graph_mailbox_address}/messages", headers={"Authorization": f"Bearer {token}"}, params={"$top": top, "$orderby": "receivedDateTime desc"})
            r.raise_for_status(); return r.json().get("value", [])
    finally:
        await cred.close()
