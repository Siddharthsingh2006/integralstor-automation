from pages.login_page import LoginPage


def test_integralstor_preflight(page, settings, credentials):
    base_url = settings["base_url"]

    # 1. Open IntegralStor
    page.goto(base_url, wait_until="domcontentloaded")

    # 2. Verify login page is available
    login_page = LoginPage(page)

    assert login_page.is_login_page_visible(), (
        "IntegralStor is reachable, but the login page is not available"
    )

    print("\nIntegralStor login page: AVAILABLE")

    # 3. Perform real login
    login_page.login(
        credentials["username"],
        credentials["password"],
    )

    # 4. Wait for navigation/application to settle
    page.wait_for_load_state("networkidle")

    # 5. Verify login actually succeeded
    assert page.url != base_url.rstrip("/") + "/", (
        f"Login appears to have failed. Current URL: {page.url}"
    )

    print(f"IntegralStor login: SUCCESS")
    print(f"Post-login URL: {page.url}")
