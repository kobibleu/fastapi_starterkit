import abc
from typing import List, Any, Optional

from fastapi_starterkit.data.domain.pageable import PageRequest, Page
from fastapi_starterkit.data.domain.sort import Sort


class CRUDRepository(abc.ABC):
    """
    Interface for generic CRUD operations for a specific type.
    """

    @abc.abstractmethod
    async def count(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_all(self):
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_all_by_id(self, ids: List[Any]):
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_by_id(self, id: Any):
        raise NotImplementedError()

    @abc.abstractmethod
    async def exists_by_id(self, id: Any) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    async def find_all(self, sort: Sort = None) -> List[Any]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def find_all_by_id(self, ids: List[Any]) -> List[Any]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def find_by_id(self, id: Any) -> Optional[Any]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def save(self, model: Any) -> Any:
        raise NotImplementedError()

    @abc.abstractmethod
    async def save_all(self, models: List[Any]) -> List[Any]:
        raise NotImplementedError()


class PagingRepository(CRUDRepository):
    """
    Extension of CrudRepository to provide additional method to retrieve entities using the pagination.
    """

    @abc.abstractmethod
    async def find_page(self, page_request: PageRequest, sort: Sort = None) -> Page[Any]:
        raise NotImplementedError()
