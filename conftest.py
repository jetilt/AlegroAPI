"""
This module contains shared pytest fixtures for API tests.
"""
import random
import time

from typing import Generator, Dict, Any

import pytest
import requests

from playwright.sync_api import Playwright, APIRequestContext
from tests.helpers import generate_pet_data


def get_unique_mock_id() -> int:
    """ This function generates a unique mock pet ID for not_found tests """
    return int(time.time() * 10000) + random.randint(1, 100000)

@pytest.fixture
def mock_id(request) -> int:
    """
    This fixture provides a mock ID at runtime to avoid changing test methods string ID
    during parametrization
    """
    if request.param == "random":
        return get_unique_mock_id()
    return request.param

@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright,
) -> Generator[APIRequestContext, None, None]:
    """ This fixture defines a Playwright APIRequestContext for API tests """
    request_context = playwright.request.new_context(
        base_url="https://petstore.swagger.io/v2",
        extra_http_headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    yield request_context
    request_context.dispose()

@pytest.fixture(scope="session")
def api_session() -> Generator[requests.Session, None, None]:
    """ This fixture defines a requests Session for connection pooling """
    session = requests.Session()
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    yield session
    session.close()

@pytest.fixture
def pet_payload() -> Dict[str, Any]:
    """ This fixture provides a fresh pet payload for each API test """
    return generate_pet_data()
