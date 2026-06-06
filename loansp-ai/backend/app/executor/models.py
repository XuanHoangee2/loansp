from pydantic import BaseModel


class ExecutionResult(BaseModel):
    task: str

    success: bool

    data: dict | None = None

    error: str | None = None
