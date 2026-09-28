from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    google_client_id: str
    google_client_secret: str
<<<<<<< Updated upstream
=======
    otp_modo: str = "dev"

    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_verify_service_sid: str | None = None

    sendgrid_api_key: str | None = None
    sendgrid_from_email: str | None = None
    sendgrid_template_id: str | None = None
>>>>>>> Stashed changes

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()