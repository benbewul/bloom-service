from flask import Flask, jsonify, render_template, request
from datetime import datetime, timezone
import uuid

app = Flask(__name__)

FLOWERS = [
    {"id": 1, "name": "Beyaz Lilyum", "price": 899, "image": "/static/images/beyaz-lilyum.jpeg", "description": "Zarif beyaz lilyumlardan ferah ve şık bir buket."},
    {"id": 2, "name": "Pembe Lilyum & Gül", "price": 1099, "image": "/static/images/pembe-lilyum-gul.jpeg", "description": "Pembe lilyum ve güllerle romantik, yumuşak tonlarda bir aranjman."},
    {"id": 3, "name": "Papatya Buketi", "price": 449, "image": "/static/images/papatya-buketi.jpeg", "description": "Güneş gibi iç açan, sade ve neşeli papatyalar."},
    {"id": 4, "name": "Pembe Lale", "price": 549, "image": "/static/images/pembe-lale.jpeg", "description": "Mevsimin en tatlı pembe lalelerinden minimal bir buket."},
    {"id": 5, "name": "Kırmızı Gül Buketi", "price": 749, "image": "/static/images/kirmizi-gul-buketi.jpeg", "description": "Klasik kırmızı güllerle zamansız bir seçim."},
]

@app.get("/")
def home():
    return render_template("index.html", flowers=FLOWERS)

@app.get("/api/flowers")
def flowers():
    return jsonify(FLOWERS)

@app.post("/api/order")
def order():
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])
    if not items:
        return jsonify({"ok": False, "message": "Sepet boş."}), 400

    by_id = {f["id"]: f for f in FLOWERS}
    total = 0
    normalized = []
    for item in items:
        try:
            flower_id = int(item.get("id"))
            qty = max(1, int(item.get("qty", 1)))
        except (TypeError, ValueError):
            continue
        flower = by_id.get(flower_id)
        if flower:
            total += flower["price"] * qty
            normalized.append({"id": flower_id, "name": flower["name"], "qty": qty})

    if not normalized:
        return jsonify({"ok": False, "message": "Geçerli ürün bulunamadı."}), 400

    return jsonify({
        "ok": True,
        "orderId": f"BLM-{uuid.uuid4().hex[:6].upper()}",
        "total": total,
        "items": normalized,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "message": "Siparişiniz alındı 🌸"
    })

@app.get("/health")
def health():
    return jsonify({"status": "UP", "service": "bloom-flower-shop"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
