import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add backend to Python path so we can import main
backend_path = str(Path(__file__).resolve().parent.parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.environ.setdefault("GROQ_API", "dummy-groq-api-key-for-tests")

from fastapi.testclient import TestClient  # noqa: E402
import pytest  # noqa: E402

# Import main AFTER adding backend to path
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    """Provide a TestClient with the LangGraph workflow mocked."""
    mock_msg = MagicMock()
    mock_msg.content = "This is a mocked loan advisor response."

    mock_graph = AsyncMock()
    mock_graph.ainvoke.return_value = {"messages": [mock_msg]}

    with TestClient(app) as test_client:
        app.state.graph = mock_graph
        yield test_client
