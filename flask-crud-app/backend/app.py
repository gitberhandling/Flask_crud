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
