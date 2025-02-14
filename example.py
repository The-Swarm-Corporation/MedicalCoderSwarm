from mcs.main import MedicalCoderSwarm

if __name__ == "__main__":
    # Extended Example Patient Case
    patient_case = """
    Patient Information:
    - Name: John Doe
    - Age: 45
    - Gender: Male
    - Ethnicity: White
    - Location: New York, NY
    - BMI: 28.5 (Overweight)
    - Occupation: Office Worker

    Presenting Complaints:
    - Persistent fatigue for 3 months
    - Swelling in lower extremities
    - Difficulty concentrating (brain fog)
    - Increased frequency of urination

    Medical History:
    - Hypertension (diagnosed 5 years ago, poorly controlled)
    - Type 2 Diabetes Mellitus (diagnosed 2 years ago, HbA1c: 8.2%)
    - Family history of chronic kidney disease (mother)

    Current Medications:
    - Lisinopril 20 mg daily
    - Metformin 1000 mg twice daily
    - Atorvastatin 10 mg daily

    Lab Results:
    - eGFR: 59 ml/min/1.73m² (Non-African American)
    - Serum Creatinine: 1.5 mg/dL
    - BUN: 22 mg/dL
    - Potassium: 4.8 mmol/L
    - HbA1c: 8.2%
    - Urinalysis: Microalbuminuria detected (300 mg/g creatinine)

    Vital Signs:
    - Blood Pressure: 145/90 mmHg
    - Heart Rate: 78 bpm
    - Respiratory Rate: 16 bpm
    - Temperature: 98.6°F
    - Oxygen Saturation: 98%

    Differential Diagnoses to Explore:
    1. Chronic Kidney Disease (CKD) Stage 3
    2. Diabetic Nephropathy
    3. Secondary Hypertension (due to CKD)
    4. Fatigue related to poorly controlled diabetes

    Specialist Consultations Needed:
    - Nephrologist
    - Endocrinologist
    - Dietitian for diabetic and CKD management

    Initial Management Recommendations:
    - Optimize blood pressure control (<130/80 mmHg target for CKD)
    - Glycemic control improvement (target HbA1c <7%)
    - Lifestyle modifications: low-sodium, renal-friendly diet
    - Referral to nephrologist for further evaluation
    """

    # Initialize the MedicalCoderSwarm with the detailed patient case
    swarm = MedicalCoderSwarm(
        patient_id="Patient-001",
        max_loops=1,
    )

    # Run the swarm on the patient case
    output = swarm.run(task=patient_case)

    # Print the system's state after processing
    print(output)
