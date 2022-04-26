from typing import Optional

import pytest
from mongomock_motor import AsyncMongoMockClient

from fastapi_starterkit.data.domain.document import Document, ObjectId
from fastapi_starterkit.data.domain.pageable import PageRequest
from fastapi_starterkit.data.domain.sort import Sort, Direction
from fastapi_starterkit.data.repository.mongo import MongoRepository


class TestDocument(Document):
    id: Optional[ObjectId]
    value: str


class TestMongoRepository(MongoRepository[TestDocument]):
    pass


@pytest.fixture
def collection():
    db = AsyncMongoMockClient()["tests"]
    yield db["tests"]


@pytest.fixture
async def mongo_repository(collection):
    repo = TestMongoRepository(collection)
    yield repo


@pytest.mark.asyncio
async def test_count(collection, mongo_repository):
    await load_data(collection)
    assert await mongo_repository.count() == 3


@pytest.mark.asyncio
async def test_delete_all(collection, mongo_repository):
    await load_data(collection)
    await mongo_repository.delete_all()
    assert await mongo_repository.count() == 0


@pytest.mark.asyncio
async def test_delete_all_by_id(collection, mongo_repository):
    object_ids = await load_data(collection)
    await mongo_repository.delete_all_by_id(object_ids[0:2])
    assert await mongo_repository.count() == 1


@pytest.mark.asyncio
async def test_delete_by_id(collection, mongo_repository):
    object_ids = await load_data(collection)
    await mongo_repository.delete_by_id(object_ids[0])
    assert await mongo_repository.count() == 2


@pytest.mark.asyncio
async def test_exists_by_id(collection, mongo_repository):
    object_ids = await load_data(collection)
    assert await mongo_repository.exists_by_id(object_ids[0])
    assert not await mongo_repository.exists_by_id(ObjectId())


@pytest.mark.asyncio
async def test_find_all(collection, mongo_repository):
    await load_data(collection)
    assert len(await mongo_repository.find_all()) == 3

    res = await mongo_repository.find_all(sort=Sort.by("value", direction=Direction.DES))
    assert [r.value for r in res] == ["value 3", "value 2", "value 1"]


@pytest.mark.asyncio
async def test_find_page(collection, mongo_repository):
    await load_data(collection)
    res = await mongo_repository.find_page(PageRequest.of_size(2))
    assert len(res.content) == 2
    assert res.total_elements == 3


@pytest.mark.asyncio
async def test_find_all_by_id(collection, mongo_repository):
    object_ids = await load_data(collection)
    assert len(await mongo_repository.find_all_by_id(object_ids[0:2])) == 2


@pytest.mark.asyncio
async def test_find_by_id(collection, mongo_repository):
    object_ids = await load_data(collection)
    assert (await mongo_repository.find_by_id(object_ids[0])).value == "value 1"
    assert await mongo_repository.find_by_id(ObjectId()) is None


@pytest.mark.asyncio
async def test_save_unexpected_type(mongo_repository):
    with pytest.raises(ValueError):
        await mongo_repository.save(1)


@pytest.mark.asyncio
async def test_save(mongo_repository):
    res = await mongo_repository.save(TestDocument(value="value 1"))
    assert res.id
    assert res.value == "value 1"
    assert len(await mongo_repository.find_all()) == 1

    res.value = "value 2"
    res = await mongo_repository.save(res)
    assert res.value == "value 2"
    assert len(await mongo_repository.find_all()) == 1


@pytest.mark.asyncio
async def test_save_all(mongo_repository):
    res = await mongo_repository.save_all([
        TestDocument(value="value 1"),
        TestDocument(value="value 2"),
        TestDocument(value="value 3")
    ])
    assert len(res) == 3
    assert len(await mongo_repository.find_all()) == 3


async def load_data(collection):
    return [
        (await collection.insert_one({"value": "value 1"})).inserted_id,
        (await collection.insert_one({"value": "value 2"})).inserted_id,
        (await collection.insert_one({"value": "value 3"})).inserted_id
    ]
