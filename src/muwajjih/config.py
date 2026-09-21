from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MUWAJIH_",
        env_file=".env",
        extra="forbid",
    )

    app_env: str = Field(default="local", min_length=1)
    model_path: str = Field(default="models/muwajjih_v1.joblib", min_length=1)
    model_version: str = Field(default="muwajjih-v1", min_length=1, max_length=64)
    redis_url: str = Field(default="redis://localhost:6379/0", min_length=1)
    log_level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    max_batch_size: int = Field(default=32, ge=1, le=128)
