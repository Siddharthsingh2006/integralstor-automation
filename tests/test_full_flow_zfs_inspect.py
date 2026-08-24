from pathlib import Path

from pages.login_page import LoginPage


def test_inspect_zfs_pool_in_logged_in_flow(page, settings, credentials):
    # -------------------------------------------------
    # 1. Open IntegralStor
    # -------------------------------------------------
    login = LoginPage(page)

    login.open(settings["base_url"])

    assert login.is_login_page_visible()

    # -------------------------------------------------
    # 2. LOGIN — ONLY ONCE
    # -------------------------------------------------
    login.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")

    # -------------------------------------------------
    # 3. Open ZFS Pools
    # Same authenticated browser session
    # -------------------------------------------------
    page.goto(settings["base_url"] + "/view_zfs_pools/")
    page.wait_for_load_state("networkidle")

    assert "ZFS pools" in page.locator("body").inner_text()

    # -------------------------------------------------
    # 4. Open Create ZFS Pool
    # -------------------------------------------------
    page.goto(settings["base_url"] + "/create_zfs_pool")
    page.wait_for_load_state("networkidle")

    Path("logs/create_zfs_pool_browser.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    print("\nURL:", page.url)
    print("\nTITLE:", page.title())

    # -------------------------------------------------
    # 5. Forms
    # -------------------------------------------------
    print("\nFORMS:")

    for form in page.locator("form").all():
        print(
            "action=",
            form.get_attribute("action"),
            "method=",
            form.get_attribute("method"),
        )

    # -------------------------------------------------
    # 6. Inputs
    # -------------------------------------------------
    print("\nINPUTS:")

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

    # -------------------------------------------------
    # 7. Selects
    # -------------------------------------------------
    print("\nSELECTS:")

    for element in page.locator("select").all():
        print(
            "name=",
            element.get_attribute("name"),
            "id=",
            element.get_attribute("id"),
        )

        for option in element.locator("option").all():
            print(
                "  option value=",
                option.get_attribute("value"),
                "text=",
                repr(option.inner_text()),
            )

    # -------------------------------------------------
    # 8. Buttons
    # -------------------------------------------------
    print("\nBUTTONS:")

    for element in page.locator(
        "button, input[type=submit], input[type=button]"
    ).all():
        tag = element.evaluate("(el) => el.tagName")

        text = ""
        if tag != "INPUT":
            text = element.inner_text()

        print(
            "text=",
            repr(text),
            "name=",
            element.get_attribute("name"),
            "value=",
            element.get_attribute("value"),
            "type=",
            element.get_attribute("type"),
        )

    # -------------------------------------------------
    # 9. Save visible page text
    # -------------------------------------------------
    Path("logs/create_zfs_pool_browser.txt").write_text(
        page.locator("body").inner_text(),
        encoding="utf-8",
    )

    print("\nBODY:")
    print(page.locator("body").inner_text())

    assert "Create" in page.locator("body").inner_text()
