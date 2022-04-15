import inspect
from typing import TypeVar, Generic, List, get_args, Optional

from fastapi import status, Depends, HTTPException, Response, Request
from pydantic import BaseModel

from fastapi_starterkit.crud.service import CRUDService, EntityNotFoundError
from fastapi_starterkit.data.domain.entity import Entity
from fastapi_starterkit.data.domain.pageable import PageRequest
from fastapi_starterkit.data.domain.sort import Sort
from fastapi_starterkit.web.decorator import get, post, put, delete
from fastapi_starterkit.web.dependencies import pageable_parameters, sort_parameters
from fastapi_starterkit.web.rest import RestEndpoints
from fastapi_starterkit.web.schema import PageSchema
from fastapi.encoders import jsonable_encoder

READ_SCHEMA = TypeVar("READ_SCHEMA")
CREATE_SCHEMA = TypeVar("CREATE_SCHEMA")
MODEL = TypeVar("MODEL")
ID = TypeVar("ID")


class CRUDEndpoints(Generic[READ_SCHEMA, CREATE_SCHEMA, MODEL, ID], RestEndpoints):

    def __init__(self, service: CRUDService[MODEL, ID], prefix: str = ""):
        # change signature to get real response_model instead of TypeVar
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
            response_model = request.get("response_model")
            if response_model == READ_SCHEMA:
                request["response_model"] = read_schema_type
            elif response_model == List[READ_SCHEMA]:
                request["response_model"] = List[read_schema_type]
            elif response_model == PageSchema[READ_SCHEMA]:
                request["response_model"] = PageSchema[read_schema_type]
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

    @get(
        "/",
        response_model=PageSchema[READ_SCHEMA],
        summary="Retrieve a list of resources.",
        description="Retrieve a list of resources.",
        status_code=status.HTTP_200_OK
    )
    async def read_list(
            self,
            request: Request,
            response: Response,
            page_request: PageRequest = Depends(pageable_parameters),
            sort: Optional[Sort] = Depends(sort_parameters),
    ):
        page = await self.service.find_page(page_request, sort)
        return self._paginated(page, request, response)

    @post(
        "/",
        response_model=READ_SCHEMA,
        summary="Create a resource.",
        description="Create a resource.",
        status_code=status.HTTP_201_CREATED
    )
    async def create(self, payload: CREATE_SCHEMA, request: Request, response: Response) -> READ_SCHEMA:
        data = jsonable_encoder(payload)
        model = self.model_type(**data)
        model = await self.service.create(model)
        return self._created(model, request, response)

    @get(
        "/{id}",
        response_model=READ_SCHEMA,
        summary="Retrieve a specific resource.",
        description="Retrieve a specific resource.",
        status_code=status.HTTP_200_OK
    )
    async def read(self, id: ID) -> READ_SCHEMA:
        try:
            return await self.service.find_by_id(id)
        except EntityNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    @put(
        "/{id}",
        response_model=READ_SCHEMA,
        summary="Update a resource.",
        description="Update a resource.",
        status_code=status.HTTP_200_OK
    )
    async def update(self, id: ID, payload: CREATE_SCHEMA) -> READ_SCHEMA:
        data = jsonable_encoder(payload)
        model = self.model_type(**data)
        model = await self.service.update(id, model)
        return model

    @delete(
        "/{id}",
        summary="Delete a resource.",
        description="Delete a resource.",
        status_code=status.HTTP_204_NO_CONTENT
    )
    async def delete(self, id: ID):
        try:
            return await self.service.delete(id)
        except EntityNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
