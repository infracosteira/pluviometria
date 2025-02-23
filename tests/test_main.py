from http import HTTPStatus
from fastapi.testclient import TestClient
from src.main import app

def test_read_root():
    client = TestClient(app)                        # Arrange (organize the code)
    response = client.get("/")                      # Act (perform the request)
    assert response.status_code == HTTPStatus.OK    # Assert (check the response)
    assert response.json() == {"message": "Hello World!"}    # Assert (check the response)