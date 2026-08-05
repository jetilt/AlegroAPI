# AlegroAPI Test Automation Framework

This project is a API test automation framework built to test the [Petstore Swagger API](https://petstore.swagger.io/). Introduces a dual implementations with both **Playwright** and **Requests** libraries for the /pet endpoint

## 🚀 Technologies Used
- **Python 3.11+**
- **Pytest**
- **Playwright (`pytest-playwright`)**: using `APIRequestContext`
- **Requests**
- **GitHub Actions**

## ⚙️ Installation

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

## 🧪 Running Tests

Run the entire test suite (both Playwright and Requests implementations) with a single command:
```bash
pytest -v
```

### Running specific suites
To run only the **Playwright API** tests:
```bash
pytest -v tests/test_petstore_api.py
```

To run only the **Requests** tests:
```bash
pytest -v tests/test_petstore_api_requests.py
```
