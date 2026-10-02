from playwright.sync_api import Locator, Page

from config.settings import get_base_url


class LoginPage:
    URL = f"{get_base_url()}/login"

    def __init__(self, page: Page):
        self.page = page
        self.open_login_button = page.locator("#btnLogin")
        self.open_signup_button = page.locator("#btnSignUp")
        self.email_input = page.locator("#loginEmail")
        self.password_input = page.locator("#loginPassword")
        self.submit_button = page.locator("#loginButton")
        self.greeting = page.locator("span.user-greeting")
        self.error_toast = page.locator("#toastContainer .toast.error")
        self.profile_button = page.locator("#btnProfile")
        self.profile_dialog = page.locator("#profileModal")
        self.profile_heading = self.profile_dialog.get_by_role("heading", name="Profilo Utente")
        self.profile_name = page.locator("#nomeProfilo")
        self.profile_surname = page.locator("#soprannomeProfilo")
        self.profile_email = page.locator("#emailProfilo")
        self.insert_match_button = page.get_by_role("button", name="INSERISCI PARTITA")
        self.primo_select = page.locator("#primo")
        self.secondo_select = page.locator("#secondo")
        self.terzo_select = page.locator("#terzo")
        self.match_participants_input = page.locator("#tuttiGiocatori")
        self.match_submit_button = page.locator("#addMatch")
        self.match_confirmation_dialog = page.locator("#confirmModal")
        self.confirm_match_button = self.match_confirmation_dialog.get_by_role(
            "button", name="Sì, Registra!"
        )
        self.monthly_ranking_button = page.get_by_role(
            "button", name="CLASSIFICA MENSILE"
        )
        self.monthly_ranking_dialog = page.locator("#monthlyModal")
        self.monthly_close_button = self.monthly_ranking_dialog.get_by_role(
            "button", name="Chiudi"
        )
        self.history_button = page.locator("#btnHistory")
        self.history_dialog = page.locator("#historyModal")
        self.history_close_button = self.history_dialog.locator(".btn-cancel")
        self.last_match_button = page.locator("#btnLastMatch")
        self.last_match_dialog = page.locator("#lastMatchModal")
        self.last_match_body = page.locator("#lastMatchBody")
        self.signup_name_input = page.locator("#nome")
        self.signup_surname_input = page.locator("#soprannome")
        self.signup_email_input = page.locator("#signUpEmail")
        self.signup_password_input = page.locator("#signupModal #password")
        self.signup_submit_button = page.locator("#signUpButton")
        self.toast_container = page.locator("#toastContainer")
        self.visible_toast = self.toast_container.locator(".toast").last
        self.monthly_ranking_heading = page.locator("h2:visible").filter(
            has_text="Classifica Mensile"
        )
        self.monthly_ranking_table = page.locator("#monthlyBody table:visible").first
        self.visible_ranking_table = page.locator("table:visible").first
        self.ranking_player_name_cells = page.locator(
            "#content table tbody tr td:nth-child(2)"
        )

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

    def open_profile(self) -> None:
        self.profile_button.click()
        self.profile_heading.wait_for(state="visible")

    def profile_details(self) -> dict[str, str]:
        return {
            "name": self.profile_name.inner_text().strip(),
            "surname": self.profile_surname.inner_text().strip(),
            "email": self.profile_email.inner_text().strip(),
        }

    def invalid_credentials_error(self) -> str:
        self.error_toast.wait_for(state="visible")
        return self.error_toast.inner_text().strip()

    def open_insert_match_form(self) -> None:
        self.insert_match_button.click()
        self.primo_select.wait_for(state="visible")
        self.page.wait_for_function(
            "document.querySelectorAll('#primo option').length > 1"
        )

    def select_match_positions(self, first: str, second: str, third: str) -> None:
        self.primo_select.select_option(value=first)
        self.secondo_select.select_option(value=second)
        self.terzo_select.select_option(value=third)

    def available_match_player_names(self) -> list[str]:
        return [
            option.get_attribute("value")
            for option in self.primo_select.locator("option").all()
            if option.get_attribute("value")
            and option.get_attribute("disabled") is None
        ]

    def set_match_participants(self, names: list[str]) -> None:
        self.match_participants_input.fill("\n".join(names))

    def match_position_values(self) -> list[str]:
        return [
            self.primo_select.input_value(),
            self.secondo_select.input_value(),
            self.terzo_select.input_value(),
        ]

    def session_token(self) -> str | None:
        return self.page.evaluate("localStorage.getItem('dartToken')")

    def submit_match(self) -> str:
        self.match_submit_button.click()
        self.confirm_match_button.click()
        self.visible_toast.wait_for(state="visible")
        return self.visible_toast.inner_text().strip()

    @staticmethod
    def _normalise_name(name: str) -> str:
        return " ".join(name.strip().upper().split())

    def dropdown_option_names(self, select: Locator) -> set[str]:
        return {
            self._normalise_name(option.inner_text().strip())
            for option in select.locator("option").all()
            if option.inner_text().strip()
            and self._normalise_name(option.inner_text().strip()) != "SELEZIONA GIOCATORE"
        }

    def disabled_option_names(self, select: Locator) -> set[str]:
        return {
            self._normalise_name(option.inner_text().strip())
            for option in select.locator("option").all()
            if option.get_attribute("disabled") is not None
            and option.inner_text().strip()
        }

    def open_monthly_ranking(self) -> None:
        self.monthly_ranking_button.click()
        self.monthly_ranking_heading.wait_for(state="visible")
        self.monthly_ranking_table.wait_for(state="visible")

    def close_monthly_ranking(self) -> None:
        self.monthly_close_button.click()

    def monthly_ranking_text(self) -> str:
        return self.monthly_ranking_table.inner_text()

    def open_history(self) -> None:
        self.history_button.click()
        self.history_dialog.wait_for(state="visible")

    def close_history(self) -> None:
        self.history_close_button.click()

    def open_last_match(self) -> None:
        self.last_match_button.click()
        self.last_match_body.wait_for(state="visible")
        self.page.wait_for_function(
            "!document.querySelector('#lastMatchBody').innerText.includes('Caricamento')"
        )

    def last_match_player_names(self) -> set[str]:
        medals = ("🥇", "🥈", "🥉")
        return {
            self._normalise_name(
                next(
                    (text.replace(medal, "") for medal in medals if medal in text),
                    text,
                )
            )
            for paragraph in self.last_match_body.locator("p").all()
            for text in [paragraph.inner_text().strip()]
            if text
        }

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

    def open_signup_form(self) -> None:
        self.open_signup_button.click()
        self.signup_name_input.wait_for(state="visible")

    def sign_up(self, name: str, surname: str, email: str, password: str) -> str:
        self.signup_name_input.fill(name)
        self.signup_surname_input.fill(surname)
        self.signup_email_input.fill(email)
        self.signup_password_input.fill(password)
        self.signup_submit_button.click()
        self.visible_toast.wait_for(state="visible")
        return self.visible_toast.inner_text().strip()

    def sort_ranking_by_player_name(self) -> None:
        self.visible_ranking_table.locator("thead th").filter(
            has_text="Giocatore"
        ).click()

    def ranking_names_in_display_order(self) -> list[str]:
        return [name.strip() for name in self.ranking_player_name_cells.all_inner_texts()]