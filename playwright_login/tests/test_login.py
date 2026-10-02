from playwright.sync_api import Browser

from config.settings import Env, get_env
from data.users import DEFAULT_USER, INVALID_USER
from pages.login_page import LoginPage

USERNAME = get_env(Env.USERNAME, DEFAULT_USER["username"])
PASSWORD = get_env(Env.PASSWORD, DEFAULT_USER["password"])
DISPLAY_NAME = get_env(Env.DISPLAY_NAME, DEFAULT_USER["display_name"])
DISPLAY_SURNAME = get_env(Env.DISPLAY_SURNAME, DEFAULT_USER["display_surname"])


# Verify that valid credentials log the user in and show the expected greeting.
def test_login(browser: Browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(USERNAME, PASSWORD)

    assert login_page.greeting_text() == f"Benvenuto {DISPLAY_NAME}"
    page.close()


# Verify that invalid credentials display an error message.
def test_login_with_invalid_credentials_shows_error(browser: Browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(INVALID_USER["username"], INVALID_USER["password"])

    assert "Credenziali non valide" in login_page.invalid_credentials_error()
    page.close()


# Verify that the login form displays its required controls.
def test_login_form_is_visible(browser: Browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.open_login_form()

    assert login_page.email_input.is_visible()
    assert login_page.password_input.is_visible()
    assert login_page.submit_button.is_visible()
    page.close()


# Verify that the profile popup displays the expected user details.
def test_user_profile_shows_correct_details(browser: Browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(USERNAME, PASSWORD)
    login_page.open_profile()

    assert login_page.profile_details() == {
        "name": DISPLAY_NAME,
        "surname": DISPLAY_SURNAME,
        "email": USERNAME.upper(),
    }
    page.close()