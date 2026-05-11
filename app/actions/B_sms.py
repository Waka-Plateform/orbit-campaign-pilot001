from app.actions.common import interpolate, apply_runtime_placeholders, schedule_allows
from app.storage.blob import read_artifact_text
from app.storage.tables import insert_event
from app.storage.cosmos import get_campaign
from app.integrations.acs_sms import send_sms

ARTIFACT_PATH = "artifacts/sms/B/template.txt"
STEP_ID = "B"


async def run(recipient: dict, ctx: dict) -> dict:
    schedule = ctx.get("schedule") or {}
    if not schedule_allows(schedule):
        return {"ok": False, "step_id": STEP_ID, "recipient_id": recipient.get("RowKey"), "status": "deferred_schedule"}
    campaign = await get_campaign()
    config = campaign.get("channels", {}).get("sms", {}).get("config", {})
    if not config:
        raise RuntimeError("SMS channel must be selected before running campaign")
    body = await read_artifact_text(ARTIFACT_PATH)
    body = interpolate(body, recipient)
    body = apply_runtime_placeholders(body, STEP_ID, recipient)
    to_number = recipient.get("phone") or recipient.get("Phone") or recipient.get("mobile")
    result = await send_sms(config, to_number, body)
    provider_id = result.get("provider_message_id")
    await insert_event("sms_sent", recipient.get("RowKey"), STEP_ID, {"provider_message_id": provider_id, "to": to_number})
    return {"ok": True, "step_id": STEP_ID, "recipient_id": recipient.get("RowKey"), "provider_message_id": provider_id, "status": "sent"}
