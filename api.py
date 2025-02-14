import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

from mcs.main import (
    MedicalCoderSwarm,
    MCSOutput,
)  # Assuming MCSOutput is the output schema of the swarm


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="MedicalCoderSwarm API",
    version="1.0.0",
    debug=True,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
db_path = "medical_coder.db"

logger.add("api.log", rotation="10 MB")

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Create tables
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        patient_data TEXT
    )
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS rate_limits (
        ip_address TEXT PRIMARY KEY,
        last_daily_reset TEXT,
        last_hourly_reset TEXT,
        daily_requests_remaining INTEGER DEFAULT 1000,
        hourly_requests_remaining INTEGER DEFAULT 100
    )
"""
)
connection.commit()
connection.close()


# Pydantic models
class PatientCase(BaseModel):
    patient_id: str = Field(
        ..., description="Unique identifier for the patient"
    )
    patient_docs: Optional[str] = Field(
        None, description="Patient documentation"
    )
    case_description: str = Field(
        ..., description="Description of the case"
    )
    summarization: bool = Field(
        False, description="Enable summarization"
    )
    rag_url: Optional[str] = Field(
        None,
        description="URL for retrieval-augmented generation (RAG)",
    )
    rag_api_key: Optional[str] = Field(
        None, description="API key for RAG"
    )


class QueryResponse(BaseModel):
    patient_id: str = Field(
        ..., description="Unique identifier for the patient"
    )
    case_data: dict = Field(
        ..., description="Case data returned by the swarm"
    )


class QueryAllResponse(BaseModel):
    patients: List[QueryResponse] = Field(
        ..., description="List of all patients"
    )


class BatchPatientCase(BaseModel):
    cases: List[PatientCase] = Field(
        ..., description="List of patient cases for batch processing"
    )


# Utility functions for database operations
def fetch_patient_data(patient_id: str) -> Optional[dict]:
    """
    Fetch patient data from the database.

    Args:
        patient_id (str): Unique identifier for the patient.

    Returns:
        Optional[dict]: Patient data dictionary or None if not found.
    """
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT patient_data FROM patients WHERE patient_id = ?",
            (patient_id,),
        )
        row = cursor.fetchone()
        if row:
            # Convert JSON string back to dictionary
            return json.loads(row[0])
        return None
    except sqlite3.Error as e:
        logger.error(f"Error fetching patient data: {e}")
        return None
    finally:
        if connection:
            connection.close()


def save_patient_data(patient_id: str, patient_data: dict):
    """
    Save patient data to the database.

    Args:
        patient_id (str): Unique identifier for the patient.
        patient_data (dict): Patient data dictionary to be saved.
    """
    try:
        # Convert dictionary to JSON string
        patient_data_json = json.dumps(patient_data)
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO patients (patient_id, patient_data) VALUES (?, ?)",
            (patient_id, patient_data_json),
        )
        connection.commit()
    except sqlite3.Error as e:
        logger.error(f"Error saving patient data: {e}")
    finally:
        if connection:
            connection.close()


# Middleware for rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path != "/health":
        await check_rate_limit(request)
    return await call_next(request)


async def check_rate_limit(request: Request):
    client_ip = request.client.host
    now = datetime.utcnow()

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Insert default rate limit record if not exists
        cursor.execute(
            """
            INSERT OR IGNORE INTO rate_limits 
            (ip_address, last_daily_reset, last_hourly_reset, daily_requests_remaining, hourly_requests_remaining)
            VALUES (?, ?, ?, ?, ?)""",
            (client_ip, now.isoformat(), now.isoformat(), 1000, 100),
        )

        # Fetch current limits
        cursor.execute(
            """
            SELECT daily_requests_remaining, hourly_requests_remaining, last_daily_reset, last_hourly_reset 
            FROM rate_limits WHERE ip_address = ?""",
            (client_ip,),
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=500, detail="Rate limit record missing."
            )

        (
            daily_remaining,
            hourly_remaining,
            last_daily_reset,
            last_hourly_reset,
        ) = row

        # Reset limits if needed
        last_daily_reset_time = datetime.fromisoformat(
            last_daily_reset
        )
        if now.date() > last_daily_reset_time.date():
            daily_remaining = 1000
            last_daily_reset = now.isoformat()

        last_hourly_reset_time = datetime.fromisoformat(
            last_hourly_reset
        )
        if (now - last_hourly_reset_time).total_seconds() >= 3600:
            hourly_remaining = 100
            last_hourly_reset = now.isoformat()

        # Check limits
        if daily_remaining <= 0:
            raise HTTPException(
                status_code=429, detail="Daily rate limit exceeded."
            )
        if hourly_remaining <= 0:
            raise HTTPException(
                status_code=429, detail="Hourly rate limit exceeded."
            )

        # Update limits
        cursor.execute(
            """
            UPDATE rate_limits 
            SET daily_requests_remaining = daily_requests_remaining - 1,
                hourly_requests_remaining = hourly_requests_remaining - 1,
                last_daily_reset = ?,
                last_hourly_reset = ?
            WHERE ip_address = ?""",
            (last_daily_reset, last_hourly_reset, client_ip),
        )
        connection.commit()
    except sqlite3.Error as e:
        logger.error(f"Rate limit error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error"
        )
    finally:
        if connection:
            connection.close()


# Endpoints
@app.post("/v1/medical-coder/run", response_model=MCSOutput)
def run_medical_coder(patient_case: PatientCase):
    try:
        logger.info(
            f"Running MedicalCoderSwarm for patient: {patient_case.patient_id}"
        )

        swarm = MedicalCoderSwarm(
            patient_id=patient_case.patient_id,
            max_loops=1,
            patient_documentation=patient_case.patient_docs,
            summarization=patient_case.summarization,
            rag_on=bool(patient_case.rag_api_key),
            rag_url=patient_case.rag_url,
            rag_api_key=patient_case.rag_api_key,
        )
        output = swarm.run(task=patient_case.case_description)
        save_patient_data(
            patient_case.patient_id, output.model_dump()
        )
        return output
    except Exception as error:
        logger.error(f"Error: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@app.post(
    "/v1/medical-coder/run-batch", response_model=List[MCSOutput]
)
def run_medical_coder_batch(batch: BatchPatientCase):
    try:
        logger.info(
            f"Running batched MedicalCoderSwarm for {len(batch.cases)} patients"
        )

        responses = []
        for case in batch.cases:
            swarm = MedicalCoderSwarm(
                patient_id=case.patient_id,
                max_loops=1,
                patient_documentation=case.patient_docs,
                summarization=case.summarization,
                rag_on=bool(case.rag_api_key),
                rag_url=case.rag_url,
                rag_api_key=case.rag_api_key,
            )
            output = swarm.run(task=case.case_description)
            save_patient_data(case.patient_id, output.model_dump())
            responses.append(output)

        return responses
    except Exception as error:
        logger.error(f"Batch processing error: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@app.get(
    "/v1/medical-coder/patient/{patient_id}",
    response_model=QueryResponse,
)
def get_patient_data(patient_id: str):
    try:
        patient_data = fetch_patient_data(patient_id)
        if not patient_data:
            raise HTTPException(
                status_code=404, detail="Patient not found"
            )
        return QueryResponse(
            patient_id=patient_id, case_data=patient_data
        )
    except Exception as error:
        logger.error(f"Error fetching patient data: {error}")
        raise HTTPException(status_code=500, detail=str(error))


@app.get(
    "/v1/medical-coder/patients", response_model=QueryAllResponse
)
def get_all_patients():
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT patient_id, patient_data FROM patients"
        )
        rows = cursor.fetchall()
        patients = [
            QueryResponse(
                patient_id=row[0], case_data=json.loads(row[1])
            )
            for row in rows
        ]
        return QueryAllResponse(patients=patients)
    except Exception as error:
        logger.error(f"Error fetching all patients: {error}")
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if connection:
            connection.close()


@app.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=True,
    )
