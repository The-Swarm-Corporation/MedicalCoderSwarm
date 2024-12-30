from mcs import MCSClient

patient_case = """
Patient: 45-year-old White Male
Location: New York, NY

Lab Results:
- egfr 
- 59 ml / min / 1.73
- non african-american

"""

with MCSClient() as client:
    response = client.run_medical_coder("P123", patient_case)
    print(response)