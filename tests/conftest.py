import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from fastapi_starterkit.crud.endpoint import CRUDEndpoints
from fastapi_starterkit.crud.service import CRUDService
from fastapi_starterkit.data.domain.entity import Entity
from fastapi_starterkit.data.repository.sql import AsyncSqlRepository


class TestModel(Entity):
    id: int = Column(Integer, primary_key=True, index=True)
    value: str = Column(String, nullable=False)


class TestReadSchema(BaseModel):
    id: int
    value: str

    class Config:
        orm_mode = True


class TestCreateSchema(BaseModel):
    value: str


class TestRepo(AsyncSqlRepository[TestModel]):
    pass


class TestService(CRUDService[TestModel, int]):
    pass


class TestEndpoint(CRUDEndpoints[TestReadSchema, TestCreateSchema, TestModel, int]):
    prefix = "/test"

    def __init__(self, toto: TestService):
        super().__init__(toto)


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session = AsyncSession(bind=engine)
    async with engine.begin() as conn:
        await conn.run_sync(Entity.metadata.create_all)
    session.add(TestModel(id=1, value="value 1"))
    session.add(TestModel(id=2, value="value 2"))
    session.add(TestModel(id=3, value="value 3"))
    await session.commit()
    yield session


@pytest.fixture
def repo(session):
    repo = TestRepo(session)
    yield repo


@pytest.fixture
def service(repo):
    service = TestService(repo)
    yield service


@pytest.fixture
def endpoint(service):
    endpoint = TestEndpoint(service)
    yield endpoint


@pytest.fixture
def app(endpoint):
    app = FastAPI()
    app.include_router(endpoint.router)
    yield app


@pytest.fixture
def client(app):
    client = TestClient(app)
    yield client
