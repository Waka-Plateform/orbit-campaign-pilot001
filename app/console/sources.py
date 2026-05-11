from fastapi import APIRouter, Body, HTTPException
from app.storage.cosmos import get_campaign
from app.storage.blob import read_artifact_text, write_artifact_version, list_artifact_versions
from app.integrations.orbit_brain import generate_text

router = APIRouter(prefix="/api/console/sources", tags=["console-sources"])


async def _find_artifact(artifact_id: str) -> dict:
    for artifact in (await get_campaign()).get("artifacts", []):
        if artifact.get("artifact_id") == artifact_id:
            return artifact
    raise HTTPException(404, "artifact not found")


@router.get("")
async def list_sources():
    return {"items": (await get_campaign()).get("artifacts", [])}


@router.get("/{artifact_id}")
async def read_source(artifact_id: str):
    artifact = await _find_artifact(artifact_id)
    return {"artifact": artifact, "content": await read_artifact_text(artifact["blob_path"])}


@router.patch("/{artifact_id}")
async def patch_source(artifact_id: str, body: dict = Body(...)):
    artifact = await _find_artifact(artifact_id)
    meta = await write_artifact_version(artifact["blob_path"], body["content"])
    return {"ok": True, "artifact_id": artifact_id, "version": meta}


@router.get("/{artifact_id}/history")
async def history(artifact_id: str):
    artifact = await _find_artifact(artifact_id)
    return {"items": await list_artifact_versions(artifact["blob_path"])}


@router.post("/{artifact_id}/test")
async def test_source(artifact_id: str, body: dict = Body(...)):
    await _find_artifact(artifact_id)
    return {
        "ok": True,
        "artifact_id": artifact_id,
        "status": "test_request_recorded",
        "recipient": body.get("recipient"),
    }


@router.post("/{artifact_id}/regenerate")
async def regenerate_source(artifact_id: str, body: dict = Body(default_factory=dict)):
    artifact = await _find_artifact(artifact_id)
    current_content = await read_artifact_text(artifact["blob_path"])
    instruction = body.get("instruction") or "Regenerate this campaign artifact while preserving its channel, compliance requirements, variables and tracking placeholders."
    system = (
        "You are Orbit campaign Scribe. Regenerate an existing campaign source artifact. "
        "Return only the updated artifact content, with no markdown fences and no commentary. "
        "Preserve all functional placeholders, opt-out or STOP compliance text, and the original artifact format."
    )
    user = (
        f"Artifact id: {artifact_id}\n"
        f"Artifact metadata: {artifact}\n"
        f"User instruction: {instruction}\n\n"
        f"Current content:\n{current_content}"
    )
    regenerated_content = await generate_text(system=system, user=user, model=body.get("model", "gpt-5.5"))
    meta = await write_artifact_version(artifact["blob_path"], regenerated_content)
    return {
        "ok": True,
        "artifact_id": artifact_id,
        "content": regenerated_content,
        "version": meta,
        "model": body.get("model", "gpt-5.5"),
    }
