from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def normalize_schedule(raw: dict | None) -> dict:
    raw = raw or {}
    return {"timezone": raw.get("timezone", "Europe/Paris"), "days": raw.get("days", [1,2,3,4,5]), "opening_hour": raw.get("opening_hour", 9), "closing_hour": raw.get("closing_hour", 19), "paused": raw.get("paused", True), "start_at": raw.get("start_at") or raw.get("start"), "end_at": raw.get("end_at")}


def next_allowed_at(schedule: dict) -> str:
    tz = ZoneInfo(schedule.get("timezone", "Europe/Paris")); now = datetime.now(tz)
    candidate = now.replace(hour=schedule.get("opening_hour", 9), minute=0, second=0, microsecond=0)
    if now.hour >= schedule.get("closing_hour", 19): candidate += timedelta(days=1)
    while candidate.isoweekday() not in schedule.get("days", [1,2,3,4,5]): candidate += timedelta(days=1)
    return candidate.isoformat()
