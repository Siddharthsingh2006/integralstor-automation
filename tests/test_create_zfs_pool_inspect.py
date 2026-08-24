from pathlib import Path


def test_inspect_create_zfs_pool(page, settings, credentials):
    # -------------------------------------------------
    # ZFS Pools
    # Login is NOT performed here.
    # The session should already be authenticated.
    # -------------------------------------------------
    page.goto(settings["base_url"] + "/view_zfs_pools/")
    page.wait_for_load_state("networkidle")

    assert "ZFS pools" in page.locator("body").inner_text()

    # -------------------------------------------------
    # Open Create ZFS Pool
    # -------------------------------------------------
    page.goto(settings["base_url"] + "/create_zfs_pool")
    page.wait_for_load_state("networkidle")

    Path("logs/create_zfs_pool_browser.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    print("\nURL:", page.url)
    print("\nTITLE:", page.title())

    print("\nFORMS:")
    for form in page.locator("form").all():
        print(
            "action=",
            form.get_attribute("action"),
            "method=",
            form.get_attribute("method"),
        )

    print("\nINPUTS:")
    for element in page.locator("input").all():
        print(
            "name=", element.get_attribute("name"),
            "id=", element.get_attribute("id"),
            "type=", element.get_attribute("type"),
            "value=", element.get_attribute("value"),
        )

    print("\nSELECTS:")
    for element in page.locator("select").all():
        print(
            "name=", element.get_attribute("name"),
            "id=", element.get_attribute("id"),
        )

    print("\nBUTTONS:")
    for element in page.locator("button, input[type=submit]").all():
        tag = element.evaluate("(el) => el.tagName")

        text = ""
        if tag != "INPUT":
            text = element.inner_text()

        print(
            "text=", text,
            "name=", element.get_attribute("name"),
            "value=", element.get_attribute("value"),
            "type=", element.get_attribute("type"),
        )

    assert "Create" in page.locator("body").inner_text()
