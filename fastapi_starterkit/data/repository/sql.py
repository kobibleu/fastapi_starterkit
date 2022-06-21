import asyncio
from typing import TypeVar, Generic, get_args, Iterable, List, Optional, Any

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from fastapi_starterkit.data.domain.entity import Entity
from fastapi_starterkit.data.domain.pageable import PageRequest, Page
from fastapi_starterkit.data.domain.sort import Sort
from fastapi_starterkit.data.repository.core import PagingRepository
from fastapi_starterkit.utils import validate_type_arg

T = TypeVar("T", bound=Entity)


class SqlRepository(Generic[T], PagingRepository):
    """
    SQL repository.

    T: the type of object handled by the repository, must be `fastapi_starterkit.data.domain.entity.Entity`.
    """

    def __init__(self):
        self.model = get_args(self.__orig_bases__[0])[0]
        validate_type_arg(self.model, Entity)

    async def count(self, session: AsyncSession) -> int:
        """
        Returns the number of entities available.
        """
        return await self._count(session, select(self.model))

    async def delete_all(self, session: AsyncSession):
        """
        Deletes all entities.
        """
        await session.execute(delete(self.model))
        await session.commit()

    async def delete_all_by_id(self, session: AsyncSession, ids: Iterable[id]):
        """
        Deletes all entities with the given IDs.
        """
        await session.execute(delete(self.model).where(self.model.id.in_(ids)))
        await session.commit()

    async def delete_by_id(self, session: AsyncSession, id: int):
        """
        Deletes the entity with the given id.
        """
        await session.execute(delete(self.model).where(self.model.id == id))
        await session.commit()

    async def exists_by_id(self, session: AsyncSession, id: int) -> bool:
        """
        Returns whether an entity with the given id exists.
        """
        return (await self._count(session, select(self.model).where(self.model.id == id))) > 0

    async def find_all(self, session: AsyncSession, sort: Sort = None) -> List[T]:
        """
        Returns all entities sorted by the given options.
        """
        return await self._all(session, select(self.model), sort)

    async def find_page(self, session: AsyncSession, page_request: PageRequest, sort: Sort = None) -> Page[T]:
        """
        Returns a Page of entities meeting the paging restriction.
        """
        return await self._page(session, select(self.model), page_request)

    async def find_all_by_id(self, session: AsyncSession, ids: Iterable[id]) -> List[T]:
        """
        Returns all entities with the given IDs.
        """
        return await self._all(session, select(self.model).where(self.model.id.in_(ids)))

    async def find_by_id(self, session: AsyncSession, id: id) -> Optional[T]:
        """
        Returns an entity by its id.
        """
        return await self._get(session, id)

    async def save(self, session: AsyncSession, model: T) -> T:
        """
        Saves a given entity.
        """
        if not isinstance(model, Entity):
            raise ValueError(f"type {type(model)} not handled by repository.")
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

    async def save_all(self, session: AsyncSession, models: Iterable[T]) -> List[T]:
        """
        Saves all given entities.
        """
        if any(not isinstance(m, Entity) for m in models):
            raise ValueError(f"one of type in the list of model is not handled by repository.")
        session.add_all(models)
        await session.commit()
        await asyncio.gather(*[session.refresh(m) for m in models])
        return list(models)

    async def _get(self, session: AsyncSession, pk: Any) -> Optional[T]:
        return await session.get(self.model, pk)

    async def _scalar(self, session: AsyncSession, stmt: Select) -> Any:
        return (await session.execute(stmt)).scalar()

    async def _all(self, session: AsyncSession, stmt: Select, sort: Sort = None) -> List[T]:
        stmt = self._apply_order_by(stmt, sort)
        return (await session.execute(stmt)).unique().scalars().all()

    async def _first(self, session: AsyncSession, stmt: Select) -> Optional[T]:
        return (await session.execute(stmt)).unique().scalars().first()

    async def _one(self, session: AsyncSession, stmt: Select) -> T:
        return (await session.execute(stmt)).unique().scalars().one()

    async def _one_or_none(self, session: AsyncSession, stmt: Select) -> Optional[T]:
        return (await session.execute(stmt)).unique().scalars().one_or_none()

    async def _count(self, session: AsyncSession, stmt: Select) -> int:
        count_query = stmt.with_only_columns(func.count(self.model.id))
        return (await session.execute(count_query)).scalar()

    async def _page(
            self, session: AsyncSession, stmt: Select, page_request: PageRequest, sort: Optional[Sort] = None
    ) -> Page[T]:
        stmt = self._apply_order_by(stmt, sort)
        count = await self._count(session, stmt.offset(None).limit(None))
        all = await self._all(session, stmt.offset(page_request.offset()).limit(page_request.size))
        return Page(content=all, page_request=page_request, total_elements=count)

    def _apply_order_by(self, stmt: Select, sort: Optional[Sort]) -> Select:
        """
        Returns a new selectable with the given list of ORDER BY criteria applied.
        """
        if sort is None:
            return stmt
        clauses = []
        for order in sort.orders:
            attr = getattr(self.model, order.key)
            clauses.append(attr.asc() if order.direction.is_ascending() else attr.desc())
        return stmt.order_by(*clauses)
