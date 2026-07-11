"""Application settings, loaded from the environment / .env via pydantic-settings.

Secrets (the OpenAI API key) are held in a SecretStr so they never leak
into logs or reprs. `.env` is gitignored; see `.env.example` for the shape.
"""
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
TEXT_MIMES = {"text/plain", "text/markdown"}
ALLOWED_MIME_TYPES = {PDF_MIME, DOCX_MIME, *TEXT_MIMES}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "isobar-api"
    debug: bool = False

    # v0.1: SQLite stands in for Postgres+pgvector; same schema shape.
    database_url: str = "sqlite+aiosqlite:///./isobar.db"

    # v0.1: local disk stands in for S3/R2.
    storage_dir: Path = Path("uploads")
    max_upload_bytes: int = 10 * 1024 * 1024

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o"

    seed_demo_jobs: bool = True


def get_settings() -> Settings:
    return Settings()
