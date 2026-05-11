import httpx
from app.config import get_settings


async def generate_text(system: str, user: str, model: str = "gpt-5.5") -> str:
    s = get_settings()
    if not s.orbit_brain_url:
        raise RuntimeError("ORBIT_BRAIN_URL is required for generated content")
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{s.orbit_brain_url.rstrip('/')}/v1/generate", json={"model": model, "system": system, "user": user})
        r.raise_for_status()
        return r.json()["text"]
