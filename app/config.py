from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    campaign_id: str = "d00ca9db-6544-46ae-a8d4-c6de76d5bfba"
    campaign_slug: str = "pilot001"
    azure_subscription_id: str | None = None
    azure_resource_group: str = "rg-orbit-campaign-pilot001"
    storage_account_name: str = "stcamppilot001"
    blob_container: str = "artifacts"
    key_vault_name: str = "kv-orbit-camp-pilot001"
    cosmos_endpoint: str | None = None
    cosmos_database: str = "Orbit"
    cosmos_container: str = "Campaigns"
    table_prospects: str = "prospects"
    table_events: str = "events"
    public_base_url: str = "https://pilot001.campaigns.wakaorbit.com"
    graph_mailbox_address: str = "campaign-pilot001@wakacomvoice.onmicrosoft.com"
    orbit_brain_url: str | None = None
    conversations_cosmos_endpoint: str | None = None
    conversations_database: str = "ConversationsDB"
    allowed_origins: str = "*"

    class Config:
        env_file = None
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
