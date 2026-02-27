"""BorrowHood application configuration.

All settings loaded from environment variables with BH_ prefix.
See .env.example for the full list.
"""

from pydantic_settings import BaseSettings


class BHSettings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "BorrowHood"
    app_url: str = "http://localhost:8000"
    secret_key: str = "change-me-in-production"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql+asyncpg://borrowhood:borrowhood_pass@localhost:5432/borrowhood"

    # Keycloak
    kc_url: str = "https://keycloak.helix.local"
    kc_realm: str = "borrowhood"
    kc_client_id: str = "borrowhood-web"
    kc_client_secret: str = ""

    # Minio
    minio_url: str = "localhost:9000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_bucket: str = "borrowhood"

    # Telegram
    telegram_bot_token: str = ""
    telegram_enabled: bool = False

    # PayPal
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_mode: str = "sandbox"  # "sandbox" or "live"
    paypal_merchant_email: str = "angel.kenel@gmail.com"

    # Google
    google_maps_api_key: str = ""

    class Config:
        env_prefix = "BH_"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = BHSettings()
