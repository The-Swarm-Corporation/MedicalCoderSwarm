import json
import os
from datetime import timedelta

# Import the classes and functions to test
from mcs.main import (
    RAGAPI,
    KeyRotationPolicy,
    MedicalCoderSwarm,
    SecureDataHandler,
)


def test_medical_coder_swarm_initialization():
    """Test the initialization of MedicalCoderSwarm"""
    try:
        # Set up test environment
        os.environ["MASTER_KEY"] = "test_master_key"
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
        
        # Initialize swarm
        swarm = MedicalCoderSwarm(
            name="Test-Swarm",
            description="Test swarm for unit testing",
            patient_id="test_patient_001",
            rag_enabled=True,
            rag_url="http://test-rag-url",
            user_name="test_user"
        )
        
        # Verify initialization
        assert swarm.name == "Test-Swarm"
        assert swarm.description == "Test swarm for unit testing"
        assert swarm.rag_enabled == True
        assert swarm.rag_url == "http://test-rag-url"
        assert swarm.user_name == "test_user"
        
        print("✓ MedicalCoderSwarm initialization test passed")
        return True
    except AssertionError as e:
        print(f"✗ MedicalCoderSwarm initialization test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error in initialization test: {str(e)}")
        return False

def test_rag_api():
    """Test the RAGAPI class"""
    try:
        # Initialize RAGAPI
        rag = RAGAPI(base_url="http://test-url")
        
        # Test initialization
        assert rag.base_url == "http://test-url"
        
        # Note: We can't actually test the query_rag method without mocking HTTP requests
        # In a real implementation, you would want to mock the requests.post call
        
        print("✓ RAGAPI test passed")
        return True
    except AssertionError as e:
        print(f"✗ RAGAPI test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error in RAGAPI test: {str(e)}")
        return False

def test_secure_data_handler():
    """Test the SecureDataHandler class"""
    try:
        # Initialize SecureDataHandler
        handler = SecureDataHandler(
            master_key="test_master_key",
            key_storage_path="test_keys",
            rotation_policy=KeyRotationPolicy(
                rotation_interval=timedelta(days=30),
                key_overlap_period=timedelta(days=2)
            ),
            auto_rotate=True
        )
        
        # Test data encryption/decryption
        test_data = {"patient_id": "test_001", "data": "test_medical_data"}
        encrypted_data = handler.encrypt_data(test_data)
        decrypted_data = handler.decrypt_data(encrypted_data)
        
        assert isinstance(encrypted_data, str)
        assert isinstance(decrypted_data, dict)
        assert decrypted_data["patient_id"] == test_data["patient_id"]
        assert decrypted_data["data"] == test_data["data"]
        
        print("✓ SecureDataHandler test passed")
        return True
    except AssertionError as e:
        print(f"✗ SecureDataHandler test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error in SecureDataHandler test: {str(e)}")
        return False

def test_swarm_run():
    """Test the run method of MedicalCoderSwarm"""
    try:
        # Initialize swarm
        swarm = MedicalCoderSwarm(
            name="Test-Run-Swarm",
            patient_documentation="Test patient with symptoms of fever and cough",
            summarization=True
        )
        
        # Test run with basic task
        task = "Analyze symptoms and provide diagnosis"
        output = swarm.run(task=task)
        
        # Verify output structure
        assert output is not None
        assert isinstance(output, str)
        
        print("✓ Swarm run test passed")
        return True
    except AssertionError as e:
        print(f"✗ Swarm run test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error in swarm run test: {str(e)}")
        return False

def test_batched_run():
    """Test the batched_run method of MedicalCoderSwarm"""
    try:
        # Initialize swarm
        swarm = MedicalCoderSwarm(
            name="Test-Batch-Swarm",
            patient_documentation="Test patient documentation"
        )
        
        # Test batch run
        tasks = ["Task 1", "Task 2"]
        imgs = ["img1.jpg", "img2.jpg"]
        outputs = swarm.batched_run(tasks=tasks, imgs=imgs)
        
        # Verify outputs
        assert isinstance(outputs, list)
        assert len(outputs) == len(tasks)
        
        print("✓ Batched run test passed")
        return True
    except AssertionError as e:
        print(f"✗ Batched run test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error in batched run test: {str(e)}")
        return False

def test_to_dict_serialization():
    """Test the to_dict serialization method"""
    try:
        # Initialize swarm
        swarm = MedicalCoderSwarm(name="Test-Serialization-Swarm")
        
        # Get dictionary representation
        swarm_dict = swarm.to_dict()
        
        # Verify dictionary structure
        assert isinstance(swarm_dict, dict)
        assert "name" in swarm_dict
        assert "description" in swarm_dict
        assert "agents" in swarm_dict
        
        # Test JSON serialization
        json_str = json.dumps(swarm_dict)
        assert isinstance(json_str, str)
        
        print("✓ to_dict serialization test passed")
        return True
    except AssertionError as e:
        print(f"✗ to_dict serialization test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error in serialization test: {str(e)}")
        return False

def run_all_tests():
    """Run all test cases and report results"""
    test_results = {
        "initialization": test_medical_coder_swarm_initialization(),
        "rag_api": test_rag_api(),
        "secure_data": test_secure_data_handler(),
        "swarm_run": test_swarm_run(),
        "batched_run": test_batched_run(),
        "serialization": test_to_dict_serialization()
    }
    
    # Print summary
    print("\nTest Summary:")
    print("=" * 50)
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
    
    print("-" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests()