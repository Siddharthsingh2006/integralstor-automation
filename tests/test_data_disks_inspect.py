from pathlib import Path

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.disks_page import DisksPage


def test_inspect_data_disks(page, settings, credentials):
    # Open IntegralStor
    login = LoginPage(page)
    login.open(settings["base_url"])

    assert login.is_login_page_visible()

    # LOGIN — ONLY ONCE
    login.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")

    # Dashboard
    dashboard = DashboardPage(page)
    assert dashboard.is_dashboard_visible()

    # Disks and storage pools
    disks = DisksPage(page)

    # Data Disks
    disks.open_data_disks(settings["base_url"])
    page.wait_for_load_state("networkidle")

    Path("logs/data_disks_browser.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    print("\nURL:", page.url)
    print("\nTITLE:", page.title())

    print("\n--- CHECKBOXES ---")

    for element in page.locator("input[type=checkbox]").all():
        print(
            "name=",
            element.get_attribute("name"),
            "id=",
            element.get_attribute("id"),
            "value=",
            element.get_attribute("value"),
            "checked=",
            element.is_checked(),
        )

    print("\n--- INPUTS ---")

    for element in page.locator("input").all():
        print(
            "name=",
            element.get_attribute("name"),
            "id=",
            element.get_attribute("id"),
            "type=",
            element.get_attribute("type"),
            "value=",
            element.get_attribute("value"),
        )

    print("\n--- TABLES ---")

    for table in page.locator("table").all():
        print("\nTABLE:")
        print(table.inner_text())

    print("\n--- LINKS ---")

    for link in page.locator("a").all():
        text = link.inner_text().strip()
        href = link.get_attribute("href")

        print(
            "TEXT=",
            repr(text),
            "HREF=",
            href,
        )

    print("\n--- BODY ---")
    print(page.locator("body").inner_text())
