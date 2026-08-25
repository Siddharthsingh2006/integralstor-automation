import requests

from pages.login_page import LoginPage


def test_integralstor_preflight(page, settings, credentials):
    base_url = settings["base_url"]

    # 1. HTTP health check
    response = requests.get(
        base_url,
        timeout=10,
        allow_redirects=True,
    )

    assert response.status_code < 500, (
        f"IntegralStor returned HTTP {response.status_code}"
    )

    print(f"\nIntegralStor reachable: {response.url}")
    print(f"HTTP status: {response.status_code}")

    # 2. Open IntegralStor login page
    login_page = LoginPage(page)
    login_page.open(base_url)

    # 3. Verify login form exists
    assert login_page.is_login_page_visible(), (
        "IntegralStor is reachable, but the login page is not available"
    )

    print("IntegralStor login page: AVAILABLE")

    # 4. Perform login
    login_page.login(
        credentials["username"],
        credentials["password"],
    )

    # 5. Wait for application navigation
    page.wait_for_load_state("networkidle")

    # 6. Verify we left the login page
    assert page.url != base_url.rstrip("/") + "/", (
        f"Login appears to have failed. Current URL: {page.url}"
    )

    print("IntegralStor login: SUCCESS")
    print(f"Post-login URL: {page.url}")
