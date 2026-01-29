import pytest
import tempfile
import os
from flask.testing import FlaskClient

from app import create_app, db


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}"
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

    os.close(db_fd)
    os.remove(db_path)


# ---------------- CREATE ----------------
def test_create_item(client: FlaskClient):
    res = client.post('/item', json={'name': 'Test Item'})
    data = res.get_json()

    assert res.status_code == 201
    assert data['status'] == 'success'
    assert data['data']['name'] == 'Test Item'


def test_create_item_no_name(client: FlaskClient):
    res = client.post('/item', json={})
    data = res.get_json()

    assert res.status_code == 400
    assert data['status'] == 'error'


# ---------------- READ ----------------
def test_get_items(client: FlaskClient):
    client.post('/item', json={'name': 'Item1'})
    client.post('/item', json={'name': 'Item2'})

    res = client.get('/item')
    data = res.get_json()

    assert res.status_code == 200
    assert len(data['data']) == 2


def test_get_items_with_filter(client: FlaskClient):
    client.post('/item', json={'name': 'Apple'})
    client.post('/item', json={'name': 'Banana'})

    res = client.get('/item?name=Apple')
    data = res.get_json()

    assert len(data['data']) == 1
    assert data['data'][0]['name'] == 'Apple'


# ---------------- UPDATE ----------------
def test_update_item(client: FlaskClient):
    client.post('/item', json={'name': 'Old Name'})
    res = client.put('/item/1', json={'name': 'New Name'})
    data = res.get_json()

    assert data['status'] == 'success'
    assert data['data']['name'] == 'New Name'


def test_update_nonexistent_item(client: FlaskClient):
    res = client.put('/item/999', json={'name': 'Nope'})
    data = res.get_json()

    assert res.status_code == 404
    assert data['status'] == 'error'


# ---------------- DELETE ----------------
def test_delete_item(client: FlaskClient):
    client.post('/item', json={'name': 'Delete Me'})
    res = client.delete('/item/1')
    data = res.get_json()

    assert res.status_code == 200
    assert data['status'] == 'success'


def test_delete_nonexistent_item(client: FlaskClient):
    res = client.delete('/item/999')
    data = res.get_json()

    assert res.status_code == 404
    assert data['status'] == 'error'
