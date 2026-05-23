# ShopSphere — Scalable Marketplace with Recommendation Engine

Multi-vendor e-commerce platform built with microservices, ElasticSearch,
RabbitMQ event-driven inventory, and Matrix Factorization recommendations.

## Architecture

| Service | Framework | Role |
|---|---|---|
| auth-service | Flask | JWT authentication, user registration |
| product-service | FastAPI | Product catalogue, ElasticSearch indexing, stock |
| order-service | **Django** | Order lifecycle, Stripe payment stub |
| cart-service | FastAPI | Redis-backed shopping cart |
| search-service | FastAPI | ElasticSearch fuzzy full-text search |
| recommendation-service | FastAPI | Matrix Factorization collaborative filtering |
| home-service | FastAPI | Homepage aggregator |
| analytics-service | FastAPI | Product view tracking, trending |
| notification-service | Python | Order notification consumer |
| notification-api | FastAPI | Notification read API |
| gateway | Nginx | API gateway, rate limiting, CORS |

**Infrastructure:** PostgreSQL · Redis · RabbitMQ · ElasticSearch

---

## Run locally (Docker Compose)

### Prerequisites
- Docker Desktop or Docker Engine + Compose plugin

### Steps

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd shopsphere

# 2. Set up environment
cp .env.example .env
# Edit .env — at minimum change JWT_SECRET

# 3. Build and start all services
docker compose up --build

# 4. Wait ~60 seconds for ElasticSearch to be ready
# Then open: http://localhost
```

### Useful local URLs

| URL | Service |
|---|---|
| http://localhost | Frontend (via Nginx gateway) |
| http://localhost/auth/hello | Auth health check |
| http://localhost/products/products | Product list |
| http://localhost/search/search?q=phone | Search |
| http://localhost:15672 | RabbitMQ management (guest/guest) |
| http://localhost:9200 | ElasticSearch |

### Stop everything
```bashd
docker compose down          # stop containers
docker compose down -v       # stop + delete volumes (fresh start)
```

---

## Deploy to Kubernetes

### Prerequisites
- `kubectl` configured against your cluster
- Nginx Ingress Controller installed:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/cloud/deploy.yaml
```

### Steps

```bash
# 1. Build and push images to your registry
# Replace 'shopsphere' with your Docker Hub username or registry URL
docker build -t shopsphere/auth-service:latest           ./auth-service
docker build -t shopsphere/product-service:latest        ./product-service
docker build -t shopsphere/order-service:latest          ./order-service
docker build -t shopsphere/cart-service:latest           ./cart-service
docker build -t shopsphere/search-service:latest         ./search-service
docker build -t shopsphere/recommendation-service:latest ./recommendation-service
docker build -t shopsphere/home-service:latest           ./home-service
docker build -t shopsphere/analytics-service:latest      ./analytics-service
docker build -t shopsphere/notification-service:latest   ./notification-service
docker build -t shopsphere/notification-api:latest       ./notification-api

docker push shopsphere/auth-service:latest
# ... push all others

# 2. Update secrets BEFORE applying
# Edit k8s/secret.yaml with real base64-encoded values:
#   echo -n "your-real-secret" | base64

# 3. Apply everything in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/infra/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress/

# 4. Wait for pods to be ready
kubectl get pods -n shopsphere -w

# 5. Add to /etc/hosts for local cluster (e.g. minikube)
echo "$(minikube ip) shopsphere.local" | sudo tee -a /etc/hosts
# Then open: http://shopsphere.local
```

### Check status
```bash
kubectl get pods        -n shopsphere
kubectl get services    -n shopsphere
kubectl get hpa         -n shopsphere
kubectl get ingress     -n shopsphere
```

### View logs
```bash
kubectl logs -n shopsphere deployment/product-service -f
kubectl logs -n shopsphere deployment/order-service   -f
```

### Scale manually
```bash
kubectl scale deployment product-service -n shopsphere --replicas=4
```

---

## Services that auto-scale (HPA)

| Service | Min | Max | Trigger |
|---|---|---|---|
| product-service | 2 | 6 | CPU > 70% or Memory > 80% |
| order-service | 2 | 6 | CPU > 70% or Memory > 80% |
| cart-service | 2 | 6 | CPU > 70% or Memory > 80% |
| search-service | 2 | 6 | CPU > 70% or Memory > 80% |
| home-service | 2 | 6 | CPU > 70% or Memory > 80% |
| notification-api | 2 | 6 | CPU > 70% or Memory > 80% |

---

## Week 4 Disaster Recovery Test

The requirement asks: manually kill the Order service to confirm the API
Gateway and other services fail gracefully.

```bash
# Docker Compose
docker compose stop order-service
# → Cart /checkout returns 502 "Order service unavailable"
# → All other pages still work
docker compose start order-service

# Kubernetes
kubectl delete pod -n shopsphere -l app=order-service
# → K8s immediately starts a replacement pod (self-healing)
# → HPA keeps minimum 2 replicas so one dying doesn't cause downtime
```
