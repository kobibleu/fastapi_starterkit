from typing import Optional

from fastapi import Query

from fastapi_starterkit.data.domain.pageable import PageRequest
from fastapi_starterkit.data.domain.sort import Sort, Direction, Order


async def pageable_parameters(
        page: int = Query(default=0, description="Page index, must not be negative.", ge=0),
        size: int = Query(default=20, description="The size of the page to be returned, must be greater than 0.", gt=0)
) -> PageRequest:
    return PageRequest(page=page, size=size)


async def sort_parameters(
        sort: Optional[str] = Query(None, description="Sort option.", example="id.asc,value.des")
) -> Optional[Sort]:
    if sort is None:
        return None
    # format is id.asc,value.des unless we can handle multiple sort query param
    orders = []
    for order_param in sort.split(","):
        split = order_param.split(".")
        direction = Direction.value_of(split[1]) if len(split) > 1 else Direction.ASC
        orders.append(Order(key=split[0], direction=direction))
    return Sort(orders=orders)
