import json
from app import app

def test_create_user():
    client = app.test_client()

    response = client.post("/api/users",
        data=json.dumps({
            "name": "Ankush",
            "email": "ankush@test.com"
        }),
        content_type="application/json"
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"


def test_get_users():
    client = app.test_client()
    response = client.get("/api/users")

    assert response.status_code == 200
