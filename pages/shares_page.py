from playwright.sync_api import Page


class SharesPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, base_url):
        self.page.goto(f"{base_url}/view_cifs_shares/")
        self.page.wait_for_load_state("networkidle")

    def is_shares_page(self):
        return self.page.locator(
            "#shares_menu"
        ).is_visible()

    def is_windows_shares_tab_visible(self):
        return self.page.locator(
            "#view_cifs_shares_tab"
        ).is_visible()

    def is_nfs_exports_tab_visible(self):
        return self.page.locator(
            "#view_nfs_shares_tab"
        ).is_visible()

    def is_iscsi_targets_tab_visible(self):
        return self.page.locator(
            "#view_iscsi_targets_tab"
        ).is_visible()

    def is_rsync_shares_tab_visible(self):
        return self.page.locator(
            "#view_rsync_shares_tab"
        ).is_visible()

    def is_directory_manager_tab_visible(self):
        return self.page.locator(
            "#view_dir_manager_tab"
        ).is_visible()

    def is_afp_exports_tab_visible(self):
        return self.page.locator(
            "#view_afp_shares_tab"
        ).is_visible()

    def is_webdav_exports_tab_visible(self):
        return self.page.locator(
            "#view_webdav_shares_tab"
        ).is_visible()

    def open_nfs_exports(self, base_url):
        self.page.goto(f"{base_url}/view_nfs_shares/")
        self.page.wait_for_load_state("networkidle")

    def open_iscsi_targets(self, base_url):
        self.page.goto(f"{base_url}/view_iscsi_targets/")
        self.page.wait_for_load_state("networkidle")

    def open_rsync_shares(self, base_url):
        self.page.goto(f"{base_url}/view_rsync_shares/")
        self.page.wait_for_load_state("networkidle")

    def open_directory_manager(self, base_url):
        self.page.goto(f"{base_url}/view_dir_manager/")
        self.page.wait_for_load_state("networkidle")

    def open_afp_exports(self, base_url):
        self.page.goto(f"{base_url}/view_afp_shares/")
        self.page.wait_for_load_state("networkidle")

    def open_webdav_exports(self, base_url):
        self.page.goto(f"{base_url}/view_webdav_shares/")
        self.page.wait_for_load_state("networkidle")
