import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from fastapi_starterkit.crud.endpoint import CRUDEndpoints, CRUDApiDoc, ApiDoc
from fastapi_starterkit.data.domain.entity import Entity
from fastapi_starterkit.web.schema import PageSchema


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
    override_api_doc = CRUDApiDoc(
        read_all=ApiDoc(
            response_model=PageSchema[TestSchema],
            summary="Retrieve a subset of tests",
            description="Retrieve a subset of tests",
            tags=["Test"],
        ),
        read_one=ApiDoc(
            response_model=TestSchema,
            summary="Retrieve a specific test",
            description="Retrieve a specific test",
            tags=["Test"],
        ),
        create=ApiDoc(
            response_model=TestSchema,
            summary="Create a test",
            description="Create a test",
            tags=["Test"],
        ),
        update=ApiDoc(
            response_model=TestSchema,
            summary="Update a test",
            description="Update a test",
            tags=["Test"],
        ),
        delete=ApiDoc(
            summary="Delete a test",
            description="Delete a test",
            tags=["Test"],
        ),
    )

    def __init__(self, service: TestService):
        super().__init__(service, prefix="/test")


test_endpoint = TestEndpoint(serv)


app = FastAPI()
app.include_router(test_endpoint.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)