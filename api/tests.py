import json
import requests
from loguru import logger

# Configure logger
logger.add("test_api.log", rotation="10 MB")

BASE_URL = "https://mcs-285321057562.us-central1.run.app/"  # Update this with your actual base URL

def test_health_check():
    """Test health check endpoint"""
    logger.info("Testing health check endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        logger.info("Health check test passed")
        return True
    except Exception as e:
        logger.error(f"Health check test failed: {str(e)}")
        return False

def test_rate_limits():
    """Test rate limits endpoint"""
    logger.info("Testing rate limits endpoint")
    try:
        response = requests.get(f"{BASE_URL}/rate-limits")
        assert response.status_code == 200
        data = response.json()
        assert "daily_requests_remaining" in data
        assert "hourly_requests_remaining" in data
        logger.info("Rate limits test passed")
        return True
    except Exception as e:
        logger.error(f"Rate limits test failed: {str(e)}")
        return False

def test_run_medical_coder():
    """Test running medical coder for single patient"""
    logger.info("Testing medical coder single patient endpoint")
    try:
        test_case = {
            "patient_id": "test123",
            "case_description": "Test case description for patient with chest pain and shortness of breath"
        }
        response = requests.post(f"{BASE_URL}/v1/medical-coder/run", json=test_case)
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == "test123"
        assert "case_data" in data
        logger.info("Medical coder single patient test passed")
        logger.info(f"Response data: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Medical coder single patient test failed: {str(e)}")
        return False

def test_get_patient_data():
    """Test retrieving patient data"""
    logger.info("Testing get patient data endpoint")
    try:
        # First create a test patient
        test_case = {
            "patient_id": "test456",
            "case_description": "Test case for data retrieval"
        }
        # Create the patient first
        create_response = requests.post(f"{BASE_URL}/v1/medical-coder/run", json=test_case)
        assert create_response.status_code == 200

        # Then retrieve the patient data
        response = requests.get(f"{BASE_URL}/v1/medical-coder/patient/test456")
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == "test456"
        logger.info("Get patient data test passed")
        logger.info(f"Retrieved data: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Get patient data test failed: {str(e)}")
        return False

def test_get_all_patients():
    """Test retrieving all patients"""
    logger.info("Testing get all patients endpoint")
    try:
        response = requests.get(f"{BASE_URL}/v1/medical-coder/patients")
        assert response.status_code == 200
        data = response.json()
        assert "patients" in data
        logger.info("Get all patients test passed")
        logger.info(f"Number of patients retrieved: {len(data['patients'])}")
        return True
    except Exception as e:
        logger.error(f"Get all patients test failed: {str(e)}")
        return False

def test_run_medical_coder_batch():
    """Test batch processing of patient cases"""
    logger.info("Testing medical coder batch endpoint")
    try:
        test_batch = {
            "cases": [
                {
                    "patient_id": "batch1", 
                    "case_description": "Patient presents with severe migraine"
                },
                {
                    "patient_id": "batch2", 
                    "case_description": "Patient diagnosed with type 2 diabetes"
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/v1/medical-coder/run-batch", json=test_batch)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        logger.info("Medical coder batch test passed")
        logger.info(f"Batch processing results: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"Medical coder batch test failed: {str(e)}")
        return False

def test_delete_patient_data():
    """Test deleting patient data"""
    logger.info("Testing delete patient data endpoint")
    try:
        # First create a test patient
        test_case = {
            "patient_id": "delete_test",
            "case_description": "Test case for deletion"
        }
        # Create the patient
        create_response = requests.post(f"{BASE_URL}/v1/medical-coder/run", json=test_case)
        assert create_response.status_code == 200

        # Then delete the patient
        response = requests.delete(f"{BASE_URL}/v1/medical-coder/patient/delete_test")
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == "delete_test"
        assert data["message"] == "Patient data deleted successfully"
        logger.info("Delete patient data test passed")
        return True
    except Exception as e:
        logger.error(f"Delete patient data test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and generate report"""
    logger.info("Starting test suite execution")
    
    test_results = {
        "total_tests": 7,
        "passed": 0,
        "failed": 0,
        "failures": []
    }

    tests = [
        test_health_check,
        test_rate_limits,
        test_run_medical_coder,
        test_get_patient_data,
        test_get_all_patients,
        test_run_medical_coder_batch,
        test_delete_patient_data
    ]

    for test in tests:
        try:
            if test():
                test_results["passed"] += 1
                logger.success(f"{test.__name__} passed")
            else:
                test_results["failed"] += 1
                test_results["failures"].append({
                    "test_name": test.__name__,
                    "error": "Test returned False"
                })
        except Exception as e:
            test_results["failed"] += 1
            test_results["failures"].append({
                "test_name": test.__name__,
                "error": str(e)
            })
            logger.error(f"{test.__name__} failed: {str(e)}")
    
    # Generate report
    success_rate = (test_results["passed"] / test_results["total_tests"]) * 100
    
    report = f"""
Test Execution Report
====================
Total Tests: {test_results['total_tests']}
Passed: {test_results['passed']}
Failed: {test_results['failed']}
Success Rate: {success_rate:.2f}%

Failed Tests:
"""
    
    if test_results["failures"]:
        for failure in test_results["failures"]:
            report += f"\n- {failure['test_name']}: {failure['error']}"
    else:
        report += "\nNone"

    logger.info("Test suite execution completed")
    return report

if __name__ == "__main__":
    print(run_all_tests())