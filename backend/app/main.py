"""FastAPI app factory + lifespan (engine, tables, demo seed, extractor).

Run locally:  uv run uvicorn app.main:app --app-dir backend --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import Settings, get_settings
from app.logging_config import configure_logging
from app.models import Base
from app.routers import candidates, health, uploads
from app.services.extraction import build_extractor
from app.services.seed import seed_demo_jobs

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.debug)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_async_engine(settings.database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        app.state.settings = settings
        app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
        api_key = (
            settings.openai_api_key.get_secret_value()
            if settings.openai_api_key
            else None
        )
        app.state.extractor = build_extractor(api_key, settings.openai_model)
        settings.storage_dir.mkdir(parents=True, exist_ok=True)

        if settings.seed_demo_jobs:
            async with app.state.session_factory() as session:
                seeded = await seed_demo_jobs(session)
                if seeded:
                    logger.info("seeded demo jobs", extra={"ctx": {"count": seeded}})

        yield
        await engine.dispose()

    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(uploads.router)
    app.include_router(candidates.router)
    return app


app = create_app()
