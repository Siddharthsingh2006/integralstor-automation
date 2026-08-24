from pathlib import Path


def test_inspect_zfs_dataset_links(page, settings, credentials):
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

    print("\n--- ZFS POOLS ---")
    print(body)

    assert "ZFS pools" in body
    assert "automationpool" in body

    # -------------------------------------------------
    # Inspect all links related to datasets
    # -------------------------------------------------
    print("\n--- DATASET RELATED LINKS ---")

    links = page.locator("a").all()

    dataset_links = []

    for link in links:
        text = link.inner_text().strip()
        href = link.get_attribute("href")

        if text or href:
            if (
                "dataset" in text.lower()
                or "dataset" in (href or "").lower()
            ):
                print(f"TEXT= {text!r} HREF= {href}")

                dataset_links.append({
                    "text": text,
                    "href": href,
                })

    assert dataset_links, "No dataset-related links found"

    # -------------------------------------------------
    # Find the Create a new dataset link
    # -------------------------------------------------
    create_dataset_link = None

    for item in dataset_links:
        if "Create a new dataset" in item["text"]:
            create_dataset_link = item
            break

    assert create_dataset_link is not None, (
        "Create a new dataset link was not found"
    )

    href = create_dataset_link["href"]

    print("\n--- CREATE DATASET LINK ---")
    print(f"TEXT= {create_dataset_link['text']!r}")
    print(f"HREF= {href}")

    assert href is not None
    assert "create_zfs_dataset" in href
    assert "pool=automationpool" in href

    # -------------------------------------------------
    # Open the dataset creation page
    # -------------------------------------------------
    if href.startswith("http"):
        dataset_url = href
    else:
        dataset_url = settings["base_url"] + href

    print("\n--- DATASET CREATION URL ---")
    print(dataset_url)

    page.goto(dataset_url)
    page.wait_for_load_state("networkidle")

    body = page.locator("body").inner_text()

    print("\n--- CREATE DATASET PAGE ---")
    print(body)

    # Save HTML for inspection
    Path("logs/create_zfs_dataset.html").write_text(
        page.content(),
        encoding="utf-8",
    )

    # -------------------------------------------------
    # Verify dataset page loaded successfully
    # -------------------------------------------------
    assert (
        "dataset" in body.lower()
    ), "Dataset creation page did not contain dataset-related text"
