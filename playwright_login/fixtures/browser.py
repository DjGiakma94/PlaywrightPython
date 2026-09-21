import pytest
from playwright.sync_api import sync_playwright

from config.settings import Env, get_bool


@pytest.fixture(scope="session")
def browser(request):
    with sync_playwright() as p:
        headless = get_bool(Env.HEADLESS, True) and not request.config.getoption("--headed")
        browser = p.chromium.launch(headless=headless)
        yield browser
        browser.close()
