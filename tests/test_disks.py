from pathlib import Path

from pages.login_page import LoginPage
from pages.disks_page import DisksPage


def test_disks_and_storage_tabs(page, settings, credentials):
    login_page = LoginPage(page)

    login_page.open(settings["base_url"])

    assert login_page.is_login_page_visible()

    login_page.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")

    disks = DisksPage(page)

    # ZFS pools
    disks.open(settings["base_url"])

    assert disks.is_zfs_pools_page()

    Path("logs/zfs_pools.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # Data disks
    disks.open_data_disks(settings["base_url"])

    assert disks.is_data_disks_page()
    assert disks.is_rotating_data_disks_section_visible()
    assert disks.is_flash_data_disks_section_visible()
    assert disks.has_data_disk_rows()
    assert disks.is_smart_status_visible()
    assert disks.is_disk_replacement_visible()
    assert disks.is_pool_information_visible()

    Path("logs/data_disks.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # OS disks
    disks.open_os_disks(settings["base_url"])

    assert disks.is_os_disks_page()
    assert disks.is_os_disk_information_visible()
    assert disks.has_os_disk_rows()

    Path("logs/os_disks.html").write_text(
        page.content(),
        encoding="utf-8",
    )
