import requests


def test_integralstor_preflight(settings):
    base_url = settings["base_url"]

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
