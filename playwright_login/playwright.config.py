from playwright.sync_api import Playwright, sync_playwright

from config.settings import Env, get_bool, get_int

# Playwright configuration for pytest-playwright or custom runners
PROJECT_ROOT = "./"


def get_browser_args():
    return {
        "headless": get_bool(Env.HEADLESS, True),
        "timeout": get_int(Env.TIMEOUT, 30000),
    }


def launch_browser():
    p = sync_playwright().start()
    browser = p.chromium.launch(**get_browser_args())
    return p, browser
