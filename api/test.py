import requests
import json

BASE_URL = "http://127.0.0.1:8000/v1/medical-coder"

# Mock data for testing
patient_case_1 = {
    "patient_id": "Patient-001",
    "case_description": "Patient: 45-year-old White Male\nLocation: New York, NY\nLab Results:\n- egfr \n- 59 ml / min / 1.73\n- non african-american\n"
}

patient_case_2 = {
    "patient_id": "Patient-002",
    "case_description": "Patient: 60-year-old Female\nLocation: Los Angeles, CA\nLab Results:\n- Hemoglobin\n- 10.5 g/dL\n- Anemic\n"
}

def test_run_medical_coder():
    """Test running the MedicalCoderSwarm with a new patient case."""
    response = requests.post(f"{BASE_URL}/run", json=patient_case_1)
    print("Run MedicalCoderSwarm Response:", response.status_code, response.json())

def test_get_patient():
    """Test retrieving data for an individual patient."""
    response = requests.get(f"{BASE_URL}/patient/Patient-001")
    print("Get Patient Response:", response.status_code, response.json())

def test_get_all_patients():
    """Test retrieving all patients' data."""
    response = requests.get(f"{BASE_URL}/patients")
    print("Get All Patients Response:", response.status_code, response.json())

def test_delete_patient():
    """Test deleting a specific patient's data."""
    response = requests.delete(f"{BASE_URL}/patient/Patient-001")
    print("Delete Patient Response:", response.status_code, response.json())

def test_delete_all_patients():
    """Test deleting all patients' data."""
    response = requests.delete(f"{BASE_URL}/patients")
    print("Delete All Patients Response:", response.status_code, response.json())

def run_all_tests():
    """Run all tests in sequence."""
    print("Testing: Run MedicalCoderSwarm")
    test_run_medical_coder()

    print("\nTesting: Get Patient")
    test_get_patient()

    print("\nTesting: Run Another MedicalCoderSwarm")
    requests.post(f"{BASE_URL}/run", json=patient_case_2)

    print("\nTesting: Get All Patients")
    test_get_all_patients()

    print("\nTesting: Delete Patient")
    test_delete_patient()

    print("\nTesting: Delete All Patients")
    test_delete_all_patients()

if __name__ == "__main__":
    run_all_tests()
