from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_one.app import app


def test_read_root_retornar_ok_e_ola_mundo():
    Client = TestClient(app)  # Arrange (organização)

    response = Client.get('/')  # Act (ação)

    assert response.status_code == HTTPStatus.OK  # Assert (verificação)
    assert response.json() == {'OLAR': 'MUNDO'}
