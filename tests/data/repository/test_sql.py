import pytest

from fastapi_starterkit.data.domain.pageable import PageRequest
from fastapi_starterkit.data.domain.sort import Sort, Direction
from tests.conftest import TestModel


@pytest.mark.asyncio
async def test_count(repo, persist_models):
    assert await repo.count() == 3


@pytest.mark.asyncio
async def test_delete_all(repo, persist_models):
    await repo.delete_all()
    assert await repo.count() == 0


@pytest.mark.asyncio
async def test_delete_all_by_id(repo, persist_models):
    await repo.delete_all_by_id((1, 2))
    assert await repo.count() == 1


@pytest.mark.asyncio
async def test_delete_by_id(repo, persist_models):
    await repo.delete_by_id(1)
    assert await repo.count() == 2


@pytest.mark.asyncio
async def test_exists_by_id(repo, persist_models):
    assert await repo.exists_by_id(1)
    assert not await repo.exists_by_id(4)


@pytest.mark.asyncio
async def test_find_all(repo, persist_models):
    assert len(await repo.find_all()) == 3

    res = await repo.find_all(sort=Sort.by("value", direction=Direction.DES))
    assert [r.value for r in res] == ["value 3", "value 2", "value 1"]


@pytest.mark.asyncio
async def test_find_page(repo, persist_models):
    res = await repo.find_page(PageRequest.of_size(2))
    assert len(res.content) == 2
    assert res.total_elements == 3


@pytest.mark.asyncio
async def test_find_all_by_id(repo, persist_models):
    assert len(await repo.find_all_by_id([1, 2])) == 2


@pytest.mark.asyncio
async def test_find_by_id(repo, persist_models):
    assert (await repo.find_by_id(1)).value == "value 1"
    assert await repo.find_by_id(4) is None


@pytest.mark.asyncio
async def test_save_unexpected_type(repo):
    with pytest.raises(ValueError):
        await repo.save(1)


@pytest.mark.asyncio
async def test_save(repo):
    res = await repo.save(TestModel(value="value 1"))
    assert res.id == 1
    assert res.value == "value 1"
    assert len(await repo.find_all()) == 1

    res.value = "value 2"
    res = await repo.save(res)
    assert res.value == "value 2"
    assert len(await repo.find_all()) == 1

    res = await repo.save(TestModel(value="value 3"))
    assert res.id == 2
    assert res.value == "value 3"
    assert len(await repo.find_all()) == 2


@pytest.mark.asyncio
async def test_save_all(repo, persist_models):
    model = await repo.find_by_id(1)
    model.value = "value 4"
    res = await repo.save_all([
        model,
        TestModel(value="value 5")
    ])
    assert len(res) == 2
    assert len(await repo.find_all()) == 4
