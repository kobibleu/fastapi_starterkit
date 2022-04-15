import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from fastapi_starterkit.crud.endpoint import CRUDEndpoints
from fastapi_starterkit.data.domain.entity import Entity


class TestService:

    def find(self):
        return []


serv = TestService()


class TestModel(Entity):
    id: int = Column(Integer, primary_key=True, index=True)
    value: str = Column(String, nullable=False)


class TestSchema(BaseModel):
    value: str


class TestEndpoint(CRUDEndpoints[TestSchema, TestSchema, TestModel, int]):

    def __init__(self, service: TestService):
        super().__init__(service, prefix="/test")


test_endpoint = TestEndpoint(serv)


app = FastAPI()
app.include_router(test_endpoint.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)