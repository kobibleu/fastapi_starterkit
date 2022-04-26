import asyncio
from typing import Optional, Iterable, List, Tuple, TypeVar, Generic, get_args

import pymongo
from bson import ObjectId
from motor.core import AgnosticCollection

from fastapi_starterkit.data.domain.document import Document
from fastapi_starterkit.data.domain.pageable import Page, PageRequest
from fastapi_starterkit.data.domain.sort import Sort
from fastapi_starterkit.data.repository.core import PagingRepository
from fastapi_starterkit.utils import validate_type_arg

T = TypeVar("T")


class MongoRepository(Generic[T], PagingRepository):
    """
    Mongo repository.

    T: the type of object handled by the repository, must be `fastapi_starterkit.data.domain.document.Document`.
    """

    def __init__(self, collection: AgnosticCollection):
        self.collection = collection
        self.model = get_args(self.__orig_bases__[0])[0]
        validate_type_arg(self.model, Document)

    async def count(self) -> int:
        """
        Returns the number of documents available.
        """
        return await self.collection.estimated_document_count()

    async def delete_all(self):
        """
        Deletes all documents.
        """
        await self.collection.drop()

    async def delete_all_by_id(self, ids: Iterable[ObjectId]):
        """
        Deletes all documents with the given IDs.
        """
        await self.collection.delete_many({"_id": {"$in": ids}})

    async def delete_by_id(self, id: ObjectId):
        """
        Deletes the document with the given id.
        """
        await self.collection.delete_one({"_id": id})

    async def exists_by_id(self, id: ObjectId) -> bool:
        """
        Returns whether a document with the given id exists.
        """
        return bool(await self.collection.count_documents({"_id": id}))

    async def find_all(self, sort: Sort = None) -> List[T]:
        """
        Returns all documents sorted by the given options.
        """
        args = {
            "filter": self._filter_query(),
            "sort": self._sort_query(sort)
        }
        result = await self.collection.find(**args).to_list(None)
        return [self.model.from_mongo(r) for r in result]

    async def find_page(self, page_request: PageRequest, sort: Sort = None) -> Page[T]:
        """
        Returns a Page of document meeting the paging restriction.
        """
        args = {
            "filter": self._filter_query(),
            "sort": self._sort_query(sort),
            "skip": page_request.offset(),
            "limit": page_request.size
        }
        documents = await self.collection.find(**args).to_list(None)
        models = [self.model.from_mongo(doc) for doc in documents]
        count = await self.count()
        return Page(
            content=models,
            page_request=page_request,
            total_elements=count
        )

    async def find_all_by_id(self, ids: Iterable[ObjectId]) -> List[T]:
        """
        Returns all documents with the given IDs.
        """
        result = await self.collection.find(filter={"_id": {"$in": ids}}).to_list(None)
        return [self.model.from_mongo(r) for r in result]

    async def find_by_id(self, id: ObjectId) -> Optional[T]:
        """
        Returns a document by its id.
        """
        document = await self.collection.find_one({"_id": id})
        return self.model.from_mongo(document)

    async def save(self, model: T) -> T:
        """
        Saves a given document.
        """
        if not isinstance(model, Document):
            raise ValueError(f"type {type(model)} not handled by repository.")
        document = model.mongo()
        id = document.get("_id")
        if id is None:
            id = (await self.collection.insert_one(document)).inserted_id
        else:
            await self.collection.replace_one({"_id": id}, document)
        return await self.find_by_id(id)

    async def save_all(self, models: Iterable[T]) -> List[T]:
        """
        Saves all given documents.
        """
        models = await asyncio.gather(*[self.save(m) for m in models])
        return list(models)

    @staticmethod
    def _filter_query(filter: dict = None) -> dict:
        """
        Build mongo filter query.
        """
        if filter is None:
            return {}
        return {}

    @staticmethod
    def _sort_query(sort: Sort) -> List[Tuple[str, int]]:
        """
        Build mongo sort query.
        """
        if sort is None:
            return []
        query = []
        for order in sort.orders:
            direction = pymongo.ASCENDING if order.direction.is_ascending() else pymongo.DESCENDING
            query.append((order.key, direction))
        return query
