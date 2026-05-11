import hmac, hashlib
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient
from app.config import get_settings
from app.storage.tables import update_prospect, insert_event

router = APIRouter(tags=["tracking"])

async def _secret():
    s = get_settings(); cred = DefaultAzureCredential(); client = SecretClient(f"https://{s.key_vault_name}.vault.azure.net", cred)
    try:
        sec = await client.get_secret("unsubscribe-secret"); return sec.value
    finally:
        await client.close(); await cred.close()

@router.get("/unsubscribe/{contact_id}")
async def unsubscribe(contact_id: str, t: str):
    secret = await _secret(); expected = hmac.new(secret.encode(), contact_id.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, t): raise HTTPException(403, "invalid token")
    await update_prospect(contact_id, {"optout": True}); await insert_event("email_unsubscribe", contact_id, None, {})
    return HTMLResponse("<html><body><h1>Désinscription confirmée</h1><p>Vous ne recevrez plus cette campagne.</p></body></html>")
