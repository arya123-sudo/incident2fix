"""Flask app exposing checkout, discount, and reservation endpoints."""

from flask import Flask, jsonify, request

from app import discounts, inventory, orders


def create_app() -> Flask:
    app = Flask(__name__)

    @app.post("/checkout")
    def checkout():
        body: dict = request.get_json(force=True) or {}
        try:
            return jsonify(orders.checkout(body)), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.post("/discount")
    def discount():
        body: dict = request.get_json(force=True) or {}
        total: float = discounts.apply_discount(body["code"], float(body["subtotal"]))
        return jsonify({"discounted_total": total}), 200

    @app.post("/reserve")
    def reserve():
        body: dict = request.get_json(force=True) or {}
        remaining: int = inventory.reserve_stock(body["item"], int(body["qty"]))
        return jsonify({"remaining": remaining}), 200

    return app
