from pathlib import Path

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.disks_page import DisksPage


def test_inspect_zfs_pool_links(page, settings, credentials):
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

    # ZFS Pools
    disks = DisksPage(page)
    disks.open(settings["base_url"])
    assert disks.is_zfs_pools_page()

    Path("logs/zfs_pools_browser.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    print("\nURL:", page.url)
    print("\nTITLE:", page.title())

    print("\n--- ALL LINKS ---")

    for link in page.locator("a").all():
        text = link.inner_text().strip()
        href = link.get_attribute("href")

        print(
            "TEXT=",
            repr(text),
            "HREF=",
            href,
        )

    print("\n--- DATASET RELATED LINKS ---")

    for link in page.locator("a").all():
        text = link.inner_text().strip()
        href = link.get_attribute("href")

        combined = f"{text} {href}".lower()

        if "dataset" in combined:
            print(
                "TEXT=",
                repr(text),
                "HREF=",
                href,
            )

    print("\n--- BUTTONS ---")

    for button in page.locator(
        "button, input[type=submit], input[type=button]"
    ).all():
        tag = button.evaluate("(el) => el.tagName")

        print(
            "TAG=",
            tag,
            "TEXT=",
            button.inner_text().strip() if tag != "INPUT" else "",
            "NAME=",
            button.get_attribute("name"),
            "VALUE=",
            button.get_attribute("value"),
            "TYPE=",
            button.get_attribute("type"),
        )

    print("\n--- BODY ---")
    print(page.locator("body").inner_text())
