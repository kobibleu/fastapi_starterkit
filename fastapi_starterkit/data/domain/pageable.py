import math
from typing import Generic, TypeVar, List, Optional

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageRequest(BaseModel):
    """
    Class for pagination information.

    Attributes:
        page The page index, must not be negative
        size The size of the page to be returned, must be greater than 0
    """
    page: int = Field(ge=0)
    size: int = Field(gt=0)

    @staticmethod
    def of_size(size: int) -> "PageRequest":
        """
        Creates a new PageRequest.
        """
        return PageRequest(page=0, size=size)

    def offset(self) -> int:
        """
        Returns the offset to be taken according to the underlying page and page size.
        """
        return self.page * self.size

    def first(self) -> "PageRequest":
        """
        Return the PageRequest requesting the first page.
        """
        return PageRequest(page=0, size=self.size)

    def next(self) -> "PageRequest":
        """
        Returns the PageRequest requesting the next Page.
        """
        return PageRequest(page=self.page + 1, size=self.size)

    def previous(self) -> "PageRequest":
        """
        Returns the previous PageRequest or the first PageRequest if the current one is already the first one.
        """
        return self if self.page == 0 else PageRequest(page=self.page - 1, size=self.size)

    def has_previous(self) -> bool:
        """
        Returns if there's a previous PageRequest we can access from the current one. Will return false in case the
        current one already refers to the first page
        """
        return self.page > 0


class Page(Generic[T], BaseModel):
    """
    A page is a sublist of a list of objects. It allows gain information about the position of it in the containing
    entire list.

    Attributes:
        content        The content of this page
        page_request   The paging information
        total_elements The total amount of items available
    """
    content: List[T]
    page_request: Optional[PageRequest]
    total_elements: Optional[int]

    def number(self) -> int:
        """
        Returns the number of the current Page.
        """
        return self.page_request.page if self.page_request else 0

    def size(self) -> int:
        """
        Returns the size of the Page.
        """
        return self.page_request.size if self.page_request else len(self.content)

    def number_of_elements(self) -> int:
        """
        Returns the number of elements currently on this Page.
        """
        return len(self.content)

    def total_pages(self) -> int:
        """
        Returns the number of total pages.
        """
        return 1 if self.size() == 0 or self.total_elements is None else math.ceil(self.total_elements / self.size())

    def has_content(self) -> bool:
        """
        Returns if the Page has content at all.
        """
        return bool(self.content)

    def has_next(self) -> bool:
        """
        Returns if there is a next Page.
        """
        return self.number() + 1 < self.total_pages()

    def has_previous(self) -> bool:
        """
        Returns if there is a previous Page.
        """
        return self.number() > 0

    def is_first(self) -> bool:
        """
        Returns if the current Page is the first one.
        """
        return not self.has_previous()

    def is_last(self) -> bool:
        """
        Returns if the current Page is the last one.
        """
        return not self.has_next()

    def next_page_request(self) -> Optional[PageRequest]:
        """
        Returns the PageRequest to request the next Page.
        """
        if not self.page_request:
            return None
        return self.page_request.next() if self.has_next() else None

    def previous_page_request(self) -> Optional[PageRequest]:
        """
        Returns the PageRequest to request the previous Page.
        """
        if not self.page_request:
            return None
        return self.page_request.previous() if self.has_previous() else None
