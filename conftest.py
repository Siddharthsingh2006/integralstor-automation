import os
from pathlib import Path

import pytest
import yaml


CONFIG_FILE = Path(__file__).parent / "config" / "settings.yaml"


@pytest.fixture(scope="session")
def settings():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def credentials():
    username = os.getenv("INTEGRALSTOR_USER")
    password = os.getenv("INTEGRALSTOR_PASSWORD")

    if not username or not password:
        pytest.fail(
            "INTEGRALSTOR_USER and INTEGRALSTOR_PASSWORD "
            "environment variables must be set"
        )

    return {
        "username": username,
        "password": password,
    }
