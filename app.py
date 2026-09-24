from flask import Flask, jsonify, render_template, request
from datetime import datetime, timezone
import os
import uuid

app = Flask(__name__)

FLOWERS = [
    {"id": 1, "name": "Beyaz Lilyum", "price": 899, "image": "/static/images/beyaz-lilyum.jpeg", "description": "Zarif beyaz lilyumlardan ferah ve şık bir buket."},
    {"id": 2, "name": "Pembe Lilyum & Gül", "price": 1099, "image": "/static/images/pembe-lilyum-gul.jpeg", "description": "Pembe lilyum ve güllerle romantik, yumuşak tonlarda bir aranjman."},
    {"id": 3, "name": "Papatya Buketi", "price": 449, "image": "/static/images/papatya-buketi.jpeg", "description": "Güneş gibi iç açan, sade ve neşeli papatyalar."},
    {"id": 4, "name": "Pembe Lale", "price": 549, "image": "/static/images/pembe-lale.jpeg", "description": "Mevsimin en tatlı pembe lalelerinden minimal bir buket."},
    {"id": 5, "name": "Kırmızı Gül Buketi", "price": 749, "image": "/static/images/kirmizi-gul-buketi.jpeg", "description": "Klasik kırmızı güllerle zamansız bir seçim."},
]


def runtime_name():
    return "BLOOM" if os.getenv("K_SERVICE") else "EVERGREEN"


def app_log(message):
    print(f"[{runtime_name()}] {message}", flush=True)


@app.before_request
def log_request():
    # Health/readiness kontrollerini gürültü yaratmaması için loglamıyoruz.
    if request.path != "/health":
        app_log(f"Request received | {request.method} {request.path}")


@app.get("/")
def home():
    return render_template("index.html", flowers=FLOWERS)


@app.get("/api/flowers")
def flowers():
    app_log(f"Product list loaded | {len(FLOWERS)} products")
    return jsonify(FLOWERS)


@app.post("/api/order")
def order():
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])
    if not items:
        app_log("Order rejected | Cart is empty")
        return jsonify({"ok": False, "message": "Sepet boş."}), 400

    by_id = {f["id"]: f for f in FLOWERS}
    total = 0
    total_items = 0
    normalized = []

    for item in items:
        try:
            flower_id = int(item.get("id"))
            qty = max(1, int(item.get("qty", 1)))
        except (TypeError, ValueError):
            continue

        flower = by_id.get(flower_id)
        if flower:
            subtotal = flower["price"] * qty
            total += subtotal
            total_items += qty
            normalized.append({
                "id": flower_id,
                "name": flower["name"],
                "qty": qty,
                "price": flower["price"],
                "subtotal": subtotal,
            })

    if not normalized:
        app_log("Order rejected | No valid products")
        return jsonify({"ok": False, "message": "Geçerli ürün bulunamadı."}), 400

    order_id = f"BLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    revision = os.getenv("K_REVISION", "standard-deployment")

    app_log("=" * 58)
    app_log("NEW ORDER RECEIVED")
    app_log(f"Order ID: {order_id}")
    app_log(f"Revision: {revision}")
    app_log("Purchased bouquets:")
    for item in normalized:
        app_log(
            f"- {item['name']} | Quantity: {item['qty']} | "
            f"Unit Price: {item['price']} TL | Subtotal: {item['subtotal']} TL"
        )
    app_log(f"Total items: {total_items}")
    app_log(f"Order total: {total} TL")
    app_log("Order status: CONFIRMED")
    app_log("=" * 58)

    return jsonify({
        "ok": True,
        "orderId": order_id,
        "total": total,
        "items": normalized,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "message": "Siparişiniz alındı"
    }), 201


@app.get("/health")
def health():
    return jsonify({"status": "UP", "service": "bloom-flower-shop"})


# Gunicorn import sırasında da görünür; Knative ve normal Deployment farkını logdan anlayabiliriz.
app_log("Application process initialized")
if os.getenv("K_SERVICE"):
    app_log(f"Knative Service: {os.getenv('K_SERVICE')}")
    app_log(f"Knative Revision: {os.getenv('K_REVISION', 'unknown')}")
    app_log("Instance is serving on demand and can scale to zero")
else:
    app_log("Running as standard OpenShift Deployment")
    app_log("Instance remains available while replicas are configured")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
