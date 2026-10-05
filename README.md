# Library Management Application - DevOps

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open: http://localhost:5000

## Test

```bash
pytest -v
```

## Docker

```bash
docker build -t library-app:1.0 .
docker run -d -p 5000:5000 library-app:1.0
docker ps
docker logs CONTAINER_ID
```

## Docker Hub

Replace YOUR_DOCKERHUB_USERNAME with your Docker Hub username.

```bash
docker login
docker tag library-app:1.0 YOUR_DOCKERHUB_USERNAME/library-app:1.0
docker push YOUR_DOCKERHUB_USERNAME/library-app:1.0
```

## Kubernetes / Minikube

Start Minikube:

```bash
minikube start --driver=docker
minikube status
kubectl get nodes
```

Update the image name in `k8s/deployment.yaml`, then:

```bash
minikube image load library-app:1.0
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods
kubectl get deployments
kubectl get services
minikube service library-service
```

## Scale 2 to 3

```bash
kubectl scale deployment library-app --replicas=3
kubectl get pods
```

## Rolling update

Build version 2:

```bash
docker build -t library-app:2.0 .
minikube image load library-app:2.0
kubectl set image deployment/library-app library-container=library-app:2.0
kubectl rollout status deployment/library-app
```

## Troubleshooting

```bash
kubectl describe pod POD-NAME
kubectl logs POD-NAME
kubectl get events
```
