import re
from app.actions.common import interpolate, apply_runtime_placeholders, schedule_allows
from app.storage.blob import read_artifact_text
from app.storage.tables import insert_event
from app.storage.cosmos import get_campaign
from app.integrations.acs_email import send_email

SUBJECT = "Vos nouvelles conditions générales"
ARTIFACT_PATH = "artifacts/email/A/template.html"
STEP_ID = "A"


async def run(recipient: dict, ctx: dict) -> dict:
    schedule = ctx.get("schedule") or {}
    if not schedule_allows(schedule):
        return {"ok": False, "step_id": STEP_ID, "recipient_id": recipient.get("RowKey"), "status": "deferred_schedule"}
    campaign = await get_campaign()
    config = campaign.get("channels", {}).get("email", {}).get("config", {})
    if not config:
        raise RuntimeError("Email channel must be selected before running campaign")
    html = await read_artifact_text(ARTIFACT_PATH)
    html = interpolate(html, recipient)
    html = apply_runtime_placeholders(html, STEP_ID, recipient)
    to_address = recipient.get("email") or recipient.get("Email")
    result = await send_email(config, to_address, SUBJECT, html, config.get("email_reply_to"))
    provider_id = result.get("provider_message_id")
    await insert_event("email_sent", recipient.get("RowKey"), STEP_ID, {"provider_message_id": provider_id, "to": to_address})
    return {"ok": True, "step_id": STEP_ID, "recipient_id": recipient.get("RowKey"), "provider_message_id": provider_id, "status": "sent"}
