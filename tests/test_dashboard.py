from pathlib import Path

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


def test_dashboard_after_login(page, settings, credentials):
    login_page = LoginPage(page)

    # Open IntegralStor.
    login_page.open(settings["base_url"])

    assert login_page.is_login_page_visible()

    # LOGIN ONLY ONCE.
    login_page.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")

    dashboard = DashboardPage(page)

    # Verify IntegralStor Dashboard.
    assert dashboard.is_dashboard_visible()

    # Save dashboard HTML.
    Path("logs/dashboard.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # Verify Netdata iframe.
    assert dashboard.is_netdata_visible()

    # Scroll the ACTUAL Netdata dashboard
    # from top to bottom.
    dashboard.scroll_netdata_top_to_bottom()
