import functools
import inspect
from typing import List, Callable

from fastapi import APIRouter, Response, Request

from fastapi_starterkit.data.domain.pageable import Page
from fastapi_starterkit.web.schema import PageSchema


class RestEndpoints:

    def __init__(self, prefix=""):
        self.router = APIRouter(prefix=prefix)
        for endpoint in self.endpoints:
            request = getattr(endpoint, "_request")
            endpoint = functools.partial(endpoint, self)
            self.router.add_api_route(endpoint=endpoint, **request)

    @property
    def endpoints(self) -> List[Callable]:
        return [
            m[1] for m in inspect.getmembers(self.__class__) if inspect.isfunction(m[1]) if hasattr(m[1], "_request")
        ]

    def _paginated(self, page: Page, request: Request, response: Response) -> PageSchema:
        link_header = ""
        request_uri = str(request.url)
        if page.has_next():
            next_page_uri = self._construct_next_page_uri(request_uri, page.number())
            link_header += self._create_link_header(next_page_uri, "next")
        if page.has_previous():
            link_header = self._append_comma_if_necessary(link_header)
            prev_page_uri = self._construct_prev_page_uri(request_uri, page.number())
            link_header += self._create_link_header(prev_page_uri, "prev")
        if not page.is_first():
            link_header = self._append_comma_if_necessary(link_header)
            first_page_uri = self._construct_first_page_uri(request_uri, page.number())
            link_header += self._create_link_header(first_page_uri, "first")
        if not page.is_last() and page.total_pages() > 1:
            link_header = self._append_comma_if_necessary(link_header)
            last_page_uri = self._construct_last_page_uri(request_uri, page.number(), page.total_pages())
            link_header += self._create_link_header(last_page_uri, "last")
        response.headers["Link"] = link_header
        return PageSchema(
            content=page.content,
            page=page.number(),
            page_size=page.size(),
            total_pages=page.total_pages(),
            total_elements=page.total_elements
        )

    @staticmethod
    def _created(model, request: Request, response: Response):
        request_uri = str(request.url)
        response.headers["Location"] = f"{request_uri.rstrip('/')}/{model.id}"
        return model

    @staticmethod
    def _construct_next_page_uri(request_uri: str, page: int) -> str:
        return request_uri.replace(f"page={page}", f"page={page + 1}")

    @staticmethod
    def _construct_prev_page_uri(request_uri, page: int) -> str:
        return request_uri.replace(f"page={page}", f"page={page - 1}")

    @staticmethod
    def _construct_first_page_uri(request_uri, page: int) -> str:
        return request_uri.replace(f"page={page}", "page=0")

    @staticmethod
    def _construct_last_page_uri(request_uri, page: int, total_pages: int) -> str:
        return request_uri.replace(f"page={page}", f"page={total_pages}")

    @staticmethod
    def _append_comma_if_necessary(link_header: str) -> str:
        if len(link_header) > 0:
            link_header += ", "
        return link_header

    @staticmethod
    def _create_link_header(uri: str, rel: str) -> str:
        return f"<{uri}>; rel=\"{rel}\""
