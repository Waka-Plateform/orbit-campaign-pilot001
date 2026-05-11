from fastapi import APIRouter, Body, HTTPException
from app.storage.cosmos import get_campaign
from app.storage.blob import read_artifact_text, write_artifact_version, list_artifact_versions

router = APIRouter(prefix="/api/console/sources", tags=["console-sources"])

@router.get("")
async def list_sources():
    return {"items": (await get_campaign()).get("artifacts", [])}

@router.get("/{artifact_id}")
async def read_source(artifact_id: str):
    for a in (await get_campaign()).get("artifacts", []):
        if a.get("artifact_id") == artifact_id:
            return {"artifact": a, "content": await read_artifact_text(a["blob_path"])}
    raise HTTPException(404, "artifact not found")

@router.patch("/{artifact_id}")
async def patch_source(artifact_id: str, body: dict = Body(...)):
    for a in (await get_campaign()).get("artifacts", []):
        if a.get("artifact_id") == artifact_id:
            meta = await write_artifact_version(a["blob_path"], body["content"])
            return {"ok": True, "artifact_id": artifact_id, "version": meta}
    raise HTTPException(404, "artifact not found")

@router.get("/{artifact_id}/history")
async def history(artifact_id: str):
    for a in (await get_campaign()).get("artifacts", []):
        if a.get("artifact_id") == artifact_id:
            return {"items": await list_artifact_versions(a["blob_path"])}
    raise HTTPException(404, "artifact not found")

@router.post("/{artifact_id}/test")
async def test_source(artifact_id: str, body: dict = Body(...)):
    return {"ok": True, "artifact_id": artifact_id, "status": "test_request_recorded", "recipient": body.get("recipient")}
