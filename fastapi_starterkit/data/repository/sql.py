import asyncio
from typing import TypeVar, Generic, get_args, Iterable, List, Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_starterkit.data.domain.entity import Entity
from fastapi_starterkit.data.domain.pageable import PageRequest, Page
from fastapi_starterkit.data.domain.sort import Sort
from fastapi_starterkit.data.repository.core import PagingRepository

T = TypeVar("T", bound=Entity)


class AsyncSqlRepository(Generic[T], PagingRepository):
    """
    SQL repository.

    T: the type of object handled by the repository, must be `fastapi_starterkit.data.domain.entity.Entity`.
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self._model = get_args(self.__orig_bases__[0])[0]
        if self._model == T:
            raise ValueError("Missing repository type")
        if not issubclass(self._model, Entity):
            raise ValueError(f"Model type {self._model} is not `fastapi_starterkit.data.domain.entity.Entity`")

    async def count(self) -> int:
        """
        Returns the number of entities available.
        """
        stmt = select(func.count()).select_from(self._model)
        return (await self._session.execute(stmt)).scalar()

    async def delete_all(self):
        """
        Deletes all entities.
        """
        stmt = delete(self._model)
        await self._session.execute(stmt)

    async def delete_all_by_id(self, ids: Iterable[id]):
        """
        Deletes all entities with the given IDs.
        """
        stmt = delete(self._model).where(self._model.id.in_(ids))
        await self._session.execute(stmt)

    async def delete_by_id(self, id: int):
        """
        Deletes the entity with the given id.
        """
        stmt = delete(self._model).where(self._model.id == id)
        await self._session.execute(stmt)

    async def exists_by_id(self, id: int) -> bool:
        """
        Returns whether an entity with the given id exists.
        """
        stmt = select(func.count()).select_from(self._model).where(self._model.id == id)
        return bool((await self._session.execute(stmt)).scalar())

    async def find_all(self, sort: Sort = None) -> List[T]:
        """
        Returns all entities sorted by the given options.
        """
        stmt = select(self._model)
        order_by = self._sort_query(sort)
        if order_by:
            stmt = stmt.order_by(*order_by)
        return (await self._session.execute(stmt)).scalars().all()

    async def find_page(self, page_request: PageRequest, sort: Sort = None) -> Page[T]:
        """
        Returns a Page of entities meeting the paging restriction.
        """
        stmt = select(self._model).offset(page_request.offset()).limit(page_request.size)
        order_by = self._sort_query(sort)
        if order_by:
            stmt = stmt.order_by(*order_by)
        result = (await self._session.execute(stmt)).scalars().all()
        count = await self.count()
        return Page(
            content=result,
            page_request=page_request,
            total_elements=count
        )

    async def find_all_by_id(self, ids: Iterable[id]) -> List[T]:
        """
        Returns all entities with the given IDs.
        """
        stmt = select(self._model).where(self._model.id.in_(ids))
        return (await self._session.execute(stmt)).scalars().all()

    async def find_by_id(self, id: id) -> Optional[T]:
        """
        Returns an entity by its id.
        """
        stmt = select(self._model).where(self._model.id == id)
        return (await self._session.execute(stmt)).scalar()

    async def save(self, model: T) -> T:
        """
        Saves a given entity.
        """
        if not isinstance(model, Entity):
            raise ValueError(f"type {type(model)} not handled by repository.")
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def save_all(self, models: Iterable[T]) -> List[T]:
        """
        Saves all given entities.
        """
        if any(not isinstance(m, Entity) for m in models):
            raise ValueError(f"one of type in the list of model is not handled by repository.")
        self._session.add_all(models)
        await self._session.flush()
        await asyncio.gather(*[self._session.refresh(m) for m in models])
        return list(models)

    def _sort_query(self, sort: Sort) -> List[str]:
        """
        Build sqlalchemy sort query.
        """
        if sort is None:
            return []
        query = []
        for order in sort.orders:
            attr = getattr(self._model, order.key)
            order_by = attr.asc() if order.direction.is_ascending() else attr.desc()
            query.append(order_by)
        return query
