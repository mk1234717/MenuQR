import uuid
from flask import Flask, request, jsonify
from menu_item import MenuItem, SeasonalDiscount

app = Flask(__name__)
items_db = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/menu', methods=['POST'])
def create_item():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    try:
        item = MenuItem(
            name=data.get('name'),
            price=data.get('price'),
            image_url=data.get('image_url'),
            is_available=data.get('is_available', True),
            special_discount_percent=data.get('special_discount_percent')
        )
        items_db[str(item.id)] = item
        return jsonify({"id": str(item.id), "name": item.name, "price": float(item.price)}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/menu/<item_id>/final_price', methods=['POST'])
def final_price(item_id):
    item = items_db.get(item_id)
    if not item:
        return jsonify({"error": "Страву не знайдено"}), 404
    data = request.get_json() or {}
    discounts = [SeasonalDiscount(d['name'], d['percent'], lambda m: True) for d in data.get('seasonal_discounts', [])]
    try:
        final = item.calculate_final_price(discounts)
        return jsonify({"item_id": item_id, "final_price": final})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)