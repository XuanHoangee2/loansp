import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock

# Add backend to Python path so we can import main
backend_path = str(Path(__file__).resolve().parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.environ.setdefault("GROQ_API", "dummy-groq-api-key-for-tests")

from fastapi.testclient import TestClient  # noqa: E402
import pytest  # noqa: E402

# Import main AFTER adding backend to path
from main import app  # noqa: E402


@pytest.fixture
def client():
    """Provide a TestClient with the LLM chain mocked."""
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = "This is a mocked loan advisor response."
    app.state.question_answer_chain = mock_chain

    with TestClient(app) as test_client:
        yield test_client
