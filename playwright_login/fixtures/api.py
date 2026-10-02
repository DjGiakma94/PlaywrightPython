import pytest
from playwright.sync_api import APIRequestContext, sync_playwright

from config.settings import get_base_url


@pytest.fixture
def api_request() -> APIRequestContext:
    with sync_playwright() as playwright:
        request = playwright.request.new_context(base_url=get_base_url())
        yield request
        request.dispose()