from playwright.sync_api import Browser

from pages.login_page import LoginPage


def test_monthly_ranking_button_is_visible(browser: Browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()

    assert login_page.monthly_ranking_button.is_visible()
    page.close()


def test_monthly_ranking_contains_main_ranking_players(browser: Browser):
    page = browser.new_page()
    login_page = LoginPage(page)
    login_page.open()
    main_ranking_players = login_page.ranking_player_names()

    login_page.open_monthly_ranking()

    monthly_ranking_players = login_page.ranking_player_names()
    assert main_ranking_players <= monthly_ranking_players
    page.close()