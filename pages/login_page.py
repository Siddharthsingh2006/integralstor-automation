from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        self.username = page.locator("#id_username")
        self.password = page.locator("#id_password")
        self.login_button = page.locator('button[type="submit"]')

    def open(self, base_url: str):
        self.page.goto(base_url)

    def is_login_page_visible(self) -> bool:
        return (
            self.username.is_visible()
            and self.password.is_visible()
            and self.login_button.is_visible()
        )

    def login(self, username: str, password: str):
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()
