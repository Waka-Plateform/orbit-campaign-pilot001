import base64, hmac, hashlib, re
from datetime import datetime
from zoneinfo import ZoneInfo
from app.config import get_settings

VAR_RE = re.compile(r"{{\s*([a-zA-Z0-9_\.]+)\s*}}")


def interpolate(text: str, recipient: dict) -> str:
    def repl(m):
        key = m.group(1)
        return str(recipient.get(key) or recipient.get(key.split('.')[-1]) or "")
    return VAR_RE.sub(repl, text)


def schedule_allows(schedule: dict) -> bool:
    tz = ZoneInfo(schedule.get("timezone") or "Europe/Paris")
    now = datetime.now(tz)
    if schedule.get("paused"):
        return False
    if schedule.get("days") and now.isoweekday() not in schedule["days"]:
        return False
    opening = schedule.get("opening_hour", 0); closing = schedule.get("closing_hour", 24)
    return opening <= now.hour < closing


def tracking_urls(step_id: str, recipient: dict, target_url: str = "https://www.galaxyai.life/conditions") -> dict:
    s = get_settings(); contact_id = recipient.get("RowKey") or recipient.get("contact_id") or recipient.get("id")
    encoded = base64.urlsafe_b64encode(target_url.encode()).decode()
    token = recipient.get("unsubscribe_token") or ""
    return {
        "open_pixel": f"{s.public_base_url}/track/open/{step_id}?contact_id={contact_id}",
        "conditions_url": f"{s.public_base_url}/track/click/{step_id}?contact_id={contact_id}&u={encoded}",
        "unsubscribe_url": f"{s.public_base_url}/unsubscribe/{contact_id}?t={token}",
        "web_text_agent_url": f"{s.public_base_url}/api/agent/text/session?contact_id={contact_id}",
        "short_url": target_url,
    }


def apply_runtime_placeholders(text: str, step_id: str, recipient: dict) -> str:
    values = tracking_urls(step_id, recipient)
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v).replace("{{ " + k + " }}", v)
    if "</body>" in text and values["open_pixel"] not in text:
        text = text.replace("</body>", f'<img src="{values["open_pixel"]}" width="1" height="1" alt="" /></body>')
    return text
