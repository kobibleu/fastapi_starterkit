import inspect
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic, List, get_args, Optional, Type, Any, Union

from fastapi import status, Depends, HTTPException, Response, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from fastapi_starterkit.crud.service import CRUDService, EntityNotFoundError
from fastapi_starterkit.data.domain.document import Document
from fastapi_starterkit.data.domain.pageable import PageRequest
from fastapi_starterkit.data.domain.sort import Sort
from fastapi_starterkit.utils import validate_type_arg
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

    def __init__(self, service: CRUDService[MODEL, ID]):
        type_args = get_args(self.__class__.__orig_bases__[0])

        self.read_schema = type_args[0]
        self.create_schema = type_args[1]
        self.model = type_args[2]
        self.id = type_args[3]

        validate_type_arg(self.read_schema, BaseModel)
        validate_type_arg(self.create_schema, BaseModel)
        validate_type_arg(self.model)
        validate_type_arg(self.id)

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
                    typed_parameters.append(p.replace(kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=self.id))
                elif p.annotation == CREATE_SCHEMA:
                    typed_parameters.append(p.replace(kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=self.create_schema))
                else:
                    typed_parameters.append(p)
            endpoint.__signature__ = signature.replace(parameters=typed_parameters)

        super().__init__()
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
        page.content = [self._map_to_schema(m) for m in page.content]
        return self._paginated(page, request, response)

    @post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, payload: CREATE_SCHEMA, request: Request, response: Response) -> READ_SCHEMA:
        model = self._map_to_model(payload)
        model = await self.service.create(model)
        schema = self._map_to_schema(model)
        return self._created(schema, request, response)

    @get("/{id}", status_code=status.HTTP_200_OK)
    async def read_one(self, id: ID) -> READ_SCHEMA:
        try:
            model = await self.service.find_by_id(id)
            return self._map_to_schema(model)
        except EntityNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @put("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: ID, payload: CREATE_SCHEMA) -> READ_SCHEMA:
        model = self._map_to_model(payload)
        model = await self.service.update(id, model)
        return self._map_to_schema(model)

    @delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(self, id: ID):
        try:
            return await self.service.delete(id)
        except EntityNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    def _map_to_model(self, schema: CREATE_SCHEMA) -> MODEL:
        return self.model(**jsonable_encoder(schema))

    def _map_to_schema(self, model: MODEL) -> READ_SCHEMA:
        if issubclass(self.model, Document):
            return self.read_schema(id=str(model.id), **model.dict(exclude={"id"}))
        else:
            return self.read_schema(**jsonable_encoder(model))
