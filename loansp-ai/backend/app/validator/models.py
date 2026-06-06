from enum import Enum
from typing import List

from pydantic import BaseModel


class ValidationStatus(str, Enum):
    VALID = "valid"
    MISSING_DATA = "missing_data"


class ValidationResult(BaseModel):
    status: ValidationStatus

    task: str

    missing_fields: List[str] = []

    available_fields: List[str] = []
