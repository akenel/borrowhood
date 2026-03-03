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

    # Community (local-global: change these per deployment)
    community_name: str = "Trapani, Sicily"  # e.g. "Portland, Oregon" or "Zurich"
    community_country: str = "IT"  # ISO 3166-1 alpha-2
    community_currency: str = "EUR"  # ISO 4217
    community_timezone: str = "Europe/Rome"
    community_tagline: str = "Built from a camper van in Trapani, Sicily, 2026."

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
    telegram_bot_name: str = ""  # e.g. "BorrowHoodBot" (without @)
    telegram_enabled: bool = False

    # PayPal
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_mode: str = "sandbox"  # "sandbox" or "live"
    paypal_merchant_email: str = "angel.kenel@gmail.com"

    # Stripe
    stripe_secret_key: str = ""         # sk_test_... or sk_live_...
    stripe_publishable_key: str = ""    # pk_test_... or pk_live_...
    stripe_webhook_secret: str = ""     # whsec_...

    # AI Provider cascade: "auto" tries gemini -> ollama -> pollinations -> template
    # Set to "gemini", "ollama", or "pollinations" to force a single provider
    ai_provider: str = "auto"

    # Google Gemini
    google_maps_api_key: str = ""
    google_api_key: str = ""  # Gemini API key for AI agents
    gemini_model: str = "gemini-2.5-flash"

    # Ollama (local or Turbo cloud at https://ollama.com)
    ollama_url: str = ""  # "http://localhost:11434" or "https://ollama.com"
    ollama_model: str = "llama3.2"
    ollama_key: str = ""  # API key for Ollama Cloud (not needed for local)

    class Config:
        env_prefix = "BH_"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = BHSettings()
