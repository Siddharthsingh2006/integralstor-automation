from pathlib import Path

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.disks_page import DisksPage


def test_integralstor_full_flow(page, settings, credentials):
    # ============================================================
    # 1. Open IntegralStor
    # ============================================================

    login_page = LoginPage(page)
    login_page.open(settings["base_url"])

    assert login_page.is_login_page_visible()

    # ============================================================
    # 2. LOGIN — ONLY ONCE
    # ============================================================

    login_page.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")

    # ============================================================
    # 3. Dashboard
    # ============================================================

    dashboard = DashboardPage(page)

    assert dashboard.is_dashboard_visible()

    Path("logs/full_dashboard.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # ============================================================
    # 4. Scroll Dashboard from top → bottom
    # ============================================================

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)

    page.evaluate(
        """
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth"
        });
        """
    )

    page.wait_for_timeout(2000)

    Path("logs/full_dashboard_bottom.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # Return to top before moving to the next feature.
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)

    # ============================================================
    # 5. Disks and storage pools
    # ============================================================

    disks = DisksPage(page)

    # ------------------------------------------------------------
    # 5a. ZFS Pools
    # ------------------------------------------------------------

    disks.open(settings["base_url"])

    assert disks.is_zfs_pools_page()

    Path("logs/full_zfs_pools.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # ------------------------------------------------------------
    # 5b. Data Disks
    # ------------------------------------------------------------

    disks.open_data_disks(settings["base_url"])

    assert disks.is_data_disks_page()
    assert disks.is_rotating_data_disks_section_visible()
    assert disks.is_flash_data_disks_section_visible()
    assert disks.has_data_disk_rows()
    assert disks.is_smart_status_visible()

    Path("logs/full_data_disks.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # ------------------------------------------------------------
    # 5c. OS Disks
    # ------------------------------------------------------------

    disks.open_os_disks(settings["base_url"])

    assert disks.is_os_disks_page()

    Path("logs/full_os_disks.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # ============================================================
    # END
    # ============================================================
