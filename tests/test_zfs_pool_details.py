from pathlib import Path


def test_inspect_zfs_pool_details(page, settings, credentials):
    # -------------------------------------------------
    # Login
    # -------------------------------------------------
    page.goto(settings["base_url"])
    page.wait_for_load_state("networkidle")

    page.locator("input[name='username']").fill(
        credentials["username"]
    )
    page.locator("input[name='password']").fill(
        credentials["password"]
    )
    page.get_by_role("button", name="Login").click()

    page.wait_for_load_state("networkidle")

    # -------------------------------------------------
    # Open ZFS pools
    # -------------------------------------------------
    page.goto(settings["base_url"] + "/view_zfs_pools/")
    page.wait_for_load_state("networkidle")

    body = page.locator("body").inner_text()

    assert "ZFS pools" in body
    assert "automationpool" in body
    assert "Online" in body

    # -------------------------------------------------
    # Basic pool information
    # -------------------------------------------------
    page.goto(
        settings["base_url"]
        + "/view_zfs_pool?name=automationpool&view=basic"
    )
    page.wait_for_load_state("networkidle")

    body = page.locator("body").inner_text()

    print("\n--- BASIC POOL ---")
    print(body)

    Path("logs/zfs_pool_basic.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    assert "automationpool" in body
    assert "Pool type" in body
    assert "RAID5" in body
    assert "Pool state" in body
    assert "ONLINE" in body
    assert "Pool errors" in body
    assert "No known data errors" in body

    # -------------------------------------------------
    # Pool components
    # -------------------------------------------------
    page.goto(
        settings["base_url"]
        + "/view_zfs_pool?name=automationpool&view=components"
    )
    page.wait_for_load_state("networkidle")

    body = page.locator("body").inner_text()

    print("\n--- POOL COMPONENTS ---")
    print(body)

    Path("logs/zfs_pool_components.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # The components page does not display the pool name.
    # Verify the RAID configuration and pool components instead.
    assert "Pool type : RAID5" in body
    assert "raidz1-0 (raid5), State (ONLINE)" in body

    # RAID group + five disks = six ONLINE entries.
    assert body.count("State (ONLINE)") == 6

    # RAID group + five disks = six zero-error entries.
    assert body.count("Read (0)") == 6
    assert body.count("Write (0)") == 6
    assert body.count("Chksum (0)") == 6

    # Verify cache and spare sections are present.
    assert "Write cache" in body
    assert "Read cache" in body
    assert "Spare disks" in body

    # -------------------------------------------------
    # Datasets and ZVOLs
    # -------------------------------------------------
    page.goto(
        settings["base_url"]
        + "/view_zfs_pool?name=automationpool&view=datasets_and_zvols"
    )
    page.wait_for_load_state("networkidle")

    body = page.locator("body").inner_text()

    print("\n--- DATASETS / ZVOLS ---")
    print(body)

    Path("logs/zfs_pool_datasets_zvols.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # Verify the datasets/ZVOLs page loaded.
    assert (
        "Filesystem datasets" in body
        or "block device volumes" in body
        or "Datasets" in body
        or "ZVOL" in body
    )
