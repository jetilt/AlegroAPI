"""
This module contains security and authentication tests
for the Petstore API using Playwright's APIRequestContext.
"""
# pylint: disable=redefined-outer-name
from typing import Dict, Any

import pytest

from playwright.sync_api import APIRequestContext

from tests.test_petstore_api import created_pet  # pylint: disable=unused-import


class TestAuthSecurity:
    """
    This class contains Auth Tests
    for Petstore Pet endpoints using APIRequestContext
    """

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated creation instead of returning 401"
    )
    def test_create_pet_unauthenticated(
        self, api_request_context: APIRequestContext, pet_payload: Dict[str, Any]
    ):
        """
        This negative test verifies that creating a pet requires OAuth2 authentication.
        Endpoint: POST https://petstore.swagger.io/v2/pet
        Security: petstore_auth (OAuth2)
        """
        response = api_request_context.post(
            "/v2/pet",
            data=pet_payload,
            headers={"Authorization": ""}
        )
        assert response.status == 401, (
            f"Expected status code 401 Unauthorized without OAuth2 token, "
            f"got {response.status}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows requests when Authorization header is completely omitted"
    )
    def test_create_pet_missing_auth_header(
        self, api_request_context: APIRequestContext, pet_payload: Dict[str, Any]
    ):
        """
        This negative test verifies that completely omitting the Authorization header is rejected.
        Endpoint: POST https://petstore.swagger.io/v2/pet
        Security: petstore_auth (OAuth2)
        """
        response = api_request_context.post(
            "/v2/pet",
            data=pet_payload
            # Note: No Authorization header
        )
        assert response.status == 401, (
            f"Expected status code 401 Unauthorized with missing auth header, "
            f"got {response.status}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated updates instead of returning 401"
    )
    def test_update_pet_unauthenticated(
        self, api_request_context: APIRequestContext, created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that updating a pet requires OAuth2 authentication.
        Endpoint: PUT https://petstore.swagger.io/v2/pet
        Security: petstore_auth (OAuth2)
        """
        created_pet["name"] = "unauthenticated_update"
        response = api_request_context.put(
            "/v2/pet",
            data=created_pet,
            headers={"Authorization": ""}
        )
        assert response.status == 401, (
            f"Expected status code 401 Unauthorized without OAuth2 token, "
            f"got {response.status}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated deletions instead of returning 401"
    )
    def test_delete_pet_unauthenticated(
        self, api_request_context: APIRequestContext, pet_payload: Dict[str, Any]
    ):
        """
        This negative test verifies that deleting a pet requires OAuth2 authentication.
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        Security: petstore_auth (OAuth2)
        """
        api_request_context.post("/v2/pet", data=pet_payload)
        pet_id = pet_payload["id"]

        response = api_request_context.delete(
            f"/v2/pet/{pet_id}",
            headers={"Authorization": ""}
        )
        assert response.status == 401, (
            f"Expected status code 401 Unauthorized without OAuth2 token, "
            f"got {response.status}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API accepts invalid API keys instead of returning 401 or 403"
    )
    def test_delete_pet_invalid_api_key(
        self, api_request_context: APIRequestContext, created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that an invalid api_key parameter is rejected on DELETE.
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        """
        pet_id = created_pet["id"]
        response = api_request_context.delete(
            f"/v2/pet/{pet_id}",
            headers={"api_key": "TEST_KEY_123"}
        )
        assert response.status in [401, 403], (
            f"Expected status code 401 or 403 with invalid api_key, "
            f"got {response.status}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API returns pet data instead of 401 without api_key"
    )
    def test_get_pet_unauthenticated(
        self, api_request_context: APIRequestContext, created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that retrieving a pet by ID requires an api_key.
        Endpoint: GET https://petstore.swagger.io/v2/pet/{petId}
        Security: api_key (header)
        """
        pet_id = created_pet["id"]
        response = api_request_context.get(
            f"/v2/pet/{pet_id}",
            headers={"api_key": ""}
        )
        assert response.status == 401, (
            f"Expected status code 401 Unauthorized without api_key, "
            f"got {response.status}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API accepts invalid API keys instead of returning 401 or 403"
    )
    def test_get_pet_invalid_api_key(
        self, api_request_context: APIRequestContext, created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that an invalid api_key is rejected on GET.
        Endpoint: GET https://petstore.swagger.io/v2/pet/{petId}
        Security: api_key (header)
        """
        pet_id = created_pet["id"]
        response = api_request_context.get(
            f"/v2/pet/{pet_id}",
            headers={"api_key": "TEST_KEY_123"}
        )
        assert response.status in [401, 403], (
            f"Expected status code 401 or 403 with invalid api_key, "
            f"got {response.status}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated search by status instead of returning 401"
    )
    def test_find_pets_by_status_unauthenticated(
        self, api_request_context: APIRequestContext
    ):
        """
        This negative test verifies that searching pets by status requires OAuth2 authentication.
        Endpoint: GET https://petstore.swagger.io/v2/pet/findByStatus
        Security: petstore_auth (OAuth2)
        """
        response = api_request_context.get(
            "/v2/pet/findByStatus",
            params={"status": "available"},
            headers={"Authorization": ""}
        )
        assert response.status == 401, (
            f"Expected status code 401 Unauthorized without OAuth2 token, "
            f"got {response.status}"
        )
