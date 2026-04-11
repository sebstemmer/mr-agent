from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from utils.common.src.config import settings
from utils.common.src.database import create_engine
from utils.common.src.health_controller import HealthController
from utils.common.src.http_client import create_http_client
from utils.common.src.router import create_router
from utils.common.src.scheduler import create_scheduler
from utils.patcher.src.container import PatcherContainer


class UtilsContainer(containers.DeclarativeContainer):
    scheduler = providers.Singleton(create_scheduler)
    http_client = providers.Singleton(create_http_client)
    engine = providers.Singleton(
        create_engine,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        db=settings.POSTGRES_DB,
    )
    session_factory = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    router = providers.Singleton(create_router)
    health_controller = providers.Singleton(
        HealthController, engine=engine, router=router
    )
    patcher_container = providers.Container(
        PatcherContainer, session_factory=session_factory
    )
