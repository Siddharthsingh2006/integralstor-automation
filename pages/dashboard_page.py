from playwright.sync_api import Page


class DashboardPage:
    def __init__(self, page: Page):
        self.page = page

    def is_dashboard_visible(self) -> bool:
        return self.page.locator("#dashboard_menu").is_visible()

    def is_storage_pools_visible(self) -> bool:
        return self.page.locator(
            'a[href="/view_zfs_pools/"]'
        ).is_visible()

    def is_shares_visible(self) -> bool:
        return self.page.locator(
            'a[href="/view_cifs_shares/"]'
        ).is_visible()

    def is_snapshots_visible(self) -> bool:
        return self.page.locator(
            'a[href="/view_zfs_snapshots/"]'
        ).is_visible()

    def is_backup_visible(self) -> bool:
        return self.page.locator(
            'a[href="/view_backup/"]'
        ).is_visible()

    def is_interfaces_visible(self) -> bool:
        return self.page.locator(
            'a[href="/view_interfaces/"]'
        ).is_visible()

    def is_netdata_visible(self) -> bool:
        """
        Check that the Netdata iframe exists and has loaded.
        """
        iframe = self.page.locator(
            'iframe[src*=":19999/"]'
        )

        if not iframe.is_visible():
            return False

        netdata_frame = self.page.frame(
            url=lambda url: ":19999/" in url
        )

        return netdata_frame is not None

    def scroll_netdata_top_to_bottom(
        self,
        step=900,
        pause_ms=150,
    ):
        """
        Quickly but visibly scroll the actual Netdata
        dashboard from top to bottom.
        """

        iframe = self.page.locator(
            'iframe[src*=":19999/"]'
        )

        iframe.wait_for(state="visible")

        netdata_frame = self.page.frame(
            url=lambda url: ":19999/" in url
        )

        if netdata_frame is None:
            raise AssertionError(
                "Netdata iframe was found, "
                "but its frame did not load."
            )

        # Give Netdata time to render its charts.
        self.page.wait_for_timeout(2000)

        # Start at the very top.
        netdata_frame.evaluate(
            "() => window.scrollTo(0, 0)"
        )

        self.page.wait_for_timeout(500)

        previous_y = -1
        unchanged_count = 0

        while True:
            current_y = netdata_frame.evaluate(
                "() => window.scrollY"
            )

            scroll_height = netdata_frame.evaluate(
                "() => document.documentElement.scrollHeight"
            )

            viewport_height = netdata_frame.evaluate(
                "() => window.innerHeight"
            )

            # Netdata reached the bottom.
            if current_y + viewport_height >= scroll_height - 10:
                break

            # Detect a page that stopped moving.
            if current_y == previous_y:
                unchanged_count += 1
            else:
                unchanged_count = 0

            if unchanged_count >= 3:
                break

            previous_y = current_y

            # Scroll inside Netdata.
            netdata_frame.evaluate(
                """
                (step) => window.scrollBy({
                    top: step,
                    left: 0,
                    behavior: "smooth"
                })
                """,
                step,
            )

            # Small pause so the metrics remain visible.
            self.page.wait_for_timeout(pause_ms)

        # Ensure we finish at the bottom.
        netdata_frame.evaluate(
            """
            () => window.scrollTo({
                top: document.documentElement.scrollHeight,
                behavior: "smooth"
            })
            """
        )

        self.page.wait_for_timeout(1000)
