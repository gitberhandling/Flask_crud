# Flask_crud
```python
app.py

from flask import Flask, request, jsonify, send_from_directory
from db import db
from models import User
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# ------------------------
# Serve Frontend
# ------------------------
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


# ------------------------
# CREATE USER
# ------------------------
@app.route("/api/users", methods=["POST"])
def create_user():
    try:
        data = request.json

        # Validation
        if not data.get("name") or not data.get("email"):
            return jsonify({
                "status": "error",
                "message": "Name and Email are required"
            }), 400

        user = User(name=data["name"], email=data["email"])
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "status": "success",
            "data": user.to_dict()
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ------------------------
# READ USERS
# ------------------------
@app.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify({
        "status": "success",
        "data": [u.to_dict() for u in users]
    }), 200


# ------------------------
# UPDATE USER
# ------------------------
@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404

        data = request.json

        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)

        db.session.commit()

        return jsonify({
            "status": "success",
            "data": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------
# DELETE USER
# ------------------------
@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
```
#db.py
```
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```
#models.py
```
from db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }
```
#requirements.txt
```
flask
flask_sqlalchemy
psycopg2-binary
python-dotenv
pytest
```
#pytest :
```
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
```
#html: 
```
<!DOCTYPE html>
<html>
<head>
    <title>Flask CRUD App</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }

        input {
            padding: 6px;
            margin: 5px;
        }

        button {
            padding: 6px 12px;
            cursor: pointer;
        }

        table {
            margin-top: 20px;
            border-collapse: collapse;
            width: 70%;
        }

        th, td {
            border: 1px solid #ccc;
            padding: 8px;
        }

        .error {
            color: red;
        }

        .success {
            color: green;
        }
    </style>
</head>

<body>

<h2>🚀 Flask CRUD Application</h2>

<div>
    <input id="name" placeholder="Name">
    <input id="email" placeholder="Email">
    <button onclick="createUser()">Add User</button>
</div>

<p id="message"></p>

<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Actions</th>
        </tr>
    </thead>

    <tbody id="users"></tbody>
</table>

<script>
const API = "/api/users";
let editId = null;

// -----------------
// CREATE / UPDATE
// -----------------
function createUser() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();

    if (!name || !email) {
        showMessage("Name and Email are required ❌", "error");
        return;
    }

    const payload = { name, email };

    const method = editId ? "PUT" : "POST";
    const url = editId ? `${API}/${editId}` : API;

    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error("Request failed");
        return res.json();
    })
    .then(() => {
        showMessage(editId ? "User updated ✅" : "User created ✅", "success");
        resetForm();
        loadUsers();
    })
    .catch(() => showMessage("Operation failed ❌", "error"));
}

// -----------------
// READ
// -----------------
function loadUsers() {
    fetch(API)
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("users");
            table.innerHTML = "";

            data.data.forEach(user => {
                table.innerHTML += `
                    <tr>
                        <td>${user.id}</td>
                        <td>${user.name}</td>
                        <td>${user.email}</td>
                        <td>
                            <button onclick="editUser(${user.id}, '${user.name}', '${user.email}')">✏ Edit</button>
                            <button onclick="deleteUser(${user.id})">🗑 Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}

// -----------------
// EDIT
// -----------------
function editUser(id, name, email) {
    editId = id;
    document.getElementById("name").value = name;
    document.getElementById("email").value = email;
    showMessage("Editing mode enabled ✏", "success");
}

// -----------------
// DELETE
// -----------------
function deleteUser(id) {
    if (!confirm("Are you sure you want to delete this user?")) return;

    fetch(`${API}/${id}`, { method: "DELETE" })
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(() => {
            showMessage("User deleted 🗑", "success");
            loadUsers();
        })
        .catch(() => showMessage("Delete failed ❌", "error"));
}

// -----------------
// UTILITIES
// -----------------
function resetForm() {
    editId = null;
    document.getElementById("name").value = "";
    document.getElementById("email").value = "";
}

function showMessage(msg, type) {
    const el = document.getElementById("message");
    el.className = type;
    el.innerText = msg;

    setTimeout(() => el.innerText = "", 3000);
}

loadUsers();
</script>

</body>
</html>
```

