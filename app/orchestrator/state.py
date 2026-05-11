from app.storage.cosmos import get_campaign, set_runtime_state


async def load_state() -> dict:
    campaign = await get_campaign()
    return campaign.get("runtime_state", {})


async def save_state(state: dict) -> None:
    await set_runtime_state(state)
