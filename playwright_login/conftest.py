import pytest

from config.settings import Env, get_bool
from fixtures.browser import browser  # noqa: F401


def pytest_addoption(parser):
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run Playwright with a visible browser window.",
    )


# Keep the fixture available through pytest's fixture discovery while centralizing
# the browser lifecycle in the fixtures package.
