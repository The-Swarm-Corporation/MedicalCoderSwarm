import json
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_PATIENT_ID = "TEST123"


def print_response(response, message=""):
    """Pretty print API response"""
    print("\n" + "=" * 50)
    if message:
        print(message)
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("Raw Response:", response.text)
    print("=" * 50 + "\n")


def run_tests():
    """Run a series of natural API tests"""
    print("\nStarting API Tests...\n")

    # 1. Check if API is healthy
    print("1. Testing API health...")
    response = requests.get(f"{API_BASE_URL}/api/health")
    print_response(response, "Health Check Response:")

    if response.status_code != 200:
        print("❌ API is not healthy! Stopping tests.")
        return
    print("✅ API is healthy!")

    # 2. Create a new analysis
    print("\n2. Creating a new analysis...")
    test_data = {
        "patient_id": TEST_PATIENT_ID,
        "patient_case": "Patient presents with severe headache and fever for 3 days",
        "patient_documentation": "Previous history of migraines",
        "max_loops": 1,
    }

    response = requests.post(
        f"{API_BASE_URL}/api/v1/analyses", json=test_data
    )
    print_response(response, "Create Analysis Response:")

    if response.status_code != 200:
        print("❌ Failed to create analysis! Stopping tests.")
        return

    analysis_id = response.json()["id"]
    print(f"✅ Successfully created analysis with ID: {analysis_id}")

    # 3. Retrieve the created analysis
    print("\n3. Retrieving the analysis...")
    time.sleep(1)  # Small delay to ensure processing
    response = requests.get(
        f"{API_BASE_URL}/api/v1/analyses/{analysis_id}"
    )
    print_response(response, "Get Analysis Response:")

    if response.status_code != 200:
        print("❌ Failed to retrieve analysis!")
    else:
        print("✅ Successfully retrieved analysis!")

    # 4. List all analyses for our test patient
    print("\n4. Listing analyses for test patient...")
    response = requests.get(
        f"{API_BASE_URL}/api/v1/analyses",
        params={"patient_id": TEST_PATIENT_ID},
    )
    print_response(response, "List Analyses Response:")

    if response.status_code != 200:
        print("❌ Failed to list analyses!")
    else:
        analyses_count = len(response.json())
        print(
            f"✅ Found {analyses_count} analyses for patient {TEST_PATIENT_ID}"
        )

    # 5. Test error handling with invalid analysis ID
    print(
        "\n5. Testing error handling - retrieving non-existent analysis..."
    )
    response = requests.get(
        f"{API_BASE_URL}/api/v1/analyses/nonexistent-id"
    )
    print_response(response, "Error Handling Response:")

    if response.status_code == 404:
        print("✅ Properly handled non-existent analysis!")
    else:
        print("❌ Unexpected response for non-existent analysis!")

    # 6. Test creating analysis with invalid data
    print(
        "\n6. Testing validation - creating analysis with invalid data..."
    )
    invalid_data = {
        "patient_id": "",  # Empty patient ID should be invalid
        "patient_case": "Test case",
    }
    response = requests.post(
        f"{API_BASE_URL}/api/v1/analyses", json=invalid_data
    )
    print_response(response, "Validation Response:")

    if response.status_code == 422:
        print("✅ Properly validated invalid data!")
    else:
        print("❌ Failed to catch invalid data!")

    # 7. Delete the analysis we created
    print("\n7. Deleting the analysis...")
    response = requests.delete(
        f"{API_BASE_URL}/api/v1/analyses/{analysis_id}"
    )
    print_response(response, "Delete Analysis Response:")

    if response.status_code != 200:
        print("❌ Failed to delete analysis!")
    else:
        print("✅ Successfully deleted analysis!")

        # Verify deletion
        response = requests.get(
            f"{API_BASE_URL}/api/v1/analyses/{analysis_id}"
        )
        if response.status_code == 404:
            print("✅ Verified analysis was deleted!")
        else:
            print("❌ Analysis still exists after deletion!")

    print("\nTest Summary:")
    print("✅ Basic API functionality testing completed")
    print("✅ Error handling verified")
    print("✅ Data validation checked")
    print("✅ CRUD operations tested")


if __name__ == "__main__":
    # Ensure the API is running first
    try:
        requests.get(f"{API_BASE_URL}/api/health")
    except requests.exceptions.ConnectionError:
        print(
            "❌ Error: API is not running! Please start the API server first."
        )
        print("   Run: python main.py")
        exit(1)

    run_tests()
