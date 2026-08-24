from pathlib import Path

from pages.login_page import LoginPage


def test_inspect_create_cifs_share(page, settings, credentials):
    login = LoginPage(page)

    login.open(settings["base_url"])
    assert login.is_login_page_visible()

    login.login(
        credentials["username"],
        credentials["password"],
    )

    page.goto(f'{settings["base_url"]}/create_cifs_share')
    page.wait_for_load_state("domcontentloaded")

    Path("logs/create_cifs_share.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    print("\nURL:", page.url)
    print("\nTITLE:", page.title())
    print("\nFORMS:", page.locator("form").count())
    print("INPUTS:", page.locator("input").count())
    print("SELECTS:", page.locator("select").count())
    print("TEXTAREAS:", page.locator("textarea").count())
    print("BUTTONS:", page.locator("button").count())
