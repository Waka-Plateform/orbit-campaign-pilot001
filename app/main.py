import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.console.main import router as console_main_router
from app.console.base import router as console_base_router
from app.console.plan import router as console_plan_router
from app.console.sources import router as console_sources_router
from app.console.channels import router as console_channels_router
from app.console.dashboard import router as console_dashboard_router
from app.console.inbox import router as console_inbox_router
from app.channels.email import router as email_channel_router
from app.channels.sms import router as sms_channel_router
from app.channels.waka_agents import router as waka_agents_router
from app.tracking.open import router as tracking_open_router
from app.tracking.click import router as tracking_click_router
from app.tracking.unsubscribe import router as unsubscribe_router
from app.webhooks.email_delivery import router as webhook_email_router
from app.webhooks.sms_event import router as webhook_sms_router
from app.webhooks.agent_callback import router as webhook_agent_router
from app.events.sse import router as sse_router
from app.events.pump import mailbox_pump
from app.orchestrator.runner import tick


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = asyncio.Event()
    pump_task = asyncio.create_task(mailbox_pump(stop))
    try:
        yield
    finally:
        stop.set()
        pump_task.cancel()


app = FastAPI(title="orbit-campaign-pilot001", version="1.0.1", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.allowed_origins == "*" else settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in [
    console_main_router,
    console_base_router,
    console_plan_router,
    console_sources_router,
    console_channels_router,
    console_dashboard_router,
    console_inbox_router,
    email_channel_router,
    sms_channel_router,
    waka_agents_router,
    tracking_open_router,
    tracking_click_router,
    unsubscribe_router,
    webhook_email_router,
    webhook_sms_router,
    webhook_agent_router,
    sse_router,
]:
    app.include_router(r)


@app.get("/health")
async def health():
    return {"ok": True, "service": "orbit-campaign-pilot001", "campaign_id": settings.campaign_id}


@app.post("/actions/A/run")
async def run_action_a(recipient: dict, ctx: dict | None = None):
    from app.actions.A_email import run
    return await run(recipient, ctx or {})


@app.post("/actions/B/run")
async def run_action_b(recipient: dict, ctx: dict | None = None):
    from app.actions.B_sms import run
    return await run(recipient, ctx or {})


@app.post("/api/orchestrator/tick")
async def orchestrator_tick(limit: int = 100):
    return await tick(limit=limit)


@app.get("/api/agent/text/session")
async def web_text_session(contact_id: str | None = None):
    return {"web_embed_url": f"https://app.wakaorbit.com/agents/89ae8482-e36f-47b7-9145-f94511a8b520/embed?campaign_id={settings.campaign_id}&contact_id={contact_id or ''}"}
