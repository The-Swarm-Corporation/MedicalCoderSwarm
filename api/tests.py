import requests

BASE_URL = "https://mcs-285321057562.us-central1.run.app/v1"

# Mock data
patient_case_1 = {
    "patient_id": "Patient-001",
    "case_description": "Patient: 45-year-old White Male\nLocation: New York, NY\nLab Results:\n- egfr \n- 59 ml / min / 1.73\n- non african-american\n",
}

patient_case_2 = {
    "patient_id": "Patient-002",
    "case_description": "Patient: 60-year-old Female\nLocation: Los Angeles, CA\nLab Results:\n- Hemoglobin\n- 10.5 g/dL\n- Anemic\n",
}


def generate_api_key():
    """Generate an API key using the API."""
    response = requests.post(f"{BASE_URL}/generate-key")
    if response.status_code == 200:
        api_key = response.json()["api_key"]
        print(f"Generated API Key: {api_key}\n")
        return api_key
    else:
        print(
            f"Failed to generate API key. Status Code: {response.status_code}"
        )
        print(f"Response: {response.text}\n")
        exit(1)


def test_health_check(api_key):
    print("Testing: Health Check")
    headers = {"api-key": api_key}
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}\n")
    except ValueError:
        print("No JSON response received.\n")


def test_run_medical_coder(api_key):
    print("Testing: Run MedicalCoderSwarm")
    headers = {"api-key": api_key}
    response = requests.post(
        f"{BASE_URL}/medical-coder/run",
        json=patient_case_1,
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_get_patient(api_key):
    print("Testing: Get Patient Data")
    headers = {"api-key": api_key}
    response = requests.get(
        f"{BASE_URL}/medical-coder/patient/{patient_case_1['patient_id']}",
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_get_all_patients(api_key):
    print("Testing: Get All Patients")
    headers = {"api-key": api_key}
    response = requests.get(
        f"{BASE_URL}/medical-coder/patients", headers=headers
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_delete_patient(api_key):
    print("Testing: Delete Patient Data")
    headers = {"api-key": api_key}
    response = requests.delete(
        f"{BASE_URL}/medical-coder/patient/{patient_case_1['patient_id']}",
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_delete_all_patients(api_key):
    print("Testing: Delete All Patients")
    headers = {"api-key": api_key}
    response = requests.delete(
        f"{BASE_URL}/medical-coder/patients", headers=headers
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_run_batch_medical_coder(api_key):
    print("Testing: Run Batch MedicalCoderSwarm")
    batch_cases = {"cases": [patient_case_1, patient_case_2]}
    headers = {"api-key": api_key}
    response = requests.post(
        f"{BASE_URL}/medical-coder/run-batch",
        json=batch_cases,
        headers=headers,
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def run_all_tests():
    api_key = generate_api_key()  # Generate and get the API key
    test_health_check(api_key)
    test_run_medical_coder(api_key)
    test_get_patient(api_key)
    test_get_all_patients(api_key)
    test_delete_patient(api_key)
    test_delete_all_patients(api_key)
    test_run_batch_medical_coder(api_key)


if __name__ == "__main__":
    run_all_tests()
