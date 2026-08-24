from pages.login_page import LoginPage


def test_login_page_is_displayed(page, settings):
    login_page = LoginPage(page)

    login_page.open(settings["base_url"])

    assert login_page.is_login_page_visible()
