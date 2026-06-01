from http import HTTPStatus

from main import app


def test_chat_success(client):
    payload = {
        "message": "What is the interest rate for a home loan?",
        "thread_id": "test-thread-123"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["response"] == "This is a mocked loan advisor response."
    assert data["thread_id"] == "test-thread-123"
    assert "processing_time" in data
    assert isinstance(data["processing_time"], float)


def test_chat_dict_response(client):
    """Test that the endpoint handles dict-shaped LLM output."""
    app.state.question_answer_chain.ainvoke.return_value = {"answer": "Dict answer"}
    payload = {
        "message": "Explain debt ratio",
        "thread_id": "test-thread-456"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["response"] == "Dict answer"
    assert data["thread_id"] == "test-thread-456"


def test_chat_error(client):
    """Test that LLM errors are surfaced as HTTP 500."""
    app.state.question_answer_chain.ainvoke.side_effect = Exception("LLM service failed")
    payload = {
        "message": "Hi",
        "thread_id": "test-thread-789"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "LLM service failed" in response.json()["detail"]


def test_chat_missing_message(client):
    """Missing required field should trigger Pydantic validation error."""
    payload = {"thread_id": "test-thread-123"}
    response = client.post("/chat", json=payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_chat_invalid_payload(client):
    """Payload with no recognised fields should trigger validation error."""
    response = client.post("/chat", json={"invalid_field": "value"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
