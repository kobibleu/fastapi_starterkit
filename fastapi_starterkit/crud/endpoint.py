import inspect
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic, List, get_args, Optional, Type, Any, Union

from fastapi import status, Depends, HTTPException, Response, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from fastapi_starterkit.crud.service import CRUDService, EntityNotFoundError
from fastapi_starterkit.data.domain.entity import Entity
from fastapi_starterkit.data.domain.pageable import PageRequest
from fastapi_starterkit.data.domain.sort import Sort
from fastapi_starterkit.web.decorator import get, post, put, delete
from fastapi_starterkit.web.dependencies import pageable_parameters, sort_parameters
from fastapi_starterkit.web.rest import RestEndpoints

READ_SCHEMA = TypeVar("READ_SCHEMA")
CREATE_SCHEMA = TypeVar("CREATE_SCHEMA")
MODEL = TypeVar("MODEL")
ID = TypeVar("ID")


@dataclass
class ApiDoc:
    response_model: Optional[Type[Any]] = None
    tags: Optional[List[Union[str, Enum]]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    response_description: str = "Successful Response"


@dataclass
class CRUDApiDoc:
    read_all: Optional[ApiDoc] = None
    read_one: Optional[ApiDoc] = None
    create: Optional[ApiDoc] = None
    update: Optional[ApiDoc] = None
    delete: Optional[ApiDoc] = None

    def get_api_doc(self, func_name: str) -> ApiDoc:
        return self.__dict__.get(func_name)


class CRUDEndpoints(Generic[READ_SCHEMA, CREATE_SCHEMA, MODEL, ID], RestEndpoints):
    override_api_doc: CRUDApiDoc = CRUDApiDoc()

    def __init__(self, service: CRUDService[MODEL, ID], prefix: str = ""):
        type_args = get_args(self.__class__.__orig_bases__[0])

        read_schema_type = type_args[0]
        if read_schema_type == READ_SCHEMA:
            raise ValueError("Missing READ_SCHEMA type")
        if not issubclass(read_schema_type, BaseModel):
            raise ValueError(f"Schema type {read_schema_type} is not `pydantic.BaseModel`")

        create_schema_type = type_args[1]
        if create_schema_type == CREATE_SCHEMA:
            raise ValueError("Missing CREATE_SCHEMA type")
        if not issubclass(create_schema_type, BaseModel):
            raise ValueError(f"Schema type {create_schema_type} is not `pydantic.BaseModel`")

        self.model_type = type_args[2]
        if self.model_type == MODEL:
            raise ValueError("Missing MODEL type")
        if not issubclass(self.model_type, Entity):
            raise ValueError(f"Model type {self.model_type} is not `fastapi_starterkit.data.domain.entity.Entity`")

        id_type = type_args[3]
        if id_type == ID:
            raise ValueError("Missing ID type")

        for endpoint in self.endpoints:
            request: dict = getattr(endpoint, "_request")
            # override request params with values coming from specific endpoints
            override_api_doc = self.override_api_doc.get_api_doc(endpoint.__name__)
            if override_api_doc:
                request.update(**override_api_doc.__dict__)
            # change signature to get real body instead of TypeVar
            signature = inspect.signature(endpoint)
            parameters = list(signature.parameters.values())
            typed_parameters = []
            for p in parameters:
                if p.annotation == ID:
                    typed_parameters.append(p.replace(kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=id_type))
                elif p.annotation == CREATE_SCHEMA:
                    typed_parameters.append(p.replace(kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=create_schema_type))
                else:
                    typed_parameters.append(p)
            endpoint.__signature__ = signature.replace(parameters=typed_parameters)

        super().__init__(prefix)
        self.service = service

    @get("/", status_code=status.HTTP_200_OK)
    async def read_all(
            self,
            request: Request,
            response: Response,
            page_request: PageRequest = Depends(pageable_parameters),
            sort: Optional[Sort] = Depends(sort_parameters),
    ):
        page = await self.service.find_page(page_request, sort)
        return self._paginated(page, request, response)

    @post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, payload: CREATE_SCHEMA, request: Request, response: Response) -> READ_SCHEMA:
        data = jsonable_encoder(payload)
        model = self.model_type(**data)
        model = await self.service.create(model)
        return self._created(model, request, response)

    @get("/{id}", status_code=status.HTTP_200_OK)
    async def read_one(self, id: ID) -> READ_SCHEMA:
        try:
            return await self.service.find_by_id(id)
        except EntityNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @put("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: ID, payload: CREATE_SCHEMA) -> READ_SCHEMA:
        data = jsonable_encoder(payload)
        model = self.model_type(**data)
        model = await self.service.update(id, model)
        return model

    @delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(self, id: ID):
        try:
            return await self.service.delete(id)
        except EntityNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
