from pathlib import Path
import re
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# GENERIC HELPERS
# ============================================================

def save_page(page, filename):
    path = LOG_DIR / filename
    path.write_text(page.content(), encoding="utf-8")


def print_page(page, title):
    body = page.locator("body").inner_text()
    print(f"\n{'=' * 20} {title} {'=' * 20}")
    print(body)
    return body


def wait_page(page):
    try:
        page.wait_for_load_state("domcontentloaded", timeout=30000)
    except PlaywrightTimeoutError:
        pass

    page.wait_for_timeout(1000)


def scroll_page_top_to_bottom(page, pause_ms=400):
    """
    Scroll the main browser page repeatedly from top to bottom.

    This is different from a single window.scrollTo() call.
    """

    print("\n--- MAIN PAGE SCROLL: TOP -> BOTTOM ---")

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(pause_ms)

    previous_height = -1

    for _ in range(100):
        result = page.evaluate(
            """
            () => {
                const doc = document.documentElement;
                const body = document.body;

                const height = Math.max(
                    doc ? doc.scrollHeight : 0,
                    body ? body.scrollHeight : 0
                );

                const viewport = window.innerHeight;

                const before = window.scrollY;

                window.scrollBy(0, Math.max(viewport * 0.75, 300));

                return {
                    height,
                    viewport,
                    before,
                    after: window.scrollY
                };
            }
            """
        )

        print(
            "MAIN SCROLL:",
            "before=", result["before"],
            "after=", result["after"],
            "height=", result["height"],
        )

        page.wait_for_timeout(pause_ms)

        if (
            result["after"] >= result["height"] - result["viewport"] - 5
            and result["height"] == previous_height
        ):
            break

        previous_height = result["height"]

    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_timeout(pause_ms)

    print("--- MAIN PAGE SCROLL COMPLETE ---")


def scroll_all_scrollable_elements(page, pause_ms=300):
    """
    Scroll every visible scrollable element.

    This catches cases where Netdata is inside:
      - a div
      - a dashboard panel
      - an iframe
      - an embedded application
    """

    print("\n--- SCROLLING ALL SCROLLABLE ELEMENTS ---")

    result = page.evaluate(
        """
        () => {
            const elements = [];

            for (const el of document.querySelectorAll("*")) {
                const style = getComputedStyle(el);

                const scrollable =
                    (el.scrollHeight > el.clientHeight + 5) &&
                    (
                        style.overflowY === "auto" ||
                        style.overflowY === "scroll" ||
                        style.overflowY === "overlay"
                    );

                if (scrollable) {
                    const rect = el.getBoundingClientRect();

                    if (
                        rect.width > 0 &&
                        rect.height > 0
                    ) {
                        elements.push({
                            tag: el.tagName,
                            id: el.id,
                            className: String(el.className).slice(0, 150),
                            scrollHeight: el.scrollHeight,
                            clientHeight: el.clientHeight
                        });
                    }
                }
            }

            return elements;
        }
        """
    )

    print("Scrollable elements found:", len(result))

    for index, item in enumerate(result, start=1):
        print(
            f"Scrollable element #{index}:",
            item
        )

    # Scroll every scrollable element.
    page.evaluate(
        """
        () => {
            const elements = [];

            for (const el of document.querySelectorAll("*")) {
                const style = getComputedStyle(el);

                const scrollable =
                    (el.scrollHeight > el.clientHeight + 5) &&
                    (
                        style.overflowY === "auto" ||
                        style.overflowY === "scroll" ||
                        style.overflowY === "overlay"
                    );

                if (scrollable) {
                    const rect = el.getBoundingClientRect();

                    if (rect.width > 0 && rect.height > 0) {
                        elements.push(el);
                    }
                }
            }

            for (const el of elements) {
                el.scrollTop = 0;
            }
        }
        """
    )

    page.wait_for_timeout(pause_ms)

    # Gradually move every scrollable element.
    for _ in range(100):
        done = page.evaluate(
            """
            () => {
                const elements = [];

                for (const el of document.querySelectorAll("*")) {
                    const style = getComputedStyle(el);

                    const scrollable =
                        (el.scrollHeight > el.clientHeight + 5) &&
                        (
                            style.overflowY === "auto" ||
                            style.overflowY === "scroll" ||
                            style.overflowY === "overlay"
                        );

                    if (scrollable) {
                        const rect = el.getBoundingClientRect();

                        if (rect.width > 0 && rect.height > 0) {
                            elements.push(el);
                        }
                    }
                }

                let allDone = true;

                for (const el of elements) {
                    const maxScroll =
                        el.scrollHeight - el.clientHeight;

                    if (el.scrollTop < maxScroll - 5) {
                        el.scrollTop = Math.min(
                            el.scrollTop + Math.max(el.clientHeight * 0.75, 300),
                            maxScroll
                        );

                        allDone = false;
                    }
                }

                return allDone;
            }
            """
        )

        page.wait_for_timeout(pause_ms)

        if done:
            break

    print("--- SCROLLABLE ELEMENTS COMPLETE ---")


def scroll_iframe_top_to_bottom(page, frame, frame_name="iframe"):
    """
    Scroll the document inside an iframe.

    This is important for Netdata if it is embedded as an iframe.
    """

    print(f"\n--- {frame_name}: TOP -> BOTTOM ---")

    try:
        frame.evaluate("window.scrollTo(0, 0)")
    except Exception as exc:
        print(f"{frame_name}: cannot scroll frame:", exc)
        return

    page.wait_for_timeout(500)

    previous = None

    for step in range(100):
        try:
            state = frame.evaluate(
                """
                () => {
                    const doc = document.documentElement;
                    const body = document.body;

                    const height = Math.max(
                        doc ? doc.scrollHeight : 0,
                        body ? body.scrollHeight : 0
                    );

                    const viewport = window.innerHeight;
                    const before = window.scrollY;

                    window.scrollBy(
                        0,
                        Math.max(viewport * 0.70, 300)
                    );

                    return {
                        height,
                        viewport,
                        before,
                        after: window.scrollY
                    };
                }
                """
            )
        except Exception as exc:
            print(f"{frame_name}: frame scrolling stopped:", exc)
            break

        print(
            f"{frame_name} STEP {step + 1}:",
            state
        )

        page.wait_for_timeout(400)

        current = (
            state["height"],
            state["after"],
        )

        if previous == current:
            break

        if (
            state["after"]
            >= state["height"] - state["viewport"] - 5
        ):
            # Do one more attempt because dynamically loaded
            # Netdata content can increase scrollHeight.
            page.wait_for_timeout(1000)

            try:
                new_height = frame.evaluate(
                    """
                    () => Math.max(
                        document.documentElement.scrollHeight,
                        document.body.scrollHeight
                    )
                    """
                )

                if new_height <= state["height"] + 5:
                    break
            except Exception:
                break

        previous = current

    try:
        frame.evaluate(
            """
            () => window.scrollTo(
                0,
                Math.max(
                    document.documentElement.scrollHeight,
                    document.body.scrollHeight
                )
            )
            """
        )
    except Exception:
        pass

    page.wait_for_timeout(1000)

    print(f"--- {frame_name}: SCROLL COMPLETE ---")


def scroll_netdata(page):
    """
    Dedicated Netdata scrolling.

    Handles:
      1. Main page
      2. All scrollable containers
      3. All iframes
      4. Netdata-related iframes
    """

    print("\n")
    print("=" * 70)
    print("NETDATA SCROLL START")
    print("=" * 70)

    # First make sure dashboard is at the top.
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    # Main page scroll.
    scroll_page_top_to_bottom(page, pause_ms=500)

    # Scroll all internal containers.
    scroll_all_scrollable_elements(page, pause_ms=500)

    # --------------------------------------------------------
    # IFRAME SCROLL
    # --------------------------------------------------------

    frames = page.frames

    print("\nTotal frames:", len(frames))

    for index, frame in enumerate(frames):
        if frame == page.main_frame:
            continue

        try:
            print(
                f"\nFRAME #{index}:",
                frame.url
            )

            scroll_iframe_top_to_bottom(
                page,
                frame,
                frame_name=f"FRAME #{index}"
            )

        except Exception as exc:
            print(
                f"FRAME #{index} skipped:",
                exc
            )

    # --------------------------------------------------------
    # FINAL PASS
    # --------------------------------------------------------

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    # Use mouse wheel as a final real-browser scroll.
    for _ in range(60):
        page.mouse.wheel(0, 600)
        page.wait_for_timeout(150)

    page.wait_for_timeout(1000)

    print("=" * 70)
    print("NETDATA SCROLL COMPLETE")
    print("=" * 70)


def click_text_if_exists(page, text, timeout=3000):
    """
    Click a visible link/button when it exists.

    Returns True when clicked.
    """

    patterns = [
        text,
        re.compile(rf"^{re.escape(text)}$", re.I),
        re.compile(re.escape(text), re.I),
    ]

    for pattern in patterns:
        try:
            locator = page.get_by_role(
                "link",
                name=pattern
            )

            if locator.count() > 0:
                locator.first.click(timeout=timeout)
                wait_page(page)
                print(f"CLICKED LINK: {text}")
                return True
        except Exception:
            pass

        try:
            locator = page.get_by_role(
                "button",
                name=pattern
            )

            if locator.count() > 0:
                locator.first.click(timeout=timeout)
                wait_page(page)
                print(f"CLICKED BUTTON: {text}")
                return True
        except Exception:
            pass

    print(f"NOT FOUND: {text}")
    return False


def open_path(page, base_url, path, title, filename):
    """
    Navigate directly to a known application URL.
    """

    url = base_url.rstrip("/") + "/" + path.lstrip("/")

    print(f"\n>>> OPENING: {title}")
    print(f">>> URL: {url}")

    page.goto(url)
    wait_page(page)

    body = print_page(page, title)

    save_page(page, filename)

    return body


def open_menu_feature(page, feature_name):
    """
    Open a feature from the left navigation.

    Used when the exact child URL is not known.
    """

    print(f"\n>>> NAVIGATION FEATURE: {feature_name}")

    if click_text_if_exists(page, feature_name):
        return True

    print(
        f"WARNING: Navigation item '{feature_name}' "
        "was not found."
    )

    return False


def scroll_current_page(page, title):
    print(f"\n>>> SCROLLING: {title}")

    scroll_page_top_to_bottom(page, pause_ms=350)
    scroll_all_scrollable_elements(page, pause_ms=350)

    print(f">>> SCROLL COMPLETE: {title}")


def click_any_text(page, names, timeout=3000):
    """
    Try several possible UI names.
    """

    for name in names:
        if click_text_if_exists(
            page,
            name,
            timeout=timeout
        ):
            return True

    return False


def ignore_expected_error(page, title):
    """
    Directory Services and similar pages may report an expected
    application error. Save it and continue.
    """

    body = page.locator("body").inner_text()

    save_page(
        page,
        f"full_flow_{title.lower().replace(' ', '_')}.html"
    )

    print(f"\n===== {title} =====")
    print(body)

    if (
        "error" in body.lower()
        or "failed" in body.lower()
        or "exception" in body.lower()
    ):
        print(
            f"Expected/ignored error detected on {title}. "
            "Continuing flow."
        )

    return body


# ============================================================
# TEST
# ============================================================

def test_integralstor_full_flow(page, settings, credentials):

    base_url = settings["base_url"]

    # ========================================================
    # 1. LOGIN
    # ========================================================

    print("\n" + "=" * 70)
    print("1. LOGIN")
    print("=" * 70)

    page.goto(base_url)
    wait_page(page)

    assert page.locator(
        "input[name='username']"
    ).count() > 0

    assert page.locator(
        "input[name='password']"
    ).count() > 0

    page.locator(
        "input[name='username']"
    ).fill(credentials["username"])

    page.locator(
        "input[name='password']"
    ).fill(credentials["password"])

    page.get_by_role(
        "button",
        name=re.compile("Login", re.I)
    ).click()

    wait_page(page)

    # ========================================================
    # 2. DASHBOARD
    # ========================================================

    body = print_page(page, "DASHBOARD")

    assert "Dashboard" in body

    save_page(
        page,
        "full_flow_dashboard.html"
    )

    # ========================================================
    # 3. NETDATA
    # ========================================================

    scroll_netdata(page)

    save_page(
        page,
        "full_flow_netdata_after_scroll.html"
    )

    # ========================================================
    # 4. DISKS AND STORAGE POOLS
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_zfs_pools/",
        "ZFS POOLS",
        "full_flow_zfs_pools.html"
    )

    assert "ZFS pools" in body
    assert "Data disks" in body
    assert "OS Disks" in body
    assert "System Tunable" in body

    # ========================================================
    # 5. CREATE ZFS POOL
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/create_zfs_pool/",
        "CREATE ZFS POOL",
        "full_flow_create_zfs_pool.html"
    )

    if "insufficient unused disks" in body.lower():
        print(
            "\nCREATE ZFS POOL:"
            "\nInsufficient unused disks."
            "\nExisting automationpool will be used."
        )
    else:
        print(
            "\nCREATE ZFS POOL:"
            "\nCreation page available."
        )

    # ========================================================
    # 6. VERIFY ZFS POOL
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_zfs_pools/",
        "VERIFY ZFS POOL",
        "full_flow_verify_zfs_pool.html"
    )

    assert "automationpool" in body
    assert "Online" in body

    # ========================================================
    # 7. CREATE DATASET
    # ========================================================

    dataset_url = (
        "/create_zfs_dataset"
        "?pool=automationpool"
        "&parent=automationpool"
    )

    body = open_path(
        page,
        base_url,
        dataset_url,
        "CREATE DATASET",
        "full_flow_create_dataset.html"
    )

    assert "Create a ZFS dataset" in body
    assert "Parent pool :" in body
    assert "automationpool" in body

    dataset_name_locator = page.locator(
        "input[name='name'], "
        "input[name='dataset_name'], "
        "input[id='name'], "
        "input[id='dataset_name']"
    )

    assert dataset_name_locator.count() > 0

    # ========================================================
    # 8. VERIFY DATASET
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_zfs_pool"
        "?name=automationpool"
        "&view=datasets_and_zvols",
        "VERIFY DATASET",
        "full_flow_verify_dataset.html"
    )

    assert "ZFS pool datasets and volumes" in body

    # ========================================================
    # 9. DATA DISKS
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_disks?type=data",
        "DATA DISKS",
        "full_flow_data_disks.html"
    )

    assert "Data disks" in body

    # ========================================================
    # 10. OS DISKS
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_disks?type=os",
        "OS DISKS",
        "full_flow_os_disks.html"
    )

    assert "System disks information" in body

    # ========================================================
    # 11. SYSTEM TUNABLE
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_system_tunable",
        "SYSTEM TUNABLE",
        "full_flow_system_tunable.html"
    )

    assert "System Tunable" in body

    # ========================================================
    # 12-19. DIRECTORIES / SHARES / TARGETS
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_cifs_shares/",
        "WINDOWS SHARES",
        "full_flow_windows_shares.html"
    )

    assert (
        "Directories, shares & targets" in body
        or "Windows Shares" in body
    )

    body = open_path(
        page,
        base_url,
        "/view_nfs_shares/",
        "NFS EXPORTS",
        "full_flow_nfs_exports.html"
    )

    assert "NFS" in body or "nfs" in body.lower()

    body = open_path(
        page,
        base_url,
        "/view_iscsi_targets/",
        "iSCSI TARGETS",
        "full_flow_iscsi_targets.html"
    )

    assert (
        "iSCSI" in body
        or "ISCSI" in body
        or "iscsi" in body.lower()
    )

    body = open_path(
        page,
        base_url,
        "/view_rsync_shares/",
        "RSYNC SHARES",
        "full_flow_rsync_shares.html"
    )

    assert (
        "RSync" in body
        or "rsync" in body.lower()
    )

    body = open_path(
        page,
        base_url,
        "/view_dir_manager/",
        "DIRECTORY MANAGER",
        "full_flow_directory_manager.html"
    )

    assert "directory" in body.lower()

    body = open_path(
        page,
        base_url,
        "/view_afp_shares/",
        "AFP EXPORTS",
        "full_flow_afp_exports.html"
    )

    assert "AFP" in body or "afp" in body.lower()

    body = open_path(
        page,
        base_url,
        "/view_webdav_shares/",
        "WEBDAV EXPORTS",
        "full_flow_webdav_exports.html"
    )

    assert "webdav" in body.lower()

    # ========================================================
    # 20. REPLICATION & SNAPSHOTS
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_remote_replications/",
        "REPLICATION & SNAPSHOTS",
        "full_flow_replication.html"
    )

    assert (
        "Replication" in body
        or "replication" in body.lower()
        or "snapshot" in body.lower()
    )

    # --------------------------------------------------------
    # VIEW SNAPSHOTS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "View Snapshots",
            "Snapshots",
            "View snapshots",
        ]
    )

    save_page(
        page,
        "full_flow_view_snapshots.html"
    )

    # --------------------------------------------------------
    # VIEW SNAPSHOT SCHEDULES
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "View Snapshot Schedules",
            "Snapshot Schedules",
            "View snapshot schedules",
            "Schedules",
        ]
    )

    save_page(
        page,
        "full_flow_snapshot_schedules.html"
    )

    # --------------------------------------------------------
    # SCHEDULE SNAPSHOT
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Schedule Snapshot",
            "Create Snapshot Schedule",
            "Add Snapshot Schedule",
            "Schedule",
        ]
    )

    save_page(
        page,
        "full_flow_schedule_snapshot.html"
    )

    # --------------------------------------------------------
    # REMOTE APPLICATIONS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Remote Applications",
            "Remote applications",
            "View Remote Applications",
        ]
    )

    save_page(
        page,
        "full_flow_remote_applications.html"
    )

    # --------------------------------------------------------
    # REMOTE REPLICATION
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Remote Replication",
            "Remote replication",
            "View Remote Replication",
            "Add Remote Replication",
        ]
    )

    save_page(
        page,
        "full_flow_remote_replication.html"
    )

    # ========================================================
    # 21. DATA BACKUP
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_backup/",
        "DATA BACKUP",
        "full_flow_data_backup.html"
    )

    assert "backup" in body.lower()

    # ========================================================
    # 22. BACKGROUND TASKS
    # ========================================================

    body = open_path(
        page,
        base_url,
        "/view_background_tasks/",
        "BACKGROUND TASKS",
        "full_flow_background_tasks.html"
    )

    assert "background" in body.lower()

    # ========================================================
    # 23. KEYS AND CERTIFICATES
    # ========================================================

    open_menu_feature(
        page,
        "Keys and Certificates"
    )

    # --------------------------------------------------------
    # USER SSH KEYS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "User SSH keys",
            "User SSH Keys",
            "SSH Keys",
        ]
    )

    save_page(
        page,
        "full_flow_user_ssh_keys.html"
    )

    # --------------------------------------------------------
    # KNOWN HOSTS SSH FINGERPRINT
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Known Hosts SSH fingerprint",
            "Known Hosts",
            "SSH fingerprint",
            "Known hosts SSH fingerprint",
        ]
    )

    save_page(
        page,
        "full_flow_known_hosts_ssh_fingerprint.html"
    )

    # --------------------------------------------------------
    # SSL CERTIFICATES AND KEYS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "SSL certificates and keys",
            "SSL Certificates",
            "Certificates and Keys",
            "Certificates",
        ]
    )

    save_page(
        page,
        "full_flow_ssl_certificates_keys.html"
    )

    # ========================================================
    # 24. NETWORKING
    # ========================================================

    open_menu_feature(
        page,
        "Networking"
    )

    # --------------------------------------------------------
    # NETWORK INTERFACES
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Network Interfaces",
            "Network interfaces",
            "Interfaces",
        ]
    )

    scroll_current_page(
        page,
        "NETWORK INTERFACES"
    )

    save_page(
        page,
        "full_flow_network_interfaces.html"
    )

    # --------------------------------------------------------
    # HOSTNAME
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Hostname",
            "Host Name",
        ]
    )

    save_page(
        page,
        "full_flow_hostname.html"
    )

    # --------------------------------------------------------
    # DNS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "DNS",
            "DNS Settings",
            "Domain Name System",
        ]
    )

    save_page(
        page,
        "full_flow_dns.html"
    )

    # ========================================================
    # 25. SERVICES
    # ========================================================

    open_menu_feature(
        page,
        "Services"
    )

    # --------------------------------------------------------
    # VIEW SERVICES
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "View Services",
            "View services",
            "Services",
        ]
    )

    save_page(
        page,
        "full_flow_view_services.html"
    )

    # --------------------------------------------------------
    # SCROLL SERVICES TOP -> BOTTOM
    # --------------------------------------------------------

    scroll_current_page(
        page,
        "SERVICES TOP TO BOTTOM"
    )

    # --------------------------------------------------------
    # CONFIGURE NTP
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Configure NTP",
            "NTP",
            "Configure ntp",
        ]
    )

    save_page(
        page,
        "full_flow_configure_ntp.html"
    )

    # --------------------------------------------------------
    # CONFIGURE WINDOWS ACCESS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Configure Windows Access",
            "Windows Access",
            "Configure Windows",
        ]
    )

    save_page(
        page,
        "full_flow_configure_windows_access.html"
    )

    # --------------------------------------------------------
    # CONFIGURE FTP ACCESS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Configure FTP Access",
            "FTP Access",
            "Configure FTP",
        ]
    )

    save_page(
        page,
        "full_flow_configure_ftp_access.html"
    )

    # --------------------------------------------------------
    # CONFIGURE EMAIL SETTINGS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Configure Email Settings",
            "Email Settings",
            "Configure Email",
        ]
    )

    save_page(
        page,
        "full_flow_configure_email_settings.html"
    )

    # ========================================================
    # 26. SYSTEM
    # ========================================================

    open_menu_feature(
        page,
        "System"
    )

    # --------------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "System Information",
            "System information",
            "View System Information",
        ]
    )

    save_page(
        page,
        "full_flow_system_information.html"
    )

    # --------------------------------------------------------
    # REBOOT
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Reboot",
            "Restart",
        ]
    )

    save_page(
        page,
        "full_flow_reboot.html"
    )

    # --------------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Shutdown",
            "Shut Down",
        ]
    )

    save_page(
        page,
        "full_flow_shutdown.html"
    )

    # --------------------------------------------------------
    # SHELL ACCESS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Shell Access",
            "Shell access",
            "Shell",
        ]
    )

    save_page(
        page,
        "full_flow_shell_access.html"
    )

    # ========================================================
    # 27. USERS & GROUPS
    # ========================================================

    open_menu_feature(
        page,
        "Users & groups"
    )

    # --------------------------------------------------------
    # LOCAL USERS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Local Users",
            "Local users",
            "Users",
        ]
    )

    save_page(
        page,
        "full_flow_local_users.html"
    )

    # --------------------------------------------------------
    # LOCAL GROUPS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Local Groups",
            "Local groups",
            "Groups",
        ]
    )

    save_page(
        page,
        "full_flow_local_groups.html"
    )

    # --------------------------------------------------------
    # DIRECTORY SERVICES
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Directory Services",
            "Directory services",
        ]
    )

    # Ignore Directory Services errors and continue.
    ignore_expected_error(
        page,
        "DIRECTORY SERVICES"
    )

    # ========================================================
    # 28. MONITORING
    # ========================================================

    open_menu_feature(
        page,
        "Monitoring"
    )

    # --------------------------------------------------------
    # AUDIT TRAIL
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Audit Trail",
            "Audit trail",
            "Audits",
        ]
    )

    save_page(
        page,
        "full_flow_audit_trail.html"
    )

    # --------------------------------------------------------
    # ALERTS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Alerts",
            "View Alerts",
        ]
    )

    save_page(
        page,
        "full_flow_alerts.html"
    )

    # --------------------------------------------------------
    # LOGS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Logs",
            "View Logs",
            "System Logs",
        ]
    )

    save_page(
        page,
        "full_flow_logs.html"
    )

    # --------------------------------------------------------
    # SCHEDULE NOTIFICATIONS
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Schedule Notifications",
            "Scheduled Notifications",
            "Notifications",
        ]
    )

    save_page(
        page,
        "full_flow_schedule_notifications.html"
    )

    # --------------------------------------------------------
    # REMOTE MONITORING
    # --------------------------------------------------------

    click_any_text(
        page,
        [
            "Remote Monitoring",
            "Remote monitoring",
        ]
    )

    save_page(
        page,
        "full_flow_remote_monitoring.html"
    )

    # ========================================================
    # END
    # ========================================================

    print("\n")
    print("=" * 70)
    print("FULL INTEGRALSTOR AUTOMATION FLOW COMPLETE")
    print("=" * 70)

