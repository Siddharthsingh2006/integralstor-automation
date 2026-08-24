from pathlib import Path

from pages.login_page import LoginPage
from pages.shares_page import SharesPage


def test_shares_page(page, settings, credentials):
    login = LoginPage(page)

    login.open(settings["base_url"])

    assert login.is_login_page_visible()

    login.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")

    shares = SharesPage(page)

    shares.open(settings["base_url"])

    assert shares.is_shares_page()

    Path("logs/shares.html").write_text(
        page.content(),
        encoding="utf-8",
    )
