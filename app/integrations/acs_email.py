from azure.communication.email.aio import EmailClient
from azure.identity.aio import DefaultAzureCredential


async def send_email(config: dict, to_address: str, subject: str, html: str, reply_to: str | None = None) -> dict:
    endpoint = config.get("email_communication_service_endpoint") or config.get("email_communication_service_id")
    sender = config["email_sender_username"]
    display = config.get("email_display_name")
    sender_address = f"{display} <{sender}>" if display else sender
    credential = DefaultAzureCredential()
    client = EmailClient(endpoint=endpoint, credential=credential)
    message = {
        "senderAddress": sender_address,
        "recipients": {"to": [{"address": to_address}]},
        "content": {"subject": subject, "html": html},
    }
    if reply_to:
        message["replyTo"] = [{"address": reply_to}]
    poller = await client.begin_send(message)
    result = await poller.result()
    await credential.close()
    return {"provider_message_id": getattr(result, "id", None) or result.get("id"), "raw": str(result)}
