# AlegroAPI Test Automation Framework

This project is an API test automation framework built to test the [Petstore Swagger API](https://petstore.swagger.io/). It introduces dual implementations with both **Playwright** (`APIRequestContext`) and **Requests** libraries for the `/v2/pet` endpoints.

## Technologies Used
- **Python 3.11+**
- **Pytest**
- **Playwright (`pytest-playwright`)**: using `APIRequestContext`
- **Requests**
- **GitHub Actions**

## Installation

Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Install Playwright browsers:
   ```bash
   playwright install
   ```

## Security & Authentication Testing

The Petstore Swagger specification defines two distinct security schemes:
- **OAuth2 (`petstore_auth`)**: Protects state-changing endpoints (`POST /pet`, `PUT /pet`, `DELETE /pet/{petId}`) and status search (`GET /pet/findByStatus`). Verified by sending requests with missing or empty `Authorization` headers.
- **API Key (`api_key`)**: Protects single-resource retrieval (`GET /pet/{petId}`) and is an optional header parameter on `DELETE /pet/{petId}`. Verified by sending requests with missing or invalid `api_key` headers.

> **Note**: The public demo API does not enforce these documented authentication requirements. The security test suites (`tests/test_auth_security.py` and `tests/test_auth_security_requests.py`) verify both security schemes, expecting `401 Unauthorized` or `403 Forbidden`. Because the public server permits unauthenticated access, these tests are marked with `@pytest.mark.xfail` to track compliance vulnerabilities cleanly.

## Running Tests

Run the entire test suite (both Playwright and Requests implementations) with a single command:
```bash
pytest -v
```

### Running specific suites
To run only the **Playwright API** tests:
```bash
pytest -v tests/test_petstore_api.py
```
```bash
pytest -v tests/test_auth_security.py
```

To run only the **Requests** tests:
```bash
pytest -v tests/test_petstore_api_requests.py
```
```bash
pytest -v tests/test_auth_security_requests.py
```
