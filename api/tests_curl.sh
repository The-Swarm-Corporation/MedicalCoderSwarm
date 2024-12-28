#!/bin/bash

BASE_URL="https://mcs-285321057562.us-central1.run.app/v1"

# Patient cases
patient_case_1='{
    "patient_id": "Patient-001",
    "case_description": "Patient: 45-year-old White Male\nLocation: New York, NY\nLab Results:\n- egfr \n- 59 ml / min / 1.73\n- non african-american\n"
}'

patient_case_2='{
    "patient_id": "Patient-002",
    "case_description": "Patient: 60-year-old Female\nLocation: Los Angeles, CA\nLab Results:\n- Hemoglobin\n- 10.5 g/dL\n- Anemic\n"
}'

batch_cases='{
    "cases": [
        {
            "patient_id": "Patient-001",
            "case_description": "Patient: 45-year-old White Male\nLocation: New York, NY\nLab Results:\n- egfr \n- 59 ml / min / 1.73\n- non african-american\n"
        },
        {
            "patient_id": "Patient-002",
            "case_description": "Patient: 60-year-old Female\nLocation: Los Angeles, CA\nLab Results:\n- Hemoglobin\n- 10.5 g/dL\n- Anemic\n"
        }
    ]
}'

# Test functions
test_run_medical_coder() {
    echo "Running test: Run MedicalCoderSwarm"
    curl -X POST "${BASE_URL}/run" -H "Content-Type: application/json" -d "$patient_case_1"
    echo
}

test_get_patient() {
    echo "Running test: Get Patient"
    curl -X GET "${BASE_URL}/patient/Patient-001"
    echo
}

test_get_all_patients() {
    echo "Running test: Get All Patients"
    curl -X GET "${BASE_URL}/patients"
    echo
}

test_delete_patient() {
    echo "Running test: Delete Patient"
    curl -X DELETE "${BASE_URL}/patient/Patient-001"
    echo
}

test_delete_all_patients() {
    echo "Running test: Delete All Patients"
    curl -X DELETE "${BASE_URL}/patients"
    echo
}

test_health_check() {
    echo "Running test: Health Check"
    curl -X GET "${BASE_URL}/health"
    echo
}

test_run_medical_coder_batch() {
    echo "Running test: Run Batch MedicalCoderSwarm"
    curl -X POST "${BASE_URL}/run-batch" -H "Content-Type: application/json" -d "$batch_cases"
    echo
}

# Run all tests
echo "Starting all tests..."
test_health_check
test_run_medical_coder
test_get_patient
curl -X POST "${BASE_URL}/run" -H "Content-Type: application/json" -d "$patient_case_2" # Additional run
test_get_all_patients
test_delete_patient
test_delete_all_patients
test_run_medical_coder_batch

echo "All tests completed."
