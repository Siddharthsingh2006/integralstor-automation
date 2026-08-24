from pathlib import Path

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.disks_page import DisksPage


def test_integralstor_full_flow(page, settings, credentials):
    # -------------------------------------------------
    # 1. Open IntegralStor
    # -------------------------------------------------
    login = LoginPage(page)

    login.open(settings["base_url"])

    assert login.is_login_page_visible()test_full_flow.py

    # -------------------------------------------------
    # 2. LOGIN — ONLY ONCE
    # -------------------------------------------------
    login.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")

    # -------------------------------------------------
    # 3. Dashboard
    # -------------------------------------------------
    dashboard = DashboardPage(page)

    assert dashboard.is_dashboard_visible()

    Path("logs/dashboard.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # Scroll Netdata dashboard top -> bottom
    dashboard.scroll_netdata_top_to_bottom(
        step=900,
        pause_ms=150,
    )

    # -------------------------------------------------
    # 4. Disks and storage pools
    # -------------------------------------------------
    disks = DisksPage(page)

    # -------------------------------------------------
    # 4.1 ZFS Pools
    # -------------------------------------------------
    disks.open(settings["base_url"])

    assert disks.is_zfs_pools_page()test_full_flow.py

    Path("logs/zfs_pools.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # -------------------------------------------------
    # 4.2 INSPECT CREATE ZFS POOL PAGE
    #
    # IMPORTANT:
    # We are already logged in.
    # Do NOT login again.
    # -------------------------------------------------
    page.goto(settings["base_url"] + "/create_zfs_pool")
    page.wait_for_load_state("networkidle")

    assert "Create" in page.locator("body").inner_text()

    Path("logs/create_zfs_pool_browser.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    print("\nCREATE ZFS POOL URL:", page.url)
    print("\nCREATE ZFS POOL TITLE:", page.title())

    # -------------------------------------------------
    # Inspect forms
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
    # Inspect inputs
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
    # Inspect selects
    # -------------------------------------------------
    print("\nSELECTS:")

    for element in page.locator("select").all():
        print(
            "name=",
            element.get_attribute("name"),
            "id=",
            element.get_attribute("id"),
        )

        options = element.locator("option").all()

        for option in options:
            print(
                "  option:",
                option.inner_text(),
                "value=",
                option.get_attribute("value"),
            )

    # -------------------------------------------------
    # Inspect buttons
    # -------------------------------------------------
    print("\nBUTTONS:")

    for element in page.locator(
        "button, input[type=submit], input[type=button]"
    ).all():

        tag_name = element.evaluate(
            "(el) => el.tagName"
        )

        text = ""

        if tag_name != "INPUT":
            text = element.inner_text()

        print(
            "text=",
            text,
            "name=",
            element.get_attribute("name"),
            "value=",
            element.get_attribute("value"),
            "type=",
            element.get_attribute("type"),
        )

    # -------------------------------------------------
    # Return to ZFS Pools
    # -------------------------------------------------
    disks.open(settings["base_url"])

    assert disks.is_zfs_pools_page()

    # -------------------------------------------------
    # 5. Data Disks
    # -------------------------------------------------
    disks.open_data_disks(settings["base_url"])

    assert disks.is_data_disks_page()
    assert disks.is_rotating_data_disks_section_visible()
    assert disks.is_flash_data_disks_section_visible()
    assert disks.has_data_disk_rows()
    assert disks.is_smart_status_visible()

    Path("logs/data_disks.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # -------------------------------------------------
    # 6. OS Disks
    # -------------------------------------------------
    disks.open_os_disks(settings["base_url"])

    assert disks.is_os_disks_page()

    Path("logs/os_disks.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # -------------------------------------------------
    # 7. System Tunable
    # -------------------------------------------------
    disks.open_system_tunable(settings["base_url"])

    assert disks.is_system_tunable_page()

    Path("logs/system_tunable.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # -------------------------------------------------
    # Verify available templates
    # -------------------------------------------------
    templates = disks.get_system_tunable_templates()

    assert "HDD Sequential" in templates
    assert "HDD Random" in templates
    assert "SSD Sequential" in templates
    assert "SSD Random" in templates

    # -------------------------------------------------
    # Verify template values
    # -------------------------------------------------
    disks.select_system_tunable_template("HDD Sequential")

    assert disks.is_template_values_visible()

    values = disks.get_template_values_text()

    assert "zfs_arc_max" in values
    assert "zfs_vdev_async_write_max_active" in values
    assert "zfs_vdev_sync_read_max_active" in values
    assert "zfs_vdev_max_active" in values
    assert "zfs_prefetch_disable" in values
    assert "zfs_txg_timeout" in values
    assert "zfs_dirty_data_max" in values
    assert "zfs_vdev_aggregation_limit" in values
    assert "zfs_metaslab_lba_weighting_enabled" in values
    assert "zfs_arc_meta_min" in values
