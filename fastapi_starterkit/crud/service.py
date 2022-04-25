from typing import TypeVar, Generic, List

from fastapi_starterkit.data.domain.pageable import PageRequest, Page
from fastapi_starterkit.data.domain.sort import Sort
from fastapi_starterkit.data.repository.core import PagingRepository

T = TypeVar("T")
ID = TypeVar("ID")


class EntityNotFoundError(Exception):
    pass


class CRUDService(Generic[T, ID]):

    def __init__(self, repo: PagingRepository):
        self._repo = repo

    async def find_all(self, sort: Sort = None) -> List[T]:
        """
        Returns all the resources.
        """
        return await self._repo.find_all(sort)

    async def find_page(self, page_request: PageRequest, sort: Sort = None) -> Page[T]:
        """
        Returns a subset of resources mathing the paging restriction.
        """
        return await self._repo.find_page(page_request, sort)

    async def find_by_id(self, id: ID) -> T:
        """
        Returns a resource by its id.
        """
        model = await self._repo.find_by_id(id)
        if model is None:
            raise EntityNotFoundError()
        return model

    async def create(self, model: T) -> T:
        """
        Create a resource.
        """
        return await self._repo.save(model)

    async def update(self, id: ID, model: T) -> T:
        """
        Update a resource.
        """
        existing_model = await self._repo.find_by_id(id)
        if existing_model is None:
            raise EntityNotFoundError()  # Create instead of not found ?
        for attr, value in vars(model).items():  # We can also specify attributes method on entity if we want to control that
            setattr(existing_model, attr, value)
        return await self._repo.save(existing_model)

    async def delete(self, id: ID):
        """
        Delete a resource.
        """
        if not await self._repo.exists_by_id(id):
            raise EntityNotFoundError()
        await self._repo.delete_by_id(id)
