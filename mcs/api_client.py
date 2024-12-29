from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


@dataclass
class PatientCase:
    """
    Represents a patient case to be processed by the Medical Coder Swarm.

    Attributes:
        patient_id (str): Unique identifier for the patient
        case_description (str): Detailed medical case description
    """

    patient_id: str
    case_description: str


@dataclass
class QueryResponse:
    """
    Response from the Medical Coder Swarm API for a single patient case.

    Attributes:
        patient_id (str): Patient identifier
        case_data (str): Processed case data
    """

    patient_id: str
    case_data: str


class MCSClientError(Exception):
    """Base exception for MCS client errors."""

    pass


class RateLimitError(MCSClientError):
    """Raised when API rate limit is exceeded."""

    pass


class AuthenticationError(MCSClientError):
    """Raised when API authentication fails."""

    pass


class ValidationError(MCSClientError):
    """Raised when request validation fails."""

    pass


class MCSClient:
    """
    Production-grade client for the Medical Coder Swarm API.

    Features:
    - Automatic retries with exponential backoff
    - Comprehensive logging
    - Type hints
    - Request validation
    - Rate limit handling

    Usage:
        >>> with MCSClient() as client:
        >>>     response = client.run_medical_coder("P123", "Patient presents with...")
    """

    def __init__(
        self,
        base_url: str = "https://mcs-285321057562.us-central1.run.app",
        timeout: int = 30,
        max_retries: int = 3,
        logger_name: str = "mcs_client",
    ):
        """
        Initialize the MCS client.

        Args:
            base_url (str): Base URL for the API
            timeout (int): Request timeout in seconds
            max_retries (int): Maximum number of retry attempts
            logger_name (str): Name for the logger instance
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Configure logger
        logger.add(
            f"{logger_name}_{datetime.now().strftime('%Y%m%d')}.log",
            rotation="500 MB",
            retention="10 days",
            level="INFO",
        )

        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {"Content-Type": "application/json"}
        )

    def _handle_response(
        self, response: requests.Response
    ) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response (requests.Response): Response from the API

        Returns:
            Dict[str, Any]: Parsed response data

        Raises:
            RateLimitError: When rate limit is exceeded
            AuthenticationError: When authentication fails
            ValidationError: When request validation fails
            MCSClientError: For other API errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {str(e)}"
            if response.status_code == 429:
                raise RateLimitError(error_msg)
            elif response.status_code == 401:
                raise AuthenticationError(error_msg)
            elif response.status_code == 422:
                raise ValidationError(error_msg)
            else:
                raise MCSClientError(error_msg)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                RateLimitError,
            )
        ),
    )
    def run_medical_coder(
        self, patient_id: str, case_description: str
    ) -> QueryResponse:
        """
        Process a single patient case through the Medical Coder Swarm.

        Args:
            patient_id (str): Unique identifier for the patient
            case_description (str): Medical case details to be processed

        Returns:
            QueryResponse: Processed case data

        Raises:
            MCSClientError: If the API request fails
        """
        logger.info(f"Processing case for patient: {patient_id}")

        payload = PatientCase(
            patient_id=patient_id, case_description=case_description
        ).__dict__

        try:
            response = self.session.post(
                f"{self.base_url}/v1/medical-coder/run",
                json=payload,
                timeout=self.timeout,
            )
            data = self._handle_response(response)
            return QueryResponse(**data)
        except Exception as e:
            logger.error(
                f"Error processing case for patient {patient_id}: {str(e)}"
            )
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def run_batch(
        self, cases: List[PatientCase]
    ) -> List[QueryResponse]:
        """
        Process multiple patient cases in batch.

        Args:
            cases (List[PatientCase]): List of patient cases to process

        Returns:
            List[QueryResponse]: List of processed case data
        """
        logger.info(f"Processing batch of {len(cases)} cases")

        payload = {"cases": [case.__dict__ for case in cases]}

        try:
            response = self.session.post(
                f"{self.base_url}/v1/medical-coder/run-batch",
                json=payload,
                timeout=self.timeout,
            )
            data = self._handle_response(response)
            return [QueryResponse(**item) for item in data]
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            raise

    def get_patient_data(self, patient_id: str) -> QueryResponse:
        """
        Retrieve data for a specific patient.

        Args:
            patient_id (str): Patient identifier

        Returns:
            QueryResponse: Patient data
        """
        logger.info(f"Retrieving data for patient: {patient_id}")

        try:
            response = self.session.get(
                f"{self.base_url}/v1/medical-coder/patient/{patient_id}",
                timeout=self.timeout,
            )
            data = self._handle_response(response)
            return QueryResponse(**data)
        except Exception as e:
            logger.error(f"Error retrieving patient data: {str(e)}")
            raise

    def get_all_patients(self) -> List[QueryResponse]:
        """
        Retrieve data for all patients.

        Returns:
            List[QueryResponse]: List of all patient data
        """
        logger.info("Retrieving all patient data")

        try:
            response = self.session.get(
                f"{self.base_url}/v1/medical-coder/patients",
                timeout=self.timeout,
            )
            data = self._handle_response(response)
            return [
                QueryResponse(**patient)
                for patient in data.get("patients", [])
            ]
        except Exception as e:
            logger.error(
                f"Error retrieving all patient data: {str(e)}"
            )
            raise

    def get_rate_limits(self) -> Dict[str, Any]:
        """
        Get current rate limit status.

        Returns:
            Dict[str, Any]: Rate limit information
        """
        logger.info("Checking rate limits")

        try:
            response = self.session.get(
                f"{self.base_url}/rate-limits", timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Error checking rate limits: {str(e)}")
            raise

    def health_check(self) -> bool:
        """
        Check if the API is operational.

        Returns:
            bool: True if API is healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health", timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# # Example usage
# if __name__ == "__main__":
#     # Using context manager
#     with MCSClient() as client:
#         # Single case processing
#         try:
#             response = client.run_medical_coder(
#                 "P123",
#                 "Patient presents with acute respiratory symptoms...",
#             )
#             print(f"Processed case: {response}")

#             # Batch processing
#             cases = [
#                 PatientCase("P124", "Case 1 description..."),
#                 PatientCase("P125", "Case 2 description..."),
#             ]
#             batch_response = client.run_batch(cases)
#             print(f"Processed batch: {batch_response}")

#             # Health check
#             is_healthy = client.health_check()
#             print(f"API health status: {is_healthy}")

#         except MCSClientError as e:
#             print(f"An error occurred: {str(e)}")
