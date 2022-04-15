import pytest

from fastapi_starterkit.web.dependencies import pageable_parameters, sort_parameters


@pytest.mark.asyncio
async def test_pageable_parameters():
    page_request = await pageable_parameters(0, 10)
    assert page_request.page == 0
    assert page_request.size == 10


@pytest.mark.asyncio
async def test_sort_parameters():
    sort = await sort_parameters(None)
    assert sort is None

    sort = await sort_parameters("id")
    assert len(sort.orders) == 1
    assert sort.orders[0].key == "id"
    assert sort.orders[0].direction.is_ascending()

    sort = await sort_parameters("id,value.des")
    assert len(sort.orders) == 2
    assert sort.orders[0].key == "id"
    assert sort.orders[0].direction.is_ascending()
    assert sort.orders[1].key == "value"
    assert sort.orders[1].direction.is_descending()
