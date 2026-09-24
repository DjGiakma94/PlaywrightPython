import pytest
from playwright.sync_api import APIRequestContext, sync_playwright


@pytest.fixture
def api_request() -> APIRequestContext:
    with sync_playwright() as playwright:
        request = playwright.request.new_context(
            base_url="https://dart-blu.onrender.com"
        )
        yield request
        request.dispose()