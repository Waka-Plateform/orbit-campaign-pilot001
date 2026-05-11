from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from app.config import get_settings


async def _client():
    s = get_settings()
    cred = DefaultAzureCredential()
    url = f"https://{s.storage_account_name}.blob.core.windows.net"
    return BlobServiceClient(url, credential=cred), cred


async def read_artifact_text(blob_path: str) -> str:
    svc, cred = await _client()
    try:
        blob = svc.get_blob_client(get_settings().blob_container, blob_path)
        data = await blob.download_blob()
        return (await data.readall()).decode("utf-8")
    finally:
        await svc.close(); await cred.close()


async def write_artifact_version(blob_path: str, content: str) -> dict:
    svc, cred = await _client()
    try:
        blob = svc.get_blob_client(get_settings().blob_container, blob_path)
        await blob.upload_blob(content.encode("utf-8"), overwrite=True)
        props = await blob.get_blob_properties()
        return {"etag": props.etag, "last_modified": props.last_modified.isoformat()}
    finally:
        await svc.close(); await cred.close()


async def list_artifact_versions(blob_path: str) -> list[dict]:
    svc, cred = await _client()
    try:
        blob = svc.get_blob_client(get_settings().blob_container, blob_path)
        versions = []
        async for item in blob.list_blob_versions(name_starts_with=blob_path):
            versions.append({"name": item.name, "version_id": item.version_id, "last_modified": item.last_modified.isoformat() if item.last_modified else None})
        return versions
    finally:
        await svc.close(); await cred.close()
