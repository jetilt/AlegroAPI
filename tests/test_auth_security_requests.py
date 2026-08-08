"""
This module contains security and authentication tests
for the Petstore API using the requests library.
"""
# pylint: disable=redefined-outer-name
from typing import Dict, Any

import pytest
import requests

from tests.test_petstore_api_requests import BASE_URL, created_pet  # pylint: disable=unused-import


class TestAuthSecurityRequests:
    """ This class contains auth tests for Petstore Pet endpoints using requests """

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated creation instead of returning 401"
    )
    def test_create_pet_unauthenticated(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This negative test verifies that creating a pet requires OAuth2 authentication.
        Endpoint: POST https://petstore.swagger.io/v2/pet
        Security: petstore_auth (OAuth2)
        """
        response = api_session.post(
            f"{BASE_URL}/pet",
            json=pet_payload,
            headers={"Authorization": ""}
        )
        assert response.status_code == 401, (
            f"Expected status code 401 Unauthorized without OAuth2 token, "
            f"got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows requests when Authorization header is completely omitted"
    )
    def test_create_pet_missing_auth_header(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This negative test verifies that completely omitting the Authorization header is rejected.
        Endpoint: POST https://petstore.swagger.io/v2/pet
        Security: petstore_auth (OAuth2)
        """
        response = api_session.post(
            f"{BASE_URL}/pet",
            json=pet_payload
            # Note: No Authorization header
        )
        assert response.status_code == 401, (
            f"Expected status code 401 Unauthorized with missing auth header, "
            f"got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated updates instead of returning 401"
    )
    def test_update_pet_unauthenticated(
        self, api_session: requests.Session, created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that updating a pet requires OAuth2 authentication.
        Endpoint: PUT https://petstore.swagger.io/v2/pet
        Security: petstore_auth (OAuth2)
        """
        created_pet["name"] = "unauthenticated_update"
        response = api_session.put(
            f"{BASE_URL}/pet",
            json=created_pet,
            headers={"Authorization": ""}
        )
        assert response.status_code == 401, (
            f"Expected status code 401 Unauthorized without OAuth2 token, "
            f"got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated deletions instead of returning 401"
    )
    def test_delete_pet_unauthenticated(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This negative test verifies that deleting a pet requires OAuth2 authentication.
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        Security: petstore_auth (OAuth2)
        """
        api_session.post(f"{BASE_URL}/pet", json=pet_payload)
        pet_id = pet_payload["id"]

        response = api_session.delete(
            f"{BASE_URL}/pet/{pet_id}",
            headers={"Authorization": ""}
        )
        assert response.status_code == 401, (
            f"Expected status code 401 Unauthorized without OAuth2 token, "
            f"got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API accepts invalid API keys instead of returning 401 or 403"
    )
    def test_delete_pet_invalid_api_key(
        self, api_session: requests.Session, created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that an invalid api_key parameter is rejected on DELETE.
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        """
        pet_id = created_pet["id"]
        response = api_session.delete(
            f"{BASE_URL}/pet/{pet_id}",
            headers={"api_key": "TEST_KEY_123"}
        )
        assert response.status_code in [401, 403], (
            f"Expected status code 401 or 403 with invalid api_key, "
            f"got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API returns pet data instead of 401 without api_key"
    )
    def test_get_pet_unauthenticated(
        self, api_session: requests.Session, created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that retrieving a pet by ID requires an api_key.
        Endpoint: GET https://petstore.swagger.io/v2/pet/{petId}
        Security: api_key (header)
        """
        pet_id = created_pet["id"]
        response = api_session.get(
            f"{BASE_URL}/pet/{pet_id}",
            headers={"api_key": ""}
        )
        assert response.status_code == 401, (
            f"Expected status code 401 Unauthorized without api_key, "
            f"got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API accepts invalid API keys instead of returning 401 or 403"
    )
    def test_get_pet_invalid_api_key(
        self, api_session: requests.Session, created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that an invalid api_key is rejected on GET.
        Endpoint: GET https://petstore.swagger.io/v2/pet/{petId}
        Security: api_key (header)
        """
        pet_id = created_pet["id"]
        response = api_session.get(
            f"{BASE_URL}/pet/{pet_id}",
            headers={"api_key": "TEST_KEY_123"}
        )
        assert response.status_code in [401, 403], (
            f"Expected status code 401 or 403 with invalid api_key, "
            f"got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated search by status instead of returning 401"
    )
    def test_find_pets_by_status_unauthenticated(
        self, api_session: requests.Session
    ):
        """
        This negative test verifies that searching pets by status requires OAuth2 authentication.
        Endpoint: GET https://petstore.swagger.io/v2/pet/findByStatus
        Security: petstore_auth (OAuth2)
        """
        response = api_session.get(
            f"{BASE_URL}/pet/findByStatus",
            params={"status": "available"},
            headers={"Authorization": ""}
        )
        assert response.status_code == 401, (
            f"Expected status code 401 Unauthorized without OAuth2 token, "
            f"got {response.status_code}"
        )
