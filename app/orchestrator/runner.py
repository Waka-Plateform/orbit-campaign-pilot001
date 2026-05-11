from datetime import datetime, timezone, timedelta
from app.actions.A_email import run as run_email_A
from app.actions.B_sms import run as run_sms_B
from app.orchestrator.schedule import normalize_schedule, next_allowed_at
from app.orchestrator.state import load_state, save_state
from app.storage.cosmos import get_campaign
from app.storage.tables import list_prospects, list_events, insert_event

WAIT_SECONDS = 24 * 60 * 60


def _now(): return datetime.now(timezone.utc)


def _due(item: dict) -> bool:
    planned = item.get("planned_at")
    return not planned or datetime.fromisoformat(planned.replace("Z", "+00:00")) <= _now()


async def _email_bounced(contact_id: str) -> bool:
    events = await list_events(limit=200, contact_id=contact_id)
    types = {e.get("event_type") for e in events}
    return "email_bounced" in types or "email_failed" in types or ("email_delivered" not in types and "email_sent" in types)


async def tick(limit: int = 100) -> dict:
    campaign = await get_campaign(); schedule = normalize_schedule(campaign.get("schedule"))
    if schedule.get("paused"):
        return {"ok": True, "status": "paused", "processed": 0}
    start = schedule.get("start_at")
    if start and datetime.fromisoformat(start.replace("Z", "+00:00")) > _now():
        return {"ok": True, "status": "scheduled", "processed": 0}
    state = await load_state(); prospects = await list_prospects(limit=limit)
    processed = 0
    for p in prospects:
        cid = p.get("RowKey")
        st = state.get(cid) or {"node": "A", "planned_at": None}
        if not _due(st):
            continue
        node = st.get("node")
        ctx = {"schedule": schedule, "flow_state": st}
        if node == "A":
            res = await run_email_A(p, ctx)
            if res.get("status") == "deferred_schedule":
                st["planned_at"] = next_allowed_at(schedule)
            else:
                st = {"node": "W1", "planned_at": (_now() + timedelta(seconds=WAIT_SECONDS)).isoformat(), "last_event": res}
        elif node == "W1":
            st = {"node": "X1", "planned_at": _now().isoformat()}
        elif node == "X1":
            st = {"node": "B" if await _email_bounced(cid) else "END_OK", "planned_at": _now().isoformat()}
        elif node == "B":
            res = await run_sms_B(p, ctx)
            if res.get("status") == "deferred_schedule":
                st["planned_at"] = next_allowed_at(schedule)
            else:
                st = {"node": "END_SMS", "planned_at": None, "last_event": res}
        elif node in ("END_OK", "END_SMS"):
            continue
        state[cid] = st; processed += 1
    await save_state(state)
    await insert_event("orchestrator_tick", None, None, {"processed": processed})
    return {"ok": True, "status": "running", "processed": processed}
