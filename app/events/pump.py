import asyncio
from app.integrations.graph_mailbox import list_messages
from app.storage.tables import insert_event

async def mailbox_pump(stop_event: asyncio.Event):
    seen = set()
    while not stop_event.is_set():
        try:
            for msg in await list_messages(top=10):
                mid = msg.get("id")
                if mid and mid not in seen:
                    seen.add(mid); await insert_event("inbox.email.new", None, None, msg)
        except Exception:
            pass
        await asyncio.sleep(60)
