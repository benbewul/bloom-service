# Bloom Flower Shop 🌸

Mini flower shop built for an OpenShift Serverless / Knative demonstration.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080

## Endpoints
- `GET /` shop UI
- `GET /api/flowers` product list
- `POST /api/order` demo order creation
- `GET /health` health check

## OpenShift demo
- `openshift/bloom-knative.yaml`: Knative Service, can scale to zero.
- `openshift/evergreen-deployment.yaml`: standard Deployment with one replica, Service and Route.

Replace `BLOOM_IMAGE` with the pushed container image before applying manifests.
