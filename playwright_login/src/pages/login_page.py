from playwright.sync_api import Page


class LoginPage:
    URL = "https://dart-blu.onrender.com/login"

    def __init__(self, page: Page):
        self.page = page
        self.open_login_button = page.locator("#btnLogin")
        self.email_input = page.locator("#loginEmail")
        self.password_input = page.locator("#loginPassword")
        self.submit_button = page.locator("#loginButton")
        self.greeting = page.locator("span.user-greeting")

    def open(self) -> None:
        self.page.goto(self.URL, wait_until="networkidle")

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