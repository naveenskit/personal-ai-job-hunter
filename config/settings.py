from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    timezone: str = "Asia/Kolkata"

    app_secret_key: SecretStr = Field(default=SecretStr("change-me"))
    api_secret_key: SecretStr = Field(default=SecretStr("change-me"))

    database_url: str = "sqlite+aiosqlite:///./data/jobhunter.db"

    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-1.5-flash"

    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None
    # Optional token to protect the dashboard endpoints. If set, requests
    # to dashboard APIs must include header 'X-DASHBOARD-TOKEN'.
    dashboard_token: SecretStr | None = None

    data_dir: Path = Path("./data")
    log_dir: Path = Path("./logs")
    export_dir: Path = Path("./exports")

    location_preferences_path: Path = Path("./config/location_preferences.yaml")
    role_preferences_path: Path = Path("./config/role_preferences.yaml")
    job_sources_path: Path = Path("./config/job_sources.yaml")
    scoring_weights_path: Path = Path("./config/scoring_weights.yaml")

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    def ensure_runtime_dirs(self) -> None:
        for path in (self.data_dir, self.log_dir, self.export_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_runtime_dirs()
    return settings
