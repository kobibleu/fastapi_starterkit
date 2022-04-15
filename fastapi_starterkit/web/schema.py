from typing import Generic, TypeVar, List

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageSchema(Generic[T], BaseModel):
    content: List[T] = Field(description="The content of this page.")
    page: int = Field(description="The number of the current page.")
    page_size: int = Field(description="The size of the page.")
    total_pages: int = Field(description="The total amount of pages available.")
    total_elements: int = Field(description="The total amount of items available.")
