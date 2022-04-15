from fastapi_starterkit.data.domain.sort import Direction, Sort


def test_direction_ascending_check():
    assert Direction.ASC.is_ascending()
    assert not Direction.DES.is_ascending()


def test_direction_descending_check():
    assert Direction.DES.is_descending()
    assert not Direction.DES.is_ascending()


def test_direction_value_of():
    assert Direction.value_of("DES") == Direction.DES
    assert Direction.value_of("ASC") == Direction.ASC
    assert Direction.value_of("des") == Direction.DES
    assert Direction.value_of("asc") == Direction.ASC
    assert Direction.value_of("toto") is None


def test_direction_values():
    assert len(Direction.values()) == 2
    assert Direction.ASC in Direction.values()
    assert Direction.DES in Direction.values()


def test_sort_creation_by_keys():
    sort = Sort.by("key1", "key2")
    assert len(sort.orders) == 2
    assert sort.orders[0].key == "key1" and sort.orders[0].direction == Direction.ASC
    assert sort.orders[1].key == "key2" and sort.orders[1].direction == Direction.ASC


def test_sort_creation_by_direction_and_keys():
    sort = Sort.by("key1", "key2", direction=Direction.DES)
    assert len(sort.orders) == 2
    assert sort.orders[0].key == "key1" and sort.orders[0].direction == Direction.DES
    assert sort.orders[1].key == "key2" and sort.orders[1].direction == Direction.DES


def test_sort_ascending():
    sort = Sort.by("key1", "key2", direction=Direction.DES)
    sort.ascending()
    assert sort.orders[0].direction == Direction.ASC
    assert sort.orders[1].direction == Direction.ASC


def test_sort_descending():
    sort = Sort.by("key1", "key2", direction=Direction.ASC)
    sort.descending()
    assert sort.orders[0].direction == Direction.DES
    assert sort.orders[1].direction == Direction.DES
