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


def test_health_check():
    print("Testing: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_run_medical_coder():
    print("Testing: Run MedicalCoderSwarm")
    response = requests.post(
        f"{BASE_URL}/medical-coder/run", json=patient_case_1
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_get_patient():
    print("Testing: Get Patient Data")
    response = requests.get(
        f"{BASE_URL}/medical-coder/patient/{patient_case_1['patient_id']}"
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_get_all_patients():
    print("Testing: Get All Patients")
    response = requests.get(f"{BASE_URL}/medical-coder/patients")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_delete_patient():
    print("Testing: Delete Patient Data")
    response = requests.delete(
        f"{BASE_URL}/medical-coder/patient/{patient_case_1['patient_id']}"
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_delete_all_patients():
    print("Testing: Delete All Patients")
    response = requests.delete(f"{BASE_URL}/medical-coder/patients")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_run_batch_medical_coder():
    print("Testing: Run Batch MedicalCoderSwarm")
    batch_cases = {"cases": [patient_case_1, patient_case_2]}
    response = requests.post(
        f"{BASE_URL}/medical-coder/run-batch", json=batch_cases
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")


def run_all_tests():
    test_health_check()
    test_run_medical_coder()
    test_get_patient()
    test_get_all_patients()
    test_delete_patient()
    test_delete_all_patients()
    test_run_batch_medical_coder()


if __name__ == "__main__":
    run_all_tests()
