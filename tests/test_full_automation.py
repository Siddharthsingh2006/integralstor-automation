from pathlib import Path

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.disks_page import DisksPage


def test_full_integralstor_automation(page, settings, credentials):

    # ============================================================
    # 1. OPEN INTEGRALSTOR
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
    # 3. DASHBOARD
    # ============================================================

    dashboard = DashboardPage(page)

    assert dashboard.is_dashboard_visible()

    Path("logs/full_dashboard.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # ============================================================
    # 4. NETDATA — TOP TO BOTTOM
    # ============================================================

    assert dashboard.is_netdata_visible()

    dashboard.scroll_netdata_top_to_bottom(
        step=900,
        pause_ms=150,
    )

    # ============================================================
    # 5. DISKS AND STORAGE POOLS
    # ============================================================

    disks = DisksPage(page)

    # ------------------------------------------------------------
    # ZFS Pools
    # ------------------------------------------------------------

    disks.open(settings["base_url"])

    assert disks.is_zfs_pools_page()

    Path("logs/full_zfs_pools.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # ------------------------------------------------------------
    # Data Disks
    # ------------------------------------------------------------

    disks.open_data_disks(settings["base_url"])

    assert disks.is_data_disks_page()

    Path("logs/full_data_disks.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # ------------------------------------------------------------
    # OS Disks
    # ------------------------------------------------------------

    disks.open_os_disks(settings["base_url"])

    assert disks.is_os_disks_page()

    Path("logs/full_os_disks.html").write_text(
        page.content(),
        encoding="utf-8",
    )
