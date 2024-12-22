from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
from mcs.main import MedicalCoderSwarm

# Initialize FastAPI app
app = FastAPI(title="MedicalCoderSwarm API", version="1.0.0")

db_path = "medical_coder.db"

# Initialize SQLite database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Create patients table if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        patient_data TEXT
    )
    """
)
connection.commit()
connection.close()


# Pydantic models
class PatientCase(BaseModel):
    patient_id: str
    case_description: str


class QueryResponse(BaseModel):
    patient_id: str
    case_data: str


class QueryAllResponse(BaseModel):
    patients: List[QueryResponse]


# Function to fetch patient data from the database
def fetch_patient_data(patient_id: str) -> Optional[str]:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT patient_data FROM patients WHERE patient_id = ?",
        (patient_id,),
    )
    row = cursor.fetchone()
    connection.close()
    return row[0] if row else None


# Function to save patient data to the database
def save_patient_data(patient_id: str, patient_data: str):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO patients (patient_id, patient_data) VALUES (?, ?)",
        (patient_id, patient_data),
    )
    connection.commit()
    connection.close()


@app.post("/v1/medical-coder/run", response_model=QueryResponse)
def run_medical_coder(patient_case: PatientCase):
    """
    Run the MedicalCoderSwarm on a given patient case.
    """
    swarm = MedicalCoderSwarm(
        patient_id=patient_case.patient_id,
        max_loops=1,
        patient_documentation="",
    )
    swarm.run(task=patient_case.case_description)

    swarm_output = swarm.to_dict()
    save_patient_data(
        patient_case.patient_id, json.dumps(swarm_output)
    )

    return QueryResponse(
        patient_id=patient_case.patient_id,
        case_data=json.dumps(swarm_output),
    )


@app.get(
    "/v1/medical-coder/patient/{patient_id}",
    response_model=QueryResponse,
)
def get_patient_data(patient_id: str):
    """
    Retrieve patient data by patient ID.
    """
    patient_data = fetch_patient_data(patient_id)
    if not patient_data:
        raise HTTPException(
            status_code=404, detail="Patient not found"
        )

    return QueryResponse(
        patient_id=patient_id, case_data=patient_data
    )


@app.get(
    "/v1/medical-coder/patients", response_model=QueryAllResponse
)
def get_all_patients():
    """
    Retrieve all patient data.
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT patient_id, patient_data FROM patients")
    rows = cursor.fetchall()
    connection.close()

    patients = [
        QueryResponse(patient_id=row[0], case_data=row[1])
        for row in rows
    ]
    return QueryAllResponse(patients=patients)


@app.delete("/v1/medical-coder/patient/{patient_id}")
def delete_patient_data(patient_id: str):
    """
    Delete a patient's data by patient ID.
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM patients WHERE patient_id = ?", (patient_id,)
    )
    connection.commit()
    connection.close()

    return {
        "message": "Patient data deleted successfully",
        "patient_id": patient_id,
    }


@app.delete("/v1/medical-coder/patients")
def delete_all_patients():
    """
    Delete all patient data.
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM patients")
    connection.commit()
    connection.close()

    return {"message": "All patient data deleted successfully"}


if __name__ == "__main__":
    try:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"An error occurred: {e}")
