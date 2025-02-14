import requests

BASE_URL = "http://localhost:8080"


def test_health_check():
    """Test the health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert (
        response.status_code == 200
    ), f"Health check failed: {response.text}"
    print("Health check passed:", response.json())


def test_run_medical_coder():
    """Test the medical coder run endpoint."""
    payload = {
        "patient_id": "patient_001",
        "patient_docs": "This is a sample patient documentation.",
        "case_description": "The patient has symptoms of fever and cough.",
        "summarization": True,
        "rag_url": "http://example.com/rag",
        "rag_api_key": "test-api-key",
    }
    response = requests.post(
        f"{BASE_URL}/v1/medical-coder/run", json=payload
    )
    assert (
        response.status_code == 200
    ), f"Run medical coder failed: {response.text}"
    print("Run medical coder passed:", response.json())


def test_run_medical_coder_batch():
    """Test the batch medical coder run endpoint."""
    payload = {
        "cases": [
            {
                "patient_id": "patient_002",
                "patient_docs": "Patient 002 documentation.",
                "case_description": "Symptoms of headache and nausea.",
                "summarization": True,
                "rag_url": None,
                "rag_api_key": None,
            },
            {
                "patient_id": "patient_003",
                "patient_docs": "Patient 003 documentation.",
                "case_description": "Symptoms of chest pain.",
                "summarization": False,
                "rag_url": "http://example.com/rag",
                "rag_api_key": "test-api-key",
            },
        ]
    }
    response = requests.post(
        f"{BASE_URL}/v1/medical-coder/run-batch", json=payload
    )
    assert (
        response.status_code == 200
    ), f"Run medical coder batch failed: {response.text}"
    print("Run medical coder batch passed:", response.json())


def test_get_patient_data():
    """Test retrieving patient data by ID."""
    patient_id = "patient_001"
    response = requests.get(
        f"{BASE_URL}/v1/medical-coder/patient/{patient_id}"
    )
    assert (
        response.status_code == 200
    ), f"Get patient data failed: {response.text}"
    print(
        f"Get patient data for {patient_id} passed:", response.json()
    )


def test_get_all_patients():
    """Test retrieving all patient data."""
    response = requests.get(f"{BASE_URL}/v1/medical-coder/patients")
    assert (
        response.status_code == 200
    ), f"Get all patients failed: {response.text}"
    print("Get all patients passed:", response.json())


if __name__ == "__main__":
    print("Starting API endpoint tests...")

    # Test health check
    test_health_check()

    # Test run medical coder
    test_run_medical_coder()

    # Test batch run medical coder
    test_run_medical_coder_batch()

    # Test get patient data
    test_get_patient_data()

    # Test get all patients
    test_get_all_patients()

    print("All tests passed!")
