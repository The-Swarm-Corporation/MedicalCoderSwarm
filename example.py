from mcs.main import MedicalCoderSwarm
import json

if __name__ == "__main__":
    # Example patient case
    patient_case = """
    Patient: 45-year-old White Male
    Location: New York, NY

    Lab Results:
    - egfr 
    - 59 ml / min / 1.73
    - non african-american
    
    """

    swarm = MedicalCoderSwarm(
        patient_id="Patient-001",
        max_loops=1,
        patient_documentation="",
        output_folder_path="reports",
    )

    swarm.run(task=patient_case)

    print(json.dumps(swarm.to_dict()))
