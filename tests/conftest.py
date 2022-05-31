import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from fastapi_starterkit.crud.endpoints import CRUDEndpoints
from fastapi_starterkit.crud.mapper import BaseMapper
from fastapi_starterkit.crud.service import CRUDService
from fastapi_starterkit.data.domain.entity import Entity
from fastapi_starterkit.data.repository.sql import SqlRepository


class TestModel(Entity):
    id: int = Column(Integer, primary_key=True, index=True)
    value: str = Column(String, nullable=False)


class TestReadSchema(BaseModel):
    id: int
    value: str


class TestCreateSchema(BaseModel):
    value: str


class TestRepo(SqlRepository[TestModel]):
    pass


class TestService(CRUDService[TestModel, int]):
    pass


class TestMapper(BaseMapper[TestModel, TestReadSchema, TestCreateSchema]):
    pass


class TestEndpoint(CRUDEndpoints[TestReadSchema, TestCreateSchema, int]):
    prefix = "/test"


@pytest.fixture
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Entity.metadata.create_all)
    yield engine
    engine.dispose()


@pytest.fixture
async def session(engine):
    session = AsyncSession(bind=engine, expire_on_commit=False)
    yield session
    await session.close()


@pytest.fixture
async def persist_models(session):
    session.add_all([
        TestModel(value="value 1"),
        TestModel(value="value 2"),
        TestModel(value="value 3")
    ])
    await session.commit()


@pytest.fixture
def repo(session):
    repo = TestRepo(session)
    yield repo


@pytest.fixture
def service(repo):
    service = TestService(repo)
    yield service


@pytest.fixture
def mapper():
    mapper = TestMapper()
    yield mapper


@pytest.fixture
def endpoint(service, mapper):
    endpoint = TestEndpoint(service, mapper)
    yield endpoint


@pytest.fixture
def app(endpoint):
    app = FastAPI()
    app.include_router(endpoint.router)
    yield app


@pytest.fixture
def client(app, persist_models):
    client = TestClient(app)
    yield client
