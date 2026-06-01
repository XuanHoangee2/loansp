from http import HTTPStatus


def test_home_page(client):
    """
    Home page should return index.html if it exists,
    otherwise a 404 (FileResponse does not leak 500s).
    """
    response = client.get("/")
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.NOT_FOUND)
