from playwright.sync_api import Browser

from config.settings import Env, get_env
from pages.login_page import LoginPage

USERNAME = get_env(Env.USERNAME, "testuser@example.com")
PASSWORD = get_env(Env.PASSWORD, "testpass")
DISPLAY_NAME = get_env(Env.DISPLAY_NAME, "DAVIDE")


def test_login(browser: Browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(USERNAME, PASSWORD)

    assert login_page.greeting_text() == f"Benvenuto {DISPLAY_NAME}"
    page.close()


def test_login_form_is_visible(browser: Browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.open_login_form()

    assert login_page.email_input.is_visible()
    assert login_page.password_input.is_visible()
    assert login_page.submit_button.is_visible()
    page.close()