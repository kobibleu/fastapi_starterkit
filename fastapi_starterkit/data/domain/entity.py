from typing import Any

from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declared_attr


@as_declarative()
class Entity:
    id: Any

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
