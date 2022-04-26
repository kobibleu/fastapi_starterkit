from typing import Optional

import bson
from pydantic import BaseModel


class ObjectId(bson.ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return bson.ObjectId(str(v))
        except bson.errors.InvalidId:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Document(BaseModel):
    id: Optional[ObjectId]

    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return data
        id = data.pop('_id', None)
        return cls(id=id, **data)

    def mongo(self):
        parsed: dict = self.dict()
        # mongodb uses `_id` as default key
        id = parsed.pop("id", None)
        if id is not None:
            parsed['_id'] = id
        return parsed
