# Creative Assignment 2 - CDPS  
**Group 3:** Aitana Cuadra Cano and Diego Galán Baquero

## Overview
This project presents a complete deployment scenario for an application that integrates the main topics covered in the course, especially those related to application deployment using **Docker** and **Kubernetes**.

The assignment is divided into four main stages:

1. Deployment of a monolithic application on a heavy virtual machine
2. Deployment of a monolithic application using Docker
3. Splitting the monolithic application into microservices with Docker Compose
4. Deployment of the microservices-based application using Kubernetes

The goal is to reinforce practical knowledge on virtualization, containers, microservices, orchestration, scalability, and reliability.

---

## 1. Deployment on a Heavy Virtual Machine

In the first stage, the application is deployed on a virtual machine running on **Google Cloud Platform**.  
To simplify the process, an automation script is used to install and start the application.

### Steps
1. Create a VM instance in Google Cloud Platform
2. Configure the firewall to allow TCP traffic
3. Connect to the VM via SSH
4. Upload the project files
5. Run the deployment script:

```bash
python3 punto1.py iniciar
```

### Verification
Once deployed, the application can be accessed from the browser at:

```text
http://<public-ip>:9095
http://<public-ip>:9095/productpage
```

### Removal
To stop and remove the deployment:

```bash
python3 punto1.py borrar
```

---

## 2. Deployment of the Monolithic Application Using Docker

In this stage, the application is packaged into a single lightweight Docker image.  
A script automates both the image creation and the container startup.

### Working Directory
```bash
cd Desktop/CreativaBuena/2Despliegue-docker/
```

### Commands

#### Create the image
```bash
python3 punto2.py crear
```

#### Start the container
```bash
python3 punto2.py iniciar
```

The container exposes port **9095**.  
The web page title displays `TEAM_ID` and `APP_OWNER`, which are injected as environment variables at startup.

#### Remove the container
```bash
python3 punto2.py borrar
```

### Verification
To access the application:

```text
http://<IP>:9095/productpage
```

Where `IP` is the address assigned to `eth0`, which can be checked with:

```bash
ifconfig
```

---

## 3. Splitting the Monolithic Application into Microservices with Docker Compose

In this stage, the monolithic application is split into four independent microservices:

- **ProductPage**
- **Details**
- **Reviews**
- **Ratings**

These services are orchestrated using **Docker Compose**.  
A script automates startup, configuration, and version switching.

### Working Directory
```bash
cd Desktop/CreativaBuena/3Despliegue-Docker-compose/
```

### Start the Application
```bash
python3 punto3.py iniciar v1   # No stars
python3 punto3.py iniciar v2   # Black stars
python3 punto3.py iniciar v3   # Red stars
```

### Remove the Environment
```bash
python3 punto3.py borrar
```

This command stops the containers and removes the network.

### Verification
Access the application from the browser at:

```text
http://localhost:9080/productpage
```

### Implementation Details
The required base image versions have been respected:

- **ProductPage:** `python:3.9-slim`
- **Details:** `ruby:2.7.1-slim` — exposed port `7070`
- **Reviews:** built with **Gradle 4.8.1** — internal port `9080`
- **Ratings:** `node:24-slim` — exposed port `9080`

### Main Differences: Single Container vs Multi-Container

#### Architecture
The single-container version runs the entire application as one block, while the multi-container version splits it into independent services with separate responsibilities.

#### Scalability
In the monolithic version, the whole application must be replicated to increase capacity.  
In the multi-container version, only the required services can be scaled.

#### Development
With Docker Compose and volumes, code changes are immediately reflected without rebuilding images.  
This is not possible in the single-container approach.

#### Resilience
In the multi-container version, the failure of a non-critical service does not necessarily stop the whole application.  
In the monolithic approach, a single error may bring the entire system down.

---

## 4. Deployment of the Microservices-Based Application Using Kubernetes

In the final stage, the application is deployed using **Kubernetes** with **Minikube**.  
This allows services to be managed in a more robust, scalable, and organized way.

A script automates deployment and switching between versions of the `reviews` service.

### Working Directory
```bash
cd Desktop/CreativaBuena/4Despliegue-kubernetes/
```

### Build Images Inside Minikube
To simplify deployment, images are built directly in Minikube’s internal Docker environment:

```bash
python3 punto4.py construir
```

### Deploy and Switch Versions
```bash
python3 punto4.py iniciar v1   # Deploy Reviews v1 (No stars)
python3 punto4.py iniciar v2   # Update to Reviews v2 (Black stars)
python3 punto4.py iniciar v3   # Update to Reviews v3 (Red stars)
```

### Verify the Scenario
To check that the pods, deployments, and services have been created correctly:

```bash
kubectl get pods -n cdps-3
kubectl get deployments -n cdps-3
kubectl get services -n cdps-3
kubectl get all -n cdps-3
```

The expected replication factors are:
- **details:** 4 replicas
- **ratings:** 3 replicas

### Access the Application
The script tries to obtain the service URL automatically.  
If needed, it can also be obtained manually:

```bash
minikube service productpage -n cdps-3 --url
```

### Remove the Deployment
```bash
python3 punto4.py borrar
```

This removes the `cdps-3` namespace and frees all cluster resources.

### Extra Cleanup Commands
If the environment fails due to memory or storage issues, the following commands may help:

```bash
minikube ssh -- docker system prune -a -f
cd practica_creativa2/bookinfo/src/reviews
docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build
```

---

## Kubernetes vs Docker: Key Differences When Scaling

### Pods vs Containers
In Kubernetes, you no longer manage containers directly as in Docker Compose, but **Pods**.  
Pods are ephemeral, have their own IP address, and provide more flexibility and decoupling.

### Scaling

#### Docker Compose
Scaling must be done manually using the `--scale` option.

#### Kubernetes
You simply declare the desired number of replicas in the YAML files.  
Kubernetes continuously ensures that the requested number of replicas is running.  
If a pod fails, Kubernetes automatically creates a new one.

### Load Balancing
Thanks to Kubernetes **Service** objects and internal DNS, no additional manual configuration is required.  
Traffic is automatically distributed among the available replicas.

---

## Weak Points of the Current Architecture

Although migrating to a microservices architecture with Kubernetes improves deployment and management significantly, the current implementation still has some weak points in terms of **reliability** and **scalability**.

### Reliability

#### Communication Between Microservices
The communication between services follows a chained structure:

```text
ProductPage → Reviews → Ratings
```

If the `Ratings` service becomes slow or fails, `Reviews` remains blocked waiting for a response, which can in turn block `ProductPage`.  
As a result, the failure of a single service may affect the whole application.

**Possible solution:**  
Use a service mesh such as **Istio**, which can apply timeouts, retries, and fallback responses to avoid cascading failures and improve resilience.

### Scalability

#### Fixed Number of Replicas
In the current version, the number of replicas is static.  
This is inefficient because:

- with low traffic, resources are wasted
- with high traffic, services may become saturated

**Possible solution:**  
Use **HPA (Horizontal Pod Autoscaler)** so Kubernetes can automatically increase or decrease the number of pods based on CPU or memory usage.

#### Missing Resource Limits
The Kubernetes YAML files do not define CPU or memory limits.  
Since containers share the host kernel, one microservice could consume too many resources and negatively affect the others.

**Possible solution:**  
Define:

- `resources.requests`
- `resources.limits`

for each Deployment, in order to guarantee balanced and stable resource usage.

---

## Conclusion
This project shows the evolution from a traditional monolithic deployment to a more modern microservices-based architecture managed with Docker and Kubernetes.

Throughout the assignment, the application has been deployed in four different ways, allowing us to compare:

- monolithic vs microservices architectures
- Docker vs Kubernetes
- manual vs declarative scaling
- basic deployment vs orchestrated deployment

This progression highlights the benefits of containerization and orchestration in terms of modularity, scalability, resilience, and maintainability.
