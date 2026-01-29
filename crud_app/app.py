from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
import os

db = SQLAlchemy()


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


def create_app(test_config=None):
    app = Flask(__name__, static_folder="frontend", static_url_path="")

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@host.docker.internal:5432/crud_ui"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Override config during tests
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    # ---------------- ERROR HANDLER ----------------
    @app.errorhandler(Exception)
    def handle_exception(e):
        print("ERROR URL:", request.method, request.path)
        code = 500
        message = str(e)
        if isinstance(e, HTTPException):
            code = e.code
            message = e.description
        return jsonify({'status': 'error', 'message': message, 'data': None}), code

    # ---------------- ROUTES ----------------
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    # CREATE
    @app.route('/item', methods=['POST'])
    def create_item():
        data = request.json
        if not data or 'name' not in data:
            return jsonify({'status': 'error', 'message': 'Name is required', 'data': None}), 400

        item = Item(
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(item)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Item created',
            'data': item.to_dict()
        }), 201

    # READ (pagination + filter + sort)
    @app.route('/item', methods=['GET'])
    def get_items():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        sort_by = request.args.get('sort_by', 'id')
        order = request.args.get('order', 'asc')
        filter_name = request.args.get('name')

        query = Item.query

        if filter_name:
            query = query.filter(Item.name.ilike(f'%{filter_name}%'))

        column = getattr(Item, sort_by, Item.id)
        if order == 'desc':
            query = query.order_by(db.desc(column))
        else:
            query = query.order_by(column)

        items_paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'status': 'success',
            'message': 'Items fetched',
            'data': [item.to_dict() for item in items_paginated.items],
            'page': page,
            'total_pages': items_paginated.pages,
            'total_items': items_paginated.total
        })

    # UPDATE
    @app.route('/item/<int:item_id>', methods=['PUT'])
    def update_item(item_id):
        data = request.json
        item = Item.query.get(item_id)

        if not item:
            return jsonify({'status': 'error', 'message': 'Item not found', 'data': None}), 404

        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Item updated',
            'data': item.to_dict()
        })

    # DELETE
    @app.route('/item/<int:item_id>', methods=['DELETE'])
    def delete_item(item_id):
        item = Item.query.get(item_id)

        if not item:
            return jsonify({'status': 'error', 'message': 'Item not found', 'data': None}), 404

        db.session.delete(item)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Item deleted',
            'data': None
        })

    return app


# ---------------- RUN SERVER ----------------
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
