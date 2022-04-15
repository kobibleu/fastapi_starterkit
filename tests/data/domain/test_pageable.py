import pytest
from pydantic import ValidationError

from fastapi_starterkit.data.domain.pageable import PageRequest, Page


def test_page_request_validation():
    with pytest.raises(ValidationError):
        PageRequest(page=-1, size=1)

    with pytest.raises(ValidationError):
        PageRequest(page=0, size=0)


def test_page_request_of_size():
    page_request = PageRequest.of_size(10)
    assert page_request.size == 10
    assert page_request.page == 0


def test_page_request_offset():
    page_request = PageRequest(page=3, size=10)
    assert page_request.offset() == 30


def test_page_request_first():
    page_request = PageRequest(page=3, size=10).first()
    assert page_request.page == 0
    assert page_request.size == 10


def test_page_request_next():
    page_request = PageRequest(page=3, size=10).next()
    assert page_request.page == 4
    assert page_request.size == 10


def test_page_request_previous():
    page_request = PageRequest(page=3, size=10).previous()
    assert page_request.page == 2
    assert page_request.size == 10

    page_request = PageRequest(page=0, size=10).previous()
    assert page_request.page == 0
    assert page_request.size == 10


def test_page_request_has_previous():
    page_request = PageRequest(page=3, size=10)
    assert page_request.has_previous()

    page_request = PageRequest(page=0, size=10)
    assert not page_request.has_previous()


def test_page_number():
    page = Page(content=[1, 2, 3], page_request=PageRequest(page=1, size=10), total_elements=13)
    assert page.number() == 1

    page = Page(content=[1, 2, 3])
    assert page.number() == 0


def test_page_size():
    page = Page(content=[1, 2, 3], page_request=PageRequest(page=1, size=10), total_elements=13)
    assert page.size() == 10

    page = Page(content=[1, 2, 3])
    assert page.size() == 3


def test_page_number_of_elements():
    page = Page(content=[1, 2, 3], page_request=PageRequest(page=1, size=10), total_elements=13)
    assert page.number_of_elements() == 3


def test_page_total_pages():
    page = Page(content=[1, 2, 3], page_request=PageRequest(page=1, size=10), total_elements=13)
    assert page.total_pages() == 2

    page = Page(content=[1, 2, 3])
    assert page.total_pages() == 1

    page = Page(content=[])
    assert page.total_pages() == 1


def test_page_has_content():
    page = Page(content=[1, 2, 3], page_request=PageRequest(page=1, size=10), total_elements=13)
    assert page.has_content()

    page = Page(content=[])
    assert not page.has_content()


def test_page_has_next():
    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=1, size=5), total_elements=25)
    assert page.has_next()

    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=5, size=5), total_elements=25)
    assert not page.has_next()

    page = Page(content=[])
    assert not page.has_next()


def test_page_has_previous():
    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=1, size=5), total_elements=25)
    assert page.has_previous()

    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=0, size=5), total_elements=25)
    assert not page.has_previous()

    page = Page(content=[])
    assert not page.has_previous()


def test_page_is_first():
    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=1, size=5), total_elements=25)
    assert not page.is_first()

    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=0, size=5), total_elements=25)
    assert page.is_first()

    page = Page(content=[])
    assert page.is_first()


def test_page_is_last():
    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=1, size=5), total_elements=25)
    assert not page.is_last()

    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=5, size=5), total_elements=25)
    assert page.is_last()

    page = Page(content=[])
    assert page.is_last()


def test_page_next_page_request():
    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=1, size=5), total_elements=25)
    assert page.next_page_request().page == 2

    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=5, size=5), total_elements=25)
    assert page.next_page_request() is None

    page = Page(content=[])
    assert page.next_page_request() is None


def test_page_previous_page_request():
    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=1, size=5), total_elements=25)
    assert page.previous_page_request().page == 0

    page = Page(content=[1, 2, 3, 4, 5], page_request=PageRequest(page=0, size=5), total_elements=25)
    assert page.previous_page_request() is None

    page = Page(content=[])
    assert page.previous_page_request() is None
