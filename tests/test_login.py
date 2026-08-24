from pages.login_page import LoginPage


def test_successful_login(page, settings, credentials):
    login_page = LoginPage(page)

    login_page.open(settings["base_url"])

    assert login_page.is_login_page_visible()

    login_page.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")


    assert page.url != settings["base_url"] + "/"
