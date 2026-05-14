import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from src.main import create_app
from src.database import get_session
from src.order.repository import OrderRepository


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:14") as pg:
        yield pg


@pytest.fixture(scope="session")
def db_url(postgres_container):
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@pytest.fixture(scope="session")
def _run_migrations(db_url):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest_asyncio.fixture(scope="session")
async def db_engine(db_url, _run_migrations):
    engine = create_async_engine(db_url, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncSession:
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def order_repository(db_session):
    return OrderRepository(db_session)


@pytest_asyncio.fixture
async def test_app(db_engine):
    app = create_app()
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async def override_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    yield app


@pytest_asyncio.fixture
async def client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as c:
        yield c
