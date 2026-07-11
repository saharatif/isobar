"""FastAPI dependency injectors — DB session, settings, extractor."""
from typing import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.services.extraction import Extractor


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_extractor(request: Request) -> Extractor:
    return request.app.state.extractor


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session
