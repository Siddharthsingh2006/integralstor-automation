from pathlib import Path

from pages.login_page import LoginPage
from pages.shares_page import SharesPage


def test_all_shares_tabs(page, settings, credentials):
    # LOGIN ONLY ONCE
    login = LoginPage(page)
    login.open(settings["base_url"])

    assert login.is_login_page_visible()

    login.login(
        credentials["username"],
        credentials["password"],
    )

    page.wait_for_load_state("networkidle")

    shares = SharesPage(page)

    tabs = {
        "windows_shares": "/view_cifs_shares/",
        "nfs_shares": "/view_nfs_shares/",
        "iscsi_targets": "/view_iscsi_targets/",
        "rsync_shares": "/view_rsync_shares/",
        "directory_manager": "/view_dir_manager/",
        "afp_shares": "/view_afp_shares/",
        "webdav_shares": "/view_webdav_shares/",
    }

    for name, path in tabs.items():
        page.goto(f"{settings['base_url']}{path}")
        page.wait_for_load_state("networkidle")

        Path(f"logs/{name}.html").write_text(
            page.content(),
            encoding="utf-8",
        )

        print(f"\n===== {name} =====")
        print(page.title())
        print(page.url)
