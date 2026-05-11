from azure.communication.sms.aio import SmsClient
from azure.identity.aio import DefaultAzureCredential


async def send_sms(config: dict, to_number: str, body: str) -> dict:
    endpoint = config.get("sms_communication_service_endpoint") or config.get("sms_communication_service_id")
    credential = DefaultAzureCredential()
    client = SmsClient(endpoint=endpoint, credential=credential)
    responses = await client.send(from_=config["sms_phone_number"], to=[to_number], message=body, enable_delivery_report=True)
    await credential.close()
    r = responses[0] if responses else None
    return {"provider_message_id": getattr(r, "message_id", None), "status": getattr(r, "http_status_code", None), "raw": str(r)}
