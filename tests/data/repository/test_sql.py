import pytest

from fastapi_starterkit.data.domain.pageable import PageRequest
from fastapi_starterkit.data.domain.sort import Sort, Direction
from tests.conftest import TestModel


@pytest.mark.asyncio
async def test_count(repo, persist_models, session):
    assert await repo.count(session) == 3


@pytest.mark.asyncio
async def test_delete_all(repo, persist_models, session):
    await repo.delete_all(session)
    assert await repo.count(session) == 0


@pytest.mark.asyncio
async def test_delete_all_by_id(repo, persist_models, session):
    await repo.delete_all_by_id(session, (1, 2))
    assert await repo.count(session) == 1


@pytest.mark.asyncio
async def test_delete_by_id(repo, persist_models, session):
    await repo.delete_by_id(session, 1)
    assert await repo.count(session) == 2


@pytest.mark.asyncio
async def test_exists_by_id(repo, persist_models, session):
    assert await repo.exists_by_id(session, 1)
    assert not await repo.exists_by_id(session, 4)


@pytest.mark.asyncio
async def test_find_all(repo, persist_models, session):
    assert len(await repo.find_all(session)) == 3

    res = await repo.find_all(session, sort=Sort.by("value", direction=Direction.DES))
    assert [r.value for r in res] == ["value 3", "value 2", "value 1"]


@pytest.mark.asyncio
async def test_find_page(repo, persist_models, session):
    res = await repo.find_page(session, PageRequest.of_size(2))
    assert len(res.content) == 2
    assert res.total_elements == 3


@pytest.mark.asyncio
async def test_find_all_by_id(repo, persist_models, session):
    assert len(await repo.find_all_by_id(session, [1, 2])) == 2


@pytest.mark.asyncio
async def test_find_by_id(repo, persist_models, session):
    assert (await repo.find_by_id(session, 1)).value == "value 1"
    assert await repo.find_by_id(session, 4) is None


@pytest.mark.asyncio
async def test_save_unexpected_type(repo, session):
    with pytest.raises(ValueError):
        await repo.save(session, 1)


@pytest.mark.asyncio
async def test_save(repo, session):
    res = await repo.save(session, TestModel(value="value 1"))
    assert res.id == 1
    assert res.value == "value 1"
    assert len(await repo.find_all(session)) == 1

    res.value = "value 2"
    res = await repo.save(session, res)
    assert res.value == "value 2"
    assert len(await repo.find_all(session)) == 1

    res = await repo.save(session, TestModel(value="value 3"))
    assert res.id == 2
    assert res.value == "value 3"
    assert len(await repo.find_all(session)) == 2


@pytest.mark.asyncio
async def test_save_all(repo, persist_models, session):
    model = await repo.find_by_id(session, 1)
    model.value = "value 4"
    res = await repo.save_all(session, [
        model,
        TestModel(value="value 5")
    ])
    assert len(res) == 2
    assert len(await repo.find_all(session)) == 4
