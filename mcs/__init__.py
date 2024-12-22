from dotenv import load_dotenv

load_dotenv()

from mcs.main import MedicalCoderSwarm  # noqa: E402

__all__ = ["MedicalCoderSwarm"]
