from dependency_injector import containers, providers
from sqlmodel import Session, create_engine, SQLModel

from config import settings as config
from repositories.job_repository import JobRepository
from repositories.search_state_repository import SearchStateRepository
from tools.jobs_tool import JobsTool


def _create_engine(url: str):
    eng = create_engine(url)
    SQLModel.metadata.create_all(eng)
    return eng


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(_create_engine, url=config.DATABASE_URL)
    session = providers.Singleton(Session, bind=engine)
    job_repo = providers.Singleton(JobRepository, session=session)
    state_repo = providers.Singleton(SearchStateRepository, session=session)
    jobs_tool = providers.Singleton(
        JobsTool,
        job_repo=job_repo,
        state_repo=state_repo,
    )
