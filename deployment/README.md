# RTI-Agent Phase C Deployment

## Kubernetes

Apply secrets separately, then deploy:

```bash
kubectl create secret generic rti-agent-secrets \
  --from-literal=GROQ_API_KEY=... \
  --from-literal=GEMINI_API_KEY=... \
  --from-literal=MONGO_URI=... \
  --from-literal=REDIS_URL=...

kubectl apply -f deployment/kubernetes/observability.yaml
kubectl apply -f deployment/kubernetes/rti-agent-api.yaml
```

The API exposes `/health`, `/metrics`, `/api/v1/governance/*`, and existing Phase A/B endpoints.

