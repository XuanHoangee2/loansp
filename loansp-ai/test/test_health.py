from http import HTTPStatus


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "loansp-chatbot"
    assert data["version"] == "1.0.0"
