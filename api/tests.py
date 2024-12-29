import time
from typing import Dict, Optional, Tuple

import requests
from loguru import logger

# Global variables
BASE_URL = "https://mcs-285321057562.us-central1.run.app"


def get_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """Generate headers for API requests"""
    headers = {}  # Start with empty headers
    if api_key:
        # FastAPI's Header dependency expects the raw header name
        headers["api-key"] = api_key
    return headers


def make_request(
    method: str,
    url: str,
    headers: Dict = None,
    json: Dict = None,
    timeout: int = 30,
) -> requests.Response:
    """Make HTTP request with consistent logging"""
    try:
        logger.debug(f"Making {method} request to {url}")
        logger.debug(f"Headers: {headers}")
        if json:
            logger.debug(f"Request body: {json}")

        response = requests.request(
            method, url, headers=headers, json=json, timeout=timeout
        )

        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(
            f"Response body: {response.text[:500]}"
        )  # First 500 chars

        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise


def setup_test_environment() -> Tuple[bool, Optional[str]]:
    """Setup test environment and get API key"""
    try:
        logger.info("Setting up test environment")
        response = make_request("POST", f"{BASE_URL}/v1/generate-key")
        response.raise_for_status()
        api_key = response.json()["api_key"]
        logger.success(
            f"Successfully generated API key: {api_key[:8]}..."
        )
        return True, api_key
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        return False, None


def test_health_check() -> bool:
    """Test health check endpoint"""
    try:
        logger.info("Testing health check endpoint")
        response = make_request("GET", f"{BASE_URL}/health")
        response.raise_for_status()
        assert response.json()["status"] == "healthy"
        logger.success("Health check test passed")
        return True
    except Exception as e:
        logger.error(f"Health check test failed: {str(e)}")
        return False


def test_api_key_validation(api_key: str) -> bool:
    """Test API key validation"""
    try:
        logger.info("Testing API key validation")
        headers = get_headers(api_key)

        # First request - just like FastAPI's Header dependency
        response = make_request(
            "GET", f"{BASE_URL}/v1/validate-key", headers=headers
        )
        response.raise_for_status()
        assert response.json()["status"] == "API key is valid"

        logger.success("API key validation test passed")
        return True
    except Exception as e:
        logger.error(f"API key validation test failed: {str(e)}")
        return False


def test_single_patient_flow(api_key: str) -> bool:
    """Test complete flow for single patient"""
    try:
        logger.info("Testing single patient flow")
        headers = get_headers(api_key)

        patient_data = {
            "patient_id": "TEST_001",
            "case_description": "Patient presents with acute respiratory infection",
        }

        # Create patient
        create_response = make_request(
            "POST",
            f"{BASE_URL}/v1/medical-coder/run",
            headers=headers,
            json=patient_data,
        )
        create_response.raise_for_status()

        # Get patient
        time.sleep(2)  # Wait for processing
        get_response = make_request(
            "GET",
            f"{BASE_URL}/v1/medical-coder/patient/{patient_data['patient_id']}",
            headers=headers,
        )
        get_response.raise_for_status()

        # Delete patient
        delete_response = make_request(
            "DELETE",
            f"{BASE_URL}/v1/medical-coder/patient/{patient_data['patient_id']}",
            headers=headers,
        )
        delete_response.raise_for_status()

        logger.success("Single patient flow test passed")
        return True
    except Exception as e:
        logger.error(f"Single patient flow test failed: {str(e)}")
        return False


def run_all_tests() -> Dict[str, bool]:
    """Run all tests and return results"""
    logger.info("Starting full test suite")

    # Setup
    setup_success, api_key = setup_test_environment()
    if not setup_success:
        logger.error("Test suite setup failed")
        return {"setup": False}

    # Run critical tests first
    test_results = {
        "health_check": test_health_check(),
        "api_key_validation": test_api_key_validation(api_key),
        "single_patient_flow": test_single_patient_flow(api_key),
    }

    # Log results
    passed_tests = sum(
        1 for result in test_results.values() if result
    )
    total_tests = len(test_results)
    logger.info(
        f"Test suite completed. Passed {passed_tests}/{total_tests} tests"
    )

    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")

    return test_results


def print_test_summary(results: Dict[str, bool]):
    """Print a formatted summary of test results"""
    print("\nTest Results Summary:")
    print("-" * 40)
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    print("-" * 40)


if __name__ == "__main__":
    results = run_all_tests()
    print_test_summary(results)
