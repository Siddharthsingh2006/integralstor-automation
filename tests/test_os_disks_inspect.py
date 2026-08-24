from pathlib import Path


def test_inspect_os_disks(page, settings, credentials):
    # Do NOT login here.
    # This test expects the existing authenticated session.

    page.goto(settings["base_url"] + "/view_disks?type=os")
    page.wait_for_load_state("networkidle")

    body = page.locator("body").inner_text()

    print("\nURL:", page.url)
    print("\nTITLE:", page.title())

    print("\n--- TABLES ---")
    for table in page.locator("table").all():
        print("\nTABLE:")
        print(table.inner_text())

    print("\n--- LINKS ---")
    for link in page.locator("a").all():
        print(
            "TEXT=", repr(link.inner_text()),
            "HREF=", link.get_attribute("href"),
        )

    print("\n--- BODY ---")
    print(body)

    Path("logs/os_disks_inspect.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    assert "OS" in body or "System disks" in body
