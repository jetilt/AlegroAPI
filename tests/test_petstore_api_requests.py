"""
This module contains API tests for the Petstore API using the requests library.
"""
# pylint: disable=redefined-outer-name
import time
import random
from typing import Dict, Any, Generator

import pytest
import requests

from tests.test_data import TestData

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

BASE_URL = "https://petstore.swagger.io/v2"

@pytest.fixture
def created_pet(
    api_session: requests.Session, pet_payload: Dict[str, Any]
) -> Generator[Dict[str, Any], None, None]:
    """ This fixture creates a pet before a test and delete it after """
    response = api_session.post(f"{BASE_URL}/pet", json=pet_payload)
    assert response.ok, (
        f"Failed to create a pet for setup: {response.status_code} {response.text}"
    )
    pet_data = response.json()

    yield pet_data

    delete_response = api_session.delete(f"{BASE_URL}/pet/{pet_data['id']}")

    if delete_response.status_code != 404:
        assert delete_response.ok, (
            f"Failed to delete the pet, got {delete_response.status_code}"
        )

class TestPetStoreAPIRequests:
    """ Class contains API Tests for Petstore Pet endpoints using requests library """

    def test_create_pet(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This test creates a new pet
        Endpoint: POST https://petstore.swagger.io/v2/pet
        """
        response = api_session.post(f"{BASE_URL}/pet", json=pet_payload)

        assert response.ok, (
            f"Expected successful response, got '{response.status_code}' "
            f"{response.text}"
        )
        assert response.status_code == 200, (
            f"Expected status code is 200, got {response.status_code}"
        )

        # Verify the created pet's fields
        response_body = response.json()
        assert response_body["id"] == pet_payload["id"], (
            f"Expected ID is {pet_payload['id']}, got {response_body.get('id')}"
        )
        assert response_body["name"] == pet_payload["name"], (
            f"Expected name is '{pet_payload['name']}', got '{response_body.get('name')}'"
        )
        assert response_body["status"] == pet_payload["status"], (
            f"Expected status is '{pet_payload['status']}', "
            f"got '{response_body.get('status')}'"
        )

        api_session.delete(f"{BASE_URL}/pet/{pet_payload['id']}")

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            "",
            pytest.param(
                TestData.INVALID_JSON_STRING,
                marks=pytest.mark.xfail(
                    reason="FAIL: API returns 400 instead of documented 405 for invalid JSON"
                )
            ),
            pytest.param(
                TestData.MALFORMED_JSON_STRING,
                marks=pytest.mark.xfail(
                    reason="FAIL: API returns 400 instead of documented 405 for malformed JSON"
                )
            ),
            None,
        ]
    )
    def test_create_pet_invalid_input(
        self, api_session: requests.Session, invalid_payload: Any
    ):
        """
        This negative test creates a pet with an invalid payload
        Endpoint: POST https://petstore.swagger.io/v2/pet
        """
        response = api_session.post(
            f"{BASE_URL}/pet",
            data=invalid_payload,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 405, (
            f"Expected error status 405, "
            f"got '{response.status_code}'"
        )

    @pytest.mark.xfail(
        reason="FAIL: API returns 200 OK instead of 400 for missing required fields"
    )
    @pytest.mark.parametrize(
        "invalid_payload",
        [
            {},
            {"id": 12345, "status": "available"}
        ]
    )
    def test_create_pet_missing_required_fields(
        self, api_session: requests.Session, invalid_payload: dict
    ):
        """
        This negative test creates a pet with missing required fields
        Endpoint: POST https://petstore.swagger.io/v2/pet
        """
        response = api_session.post(f"{BASE_URL}/pet", json=invalid_payload)
        assert response.status_code == 400, (
            f"Expected error status 400, got '{response.status_code}'"
        )

    @pytest.mark.xfail(
        reason="FAIL: API returns 500 instead of 400 for invalid data type"
    )
    def test_create_pet_invalid_id_type(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This negative test creates a pet with an invalid data type for id
        Endpoint: POST https://petstore.swagger.io/v2/pet
        """
        pet_payload["id"] = "abc"
        response = api_session.post(f"{BASE_URL}/pet", json=pet_payload)
        assert response.status_code == 400, (
            f"Expected error status 400, got '{response.status_code}'"
        )

    @pytest.mark.xfail(
        reason="FAIL: API returns unexpected behavior for integer overflow"
    )
    def test_create_pet_integer_overflow(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This negative test creates a pet with an id causing integer overflow
        Endpoint: POST https://petstore.swagger.io/v2/pet
        """
        pet_payload["id"] = 9999999999999999999999
        response = api_session.post(f"{BASE_URL}/pet", json=pet_payload)
        assert response.status_code == 400, (
            f"Expected error status 400, got '{response.status_code}'"
        )

    def test_get_pet_by_id(
        self, api_session: requests.Session, created_pet: Dict[str, Any]
    ):
        """
        This test retrieves an existing pet by {petId}
        Endpoint: GET https://petstore.swagger.io/v2/pet/{petId}
        """
        pet_id = created_pet["id"]
        response = api_session.get(f"{BASE_URL}/pet/{pet_id}")

        assert response.ok, (
            f"Expected successful response retrieving pet, got {response.status_code} "
            f"{response.text}"
        )
        assert response.status_code == 200, (
            f"Expected status code 200, got {response.status_code}"
        )
        # Verify the returned pet
        response_body = response.json()
        assert response_body["id"] == pet_id, (
            f"Expected fetched pet ID is {pet_id}, got {response_body.get('id')}"
        )
        assert response_body["name"] == created_pet["name"], (
            f"Expected fetched pet name is '{created_pet['name']}', "
            f"got '{response_body.get('name')}'"
        )

    @pytest.mark.parametrize(
        "mock_id",
        [
            0,
            -1,
            pytest.param("random", id="random"),
            pytest.param(
                9999999999999999999,
                marks=pytest.mark.xfail(
                    reason="FAIL: API returns NumberFormatException instead of 'Pet not found'"
                )
            ),
        ],
        indirect=True
    )
    def test_get_pet_not_found(self, api_session: requests.Session, mock_id: int):
        """
        This negative test tries to retrieve a non-existent pet
        Endpoint: GET https://petstore.swagger.io/v2/pet/{petId}
        """
        response = api_session.get(f"{BASE_URL}/pet/{mock_id}")

        assert not response.ok, (
            "Expected failure retrieving non-existent pet, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 404, (
            f"Expected status code 404 for missing pet, got {response.status_code}"
        )
        assert response.json().get("message") == "Pet not found", (
            "Expected 'Pet not found' message, "
            f"got {response.json().get('message')}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API returns 404 instead of documented 400 for invalid ID")
    @pytest.mark.parametrize(
        "invalid_id",
        [
            TestData.INVALID_ID_STRING,
            "12.34",
            "@#$%",
            "True",
        ]
    )
    def test_get_pet_invalid_id(self, api_session: requests.Session, invalid_id: str):
        """
        This negative test checks for a 400 error when an invalid ID is supplied
        Endpoint: GET https://petstore.swagger.io/v2/pet/{petId}
        """
        response = api_session.get(f"{BASE_URL}/pet/{invalid_id}")

        assert not response.ok, (
            "Expected failure retrieving pet with invalid ID, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 400, (
            f"Expected status code 400 for invalid ID, got {response.status_code}"
        )

    def test_update_pet_json(
        self, api_session: requests.Session, created_pet: Dict[str, Any]
    ):
        """
        This test updates an existing pet's status using PUT with JSON
        Endpoint: PUT https://petstore.swagger.io/v2/pet
        """
        updated_payload = created_pet.copy()
        updated_payload["status"] = "sold"
        updated_payload["name"] = created_pet["name"] + "_updated"

        response = api_session.put(f"{BASE_URL}/pet", json=updated_payload)

        assert response.ok, (
            f"Expected successful response updating pet, got {response.status_code} "
            f"{response.text}"
        )
        assert response.status_code == 200, (
            f"Expected status code 200 after update, got {response.status_code}"
        )

        # Verify the updated pet
        response_body = response.json()
        assert response_body["name"] == updated_payload["name"], (
            f"Expected updated name '{updated_payload['name']}', "
            f"got '{response_body.get('name')}'"
        )
        assert response_body["status"] == "sold", (
            f"Expected updated status 'sold', got '{response_body.get('status')}'"
        )

    @pytest.mark.xfail(reason="FAIL: API returns 500 instead of 400 for invalid ID format on PUT")
    @pytest.mark.parametrize(
        "invalid_id",
        [
            TestData.INVALID_ID_STRING,
            "12.34",
            "@#$%",
            "True",
        ]
    )
    def test_update_pet_invalid_id(self, api_session: requests.Session, invalid_id: str):
        """
        This negative test tries to update the pet with invalid ID format (expects 400)
        Endpoint: PUT https://petstore.swagger.io/v2/pet
        """
        invalid_payload = {"id": invalid_id}
        response = api_session.put(f"{BASE_URL}/pet", json=invalid_payload)

        assert not response.ok, (
            "Expected failure updating pet with invalid ID, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 400, (
            f"Expected status code 400 for invalid ID, got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API returns 200 or 500 instead of 404 for non-existent pet on PUT")
    @pytest.mark.parametrize(
        "mock_id",
        [
            0,
            -1,
            pytest.param("random", id="random"),
            9999999999999999999,
        ],
        indirect=True
    )
    def test_update_pet_not_found(self, api_session: requests.Session, mock_id: int):
        """
        This negative test tries to update the non-existent pet (expects 404)
        Endpoint: PUT https://petstore.swagger.io/v2/pet
        """
        not_found_payload = {"id": mock_id, "name": "non-existent pet"}
        response = api_session.put(f"{BASE_URL}/pet", json=not_found_payload)

        assert not response.ok, (
            "Expected failure updating non-existent pet, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 404, (
            f"Expected status code 404 for non-existent pet, got {response.status_code}"
        )

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            "",
            pytest.param(
                TestData.INVALID_JSON_STRING,
                marks=pytest.mark.xfail(
                    reason="FAIL: API returns 400 instead of documented 405 "
                           "for invalid JSON on PUT"
                )
            ),
            pytest.param(
                TestData.MALFORMED_JSON_STRING,
                marks=pytest.mark.xfail(
                    reason="FAIL: API returns 400 instead of documented 405 "
                           "for malformed JSON on PUT"
                )
            ),
            None,
        ]
    )
    def test_update_pet_validation_exception(
        self, api_session: requests.Session, invalid_payload: Any
    ):
        """ 
        This negative test tries to update pet with invalid payload (expects 405)
        Endpoint: PUT https://petstore.swagger.io/v2/pet
        """
        response = api_session.put(
            f"{BASE_URL}/pet",
            data=invalid_payload,
            headers={"Content-Type": "application/json"}
        )

        assert not response.ok, (
            "Expected failure for empty body validation, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 405, (
            f"Expected status code 405 for validation exception, got {response.status_code}"
        )

    def test_update_pet_form_data(
        self, api_session: requests.Session, created_pet: Dict[str, Any]
    ):
        """
        This test updates a pet in the store with form data (POST)
        Endpoint: POST https://petstore.swagger.io/v2/pet/{petId}
        """
        pet_id = created_pet["id"]

        response = api_session.post(
            f"{BASE_URL}/pet/{pet_id}",
            data={
                "name": "updated_pet_name",
                "status": "pending"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.ok, (
            "Expected successful response updating via form data, "
            f"got {response.status_code} {response.text}"
        )
        assert response.status_code == 200, (
            f"Expected status code 200 after form update, got {response.status_code}"
        )

        # Verify that the update was successful
        get_response = api_session.get(f"{BASE_URL}/pet/{pet_id}")
        assert get_response.ok, (
            "Expected successful fetch after form update, "
            f"got {get_response.status_code} {get_response.text}"
        )
        assert get_response.json()["name"] == "updated_pet_name", (
            "Expected updated name 'updated_pet_name', "
            f"got '{get_response.json().get('name')}'"
        )
        assert get_response.json()["status"] == "pending", (
            "Expected updated status 'pending', "
            f"got '{get_response.json().get('status')}'"
        )

    @pytest.mark.xfail(reason="FAIL: API returns 200 instead of 405 for invalid form data on POST")
    @pytest.mark.parametrize(
        "invalid_form_data",
        [
            TestData.INVALID_FORM_DATA_STRING,
            "",
            TestData.MALFORMED_JSON_STRING_FULL,
            None,
        ]
    )
    def test_update_pet_form_data_invalid_input(
        self, api_session: requests.Session, created_pet: Dict[str, Any], invalid_form_data: Any
    ):
        """
        This negative test tries to update pet with invalid form data (expects 405)
        Endpoint: POST https://petstore.swagger.io/v2/pet/{petId}
        """
        pet_id = created_pet["id"]
        response = api_session.post(
            f"{BASE_URL}/pet/{pet_id}",
            data=invalid_form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert not response.ok, (
            "Expected failure for invalid form data, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 405, (
            f"Expected status code 405 for invalid input, got {response.status_code}"
        )

    def test_update_pet_form_data_content_type_mismatch(
        self,
        api_session: requests.Session,
        created_pet: Dict[str, Any]
    ):
        """
        This negative test verifies that sending application/json to a form data endpoint
        returns a proper 415 Unsupported Media Type.
        Endpoint: POST https://petstore.swagger.io/v2/pet/{petId}
        """
        pet_id = created_pet["id"]
        response = api_session.post(
            f"{BASE_URL}/pet/{pet_id}",
            json={"name": "updated_name", "status": "sold"}
        )
        assert response.status_code == 415, (
            f"Expected status code 415 for Unsupported Media Type, got {response.status_code}"
        )

    @pytest.mark.parametrize("status", ["available", "pending", "sold"])
    def test_find_pet_by_status(self, api_session: requests.Session, status: str):
        """
        This test finds pets by different statuses
        Endpoint: GET https://petstore.swagger.io/v2/pet/findByStatus
        """
        response = api_session.get(
            f"{BASE_URL}/pet/findByStatus",
            params={"status": status}
        )

        assert response.ok, (
            f"Expected successful response finding by status '{status}', "
            f"got {response.status_code} {response.text}"
        )
        assert response.status_code == 200, (
            f"Expected status code 200, got {response.status_code}"
        )

        # Verify the returned pets' status
        response_body = response.json()
        assert isinstance(response_body, list), (
            f"Expected list of pets in response, got {type(response_body)}"
        )
        if len(response_body) > 0:
            assert response_body[0]["status"] == status, (
                f"Expected pet status to be '{status}', "
                f"got '{response_body[0].get('status')}'"
            )

    @pytest.mark.xfail(
        reason="FAIL: API returns 200 instead of 400 for invalid status value")
    @pytest.mark.parametrize(
        "invalid_status",
        [
            TestData.INVALID_STATUS_STRING,
            " ",
            "!@#",
            "123",
            "",
        ]
    )
    def test_find_pet_by_invalid_status(self, api_session: requests.Session, invalid_status: str):
        """
        This negative test checks for a 400 error when an invalid status is supplied
        Endpoint: GET https://petstore.swagger.io/v2/pet/findByStatus
        """
        response = api_session.get(
            f"{BASE_URL}/pet/findByStatus",
            params={"status": invalid_status}
        )

        assert not response.ok, (
            "Expected failure for invalid status, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 400, (
            f"Expected status code 400 for invalid status, got {response.status_code}"
        )

    def test_delete_pet(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This test deletes a pet by petId
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        """
        create_response = api_session.post(f"{BASE_URL}/pet", json=pet_payload)
        assert create_response.ok, (
            f"Failed to setup pet for deletion test: {create_response.status_code} "
            f"{create_response.text}"
        )
        pet_id = pet_payload["id"]

        response = api_session.delete(f"{BASE_URL}/pet/{pet_id}")
        assert response.ok, (
            f"Expected successful deletion response, got {response.status_code} "
            f"{response.text}"
        )
        assert response.status_code == 200, (
            f"Expected status code 200 for deletion, got {response.status_code}"
        )

        # Verify that cannot retreive the deleted pet
        get_response = api_session.get(f"{BASE_URL}/pet/{pet_id}")
        assert not get_response.ok, (
            "Expected failure retrieving deleted pet, but got success with status "
            f"{get_response.status_code}"
        )
        assert get_response.status_code == 404, (
            f"Expected status 404 for deleted pet, got {get_response.status_code}"
        )

    def test_delete_pet_twice(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This negative test attempts to delete a pet that has already been deleted.
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        """
        api_session.post(f"{BASE_URL}/pet", json=pet_payload)
        pet_id = pet_payload["id"]
        api_session.delete(f"{BASE_URL}/pet/{pet_id}")

        response = api_session.delete(f"{BASE_URL}/pet/{pet_id}")
        assert response.status_code == 404, (
            f"Expected status code 404 for already deleted pet, got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API allows unauthenticated deletions instead of returning 401"
    )
    def test_delete_pet_unauthenticated(
        self, api_session: requests.Session, pet_payload: Dict[str, Any]
    ):
        """
        This negative test verifies that deleting a pet requires an API key.
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        """
        api_session.post(f"{BASE_URL}/pet", json=pet_payload)
        pet_id = pet_payload["id"]

        # Ensure no api_key is sent
        response = api_session.delete(f"{BASE_URL}/pet/{pet_id}", headers={"api_key": None})
        assert response.status_code == 401, (
            f"Expected status code 401 Unauthorized without api_key, got {response.status_code}"
        )

    @pytest.mark.xfail(
        reason="FAIL: API returns 404 instead of documented 400 for invalid ID format")
    @pytest.mark.parametrize(
        "invalid_id",
        [
            TestData.INVALID_ID_STRING,
            "12.34",
            "@#$%",
            "True",
        ]
    )
    def test_delete_pet_invalid_id(self, api_session: requests.Session, invalid_id: str):
        """
        This negative test checks for a 400 error when an invalid ID is supplied to DELETE
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        """
        response = api_session.delete(f"{BASE_URL}/pet/{invalid_id}")

        assert not response.ok, (
            "Expected failure deleting pet with invalid ID, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 400, (
            f"Expected status code 400 for invalid ID, got {response.status_code}"
        )

    @pytest.mark.parametrize(
        "mock_id",
        [
            0,
            -1,
            pytest.param("random", id="random"),
            9999999999999999999,
        ],
        indirect=True
    )
    def test_delete_pet_not_found(self, api_session: requests.Session, mock_id: int):
        """ 
        This negative test checks for a 404 error
        when a non-existent pet ID is supplied to DELETE
        Endpoint: DELETE https://petstore.swagger.io/v2/pet/{petId}
        """
        response = api_session.delete(f"{BASE_URL}/pet/{mock_id}")

        assert not response.ok, (
            "Expected failure deleting non-existent pet, but request succeeded "
            f"with status {response.status_code}"
        )
        assert response.status_code == 404, (
            f"Expected status code 404 for non-existent pet, got {response.status_code}"
        )
