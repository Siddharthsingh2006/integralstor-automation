class DisksPage:
    def __init__(self, page):
        self.page = page

    def open(self, base_url):
        self.page.goto(f"{base_url}/view_zfs_pools/")
        self.page.wait_for_load_state("networkidle")

    def open_data_disks(self, base_url):
        self.page.goto(f"{base_url}/view_disks?type=data")
        self.page.wait_for_load_state("networkidle")

    def open_os_disks(self, base_url):
        self.page.goto(f"{base_url}/view_disks?type=os")
        self.page.wait_for_load_state("networkidle")

    def is_zfs_pools_page(self):
        return self.page.locator("#view_zfs_pools_tab").is_visible()

    def is_data_disks_page(self):
        return self.page.locator("#view_data_disks_tab").is_visible()

    def is_os_disks_page(self):
        return self.page.locator("#view_os_disks_tab").is_visible()

    def is_rotating_data_disks_section_visible(self):
        return self.page.get_by_text(
            "Data disks (rotating)",
            exact=True,
        ).is_visible()

    def is_flash_data_disks_section_visible(self):
        return self.page.get_by_text(
            "Data disks (Flash)",
            exact=True,
        ).is_visible()

    def has_data_disk_rows(self):
        table = self.page.locator(
            "h4:has-text('Data disks (rotating)')"
        ).locator("xpath=following-sibling::table[1]")

        return table.locator("tbody tr").count() > 1

    def is_smart_status_visible(self):
    	return self.page.get_by_role(
            "columnheader",
            name="S.M.A.R.T status",
        ).first.is_visible()

    def is_disk_replacement_visible(self):
        return self.page.get_by_role(
            "columnheader",
            name="Disk replacement",
        ).first.is_visible()

    def is_pool_information_visible(self):
        return self.page.get_by_text(
            "Pool :",
            exact=False,
        ).first.is_visible()

    def is_os_disk_information_visible(self):
        return self.page.get_by_text(
            "OS Disks information",
            exact=True,
        ).is_visible()

    def has_os_disk_rows(self):
        table = self.page.locator(
            "h4:has-text('OS Disks information')"
        ).locator("xpath=following-sibling::table[1]")

        return table.locator("tbody tr").count() > 1

    def open_system_tunable(self, base_url):
        self.page.goto(f"{base_url}/view_system_tunable/")
        self.page.wait_for_load_state("networkidle")

    def is_system_tunable_page(self):
        return self.page.locator(
            "#view_system_tunable_tab"
        ).is_visible()

    def get_system_tunable_templates(self):
        return [
            option.inner_text().strip()
            for option in self.page.locator(
                "#template option"
            ).all()
        ]

    def select_system_tunable_template(self, template_name):
        self.page.locator("#template").select_option(
            label=template_name
        )

        # The page uses JavaScript onchange to update
        # the Template Values table.
        self.page.wait_for_timeout(300)

    def is_template_values_visible(self):
        values = self.page.locator("#template-value")

        if not values.is_visible():
            # Open the Bootstrap collapse panel if necessary.
            collapse = self.page.locator("#collapseOne")

            if not collapse.is_visible():
                self.page.get_by_text(
                    "Click Here to See Template Values",
                    exact=False,
                ).click()

                self.page.wait_for_timeout(300)

        # Verify that actual template values are present.
        return (
            values.is_visible()
            and values.locator("table tr").count() > 0
        )


    def get_template_values_text(self) -> str:
        return self.page.locator(
            "#template-value"
        ).inner_text()
