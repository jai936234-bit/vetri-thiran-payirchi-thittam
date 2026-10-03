from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "LegalEase"


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


def test_validation():

    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "",
            "terms": "",
            "effective_date": ""
        }
    )

    assert response.status_code == 422


def test_txt_export():

    response = client.post(
        "/export/txt",
        json={
            "document_type": "NDA",
            "content": "NON-DISCLOSURE AGREEMENT"
        }
    )

    assert response.status_code == 200

    assert (
        b"NON-DISCLOSURE AGREEMENT"
        in response.content
    )