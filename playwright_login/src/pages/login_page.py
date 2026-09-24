from playwright.sync_api import Locator, Page


class LoginPage:
    URL = "https://dart-blu.onrender.com/login"

    def __init__(self, page: Page):
        self.page = page
        self.open_login_button = page.locator("#btnLogin")
        self.email_input = page.locator("#loginEmail")
        self.password_input = page.locator("#loginPassword")
        self.submit_button = page.locator("#loginButton")
        self.greeting = page.locator("span.user-greeting")
        self.monthly_ranking_button = page.get_by_role(
            "button", name="CLASSIFICA MENSILE"
        )
        self.monthly_ranking_heading = page.locator("h2:visible").filter(
            has_text="Classifica Mensile"
        )
        self.monthly_ranking_table = page.locator("#monthlyBody table:visible").first
        self.visible_ranking_table = page.locator("table:visible").first

    def open(self) -> None:
        self.page.goto(self.URL, wait_until="networkidle")
        self.visible_ranking_table.locator("thead th").filter(
            has_text="GIOCATORE"
        ).wait_for(state="visible")

    def open_login_form(self) -> None:
        self.open_login_button.click()
        self.email_input.wait_for(state="visible")

    def login(self, username: str, password: str) -> None:
        self.open_login_form()
        self.email_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()

    def greeting_text(self) -> str:
        self.greeting.wait_for(state="visible")
        return self.greeting.inner_text().strip()

    def open_monthly_ranking(self) -> None:
        self.monthly_ranking_button.click()
        self.monthly_ranking_heading.wait_for(state="visible")
        self.monthly_ranking_table.wait_for(state="visible")

    def ranking_player_names(self, table: Locator | None = None) -> set[str]:
        ranking_table = table or self.visible_ranking_table
        headers = ranking_table.locator("thead th").all_inner_texts()
        player_column = next(
            index
            for index, header in enumerate(headers)
            if header.strip().upper() == "GIOCATORE"
        )
        return {
            row.locator("td").nth(player_column).inner_text().strip()
            for row in ranking_table.locator("tbody tr").all()
        }

    def ranking_rows(self, table: Locator | None = None) -> dict[str, list[str]]:
        ranking_table = table or self.visible_ranking_table
        headers = ranking_table.locator("thead th").all_inner_texts()
        player_column = next(
            index
            for index, header in enumerate(headers)
            if header.strip().upper() == "GIOCATORE"
        )
        return {
            cells[player_column].strip(): [
                cell.strip()
                for index, cell in enumerate(cells)
                if index not in (0, player_column)
            ]
            for row in ranking_table.locator("tbody tr").all()
            for cells in [row.locator("td").all_inner_texts()]
        }