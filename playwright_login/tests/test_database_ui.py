from playwright.sync_api import Browser

from config.settings import Env, get_env
from database.classifica import fetch_main_ranking
from database.giocatori import fetch_user_profile
from database.mesi import fetch_monthly_ranking
from pages.login_page import LoginPage

USERNAME = get_env(Env.USERNAME, "testuser@example.com")
PASSWORD = get_env(Env.PASSWORD, "testpass")


def _normalise_name(name: str) -> str:
    return " ".join(name.strip().upper().split())


def _numeric(value: str) -> int | float:
    parsed = float(value.replace(",", "."))
    return int(parsed) if parsed.is_integer() else parsed


# Verify that the main ranking UI matches the database.
def test_main_ranking_matches_database(browser: Browser, db_connection):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()

    ui_rows = login_page.ranking_rows()
    database_rows = fetch_main_ranking(db_connection)

    assert {_normalise_name(name) for name in ui_rows} == set(database_rows)
    for name, expected in database_rows.items():
        values = ui_rows[next(ui_name for ui_name in ui_rows if _normalise_name(ui_name) == name)]
        assert [_numeric(value) for value in values[:4]] == [
            expected["partite"],
            expected["primo"],
            expected["secondo"],
            expected["terzo"],
        ]
        assert _numeric(values[4]) == sum(
            expected[field] for field in ("primo", "secondo", "terzo")
        )
    page.close()


# Verify that the monthly ranking UI matches the database.
def test_monthly_ranking_matches_database(browser: Browser, db_connection):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.open_monthly_ranking()

    ui_rows = login_page.ranking_rows(login_page.monthly_ranking_table)
    database_rows = fetch_monthly_ranking(db_connection)

    assert {_normalise_name(name) for name in ui_rows} == set(database_rows)
    for name, expected_points in database_rows.items():
        ui_name = next(ui_name for ui_name in ui_rows if _normalise_name(ui_name) == name)
        actual_points = [_numeric(value) for value in ui_rows[ui_name]]
        assert actual_points == expected_points
    page.close()


# Verify that the logged-in user's profile matches the database.
def test_user_profile_matches_database(browser: Browser, db_connection):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(USERNAME, PASSWORD)
    login_page.open_profile()

    database_profile = fetch_user_profile(db_connection, USERNAME)
    assert database_profile is not None, f"No database profile found for {USERNAME}"

    ui_profile = login_page.profile_details()
    expected_profile = {
        "name": database_profile["nome"],
        "surname": database_profile["soprannome"],
        "email": database_profile["email"],
    }
    assert {
        field: value.strip().casefold() for field, value in ui_profile.items()
    } == {
        field: value.strip().casefold() for field, value in expected_profile.items()
    }
    page.close()