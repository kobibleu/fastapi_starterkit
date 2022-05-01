from typing import Generic, TypeVar, get_args

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from fastapi_starterkit.utils import validate_type_arg

READ_SCHEMA = TypeVar("READ_SCHEMA")
CREATE_SCHEMA = TypeVar("CREATE_SCHEMA")
MODEL = TypeVar("MODEL")


class BaseMapper(Generic[MODEL, READ_SCHEMA, CREATE_SCHEMA]):

    def __init__(self):
        type_args = get_args(self.__class__.__orig_bases__[0])
        self.model = type_args[0]
        self.read_schema = type_args[1]
        self.create_schema = type_args[2]

        validate_type_arg(self.read_schema, BaseModel)
        validate_type_arg(self.create_schema, BaseModel)
        validate_type_arg(self.model)

    def map_to_read_schema(self, model: MODEL) -> READ_SCHEMA:
        return self.read_schema(**jsonable_encoder(model))

    def map_to_model(self, schema: CREATE_SCHEMA) -> MODEL:
        return self.model(**jsonable_encoder(schema))
