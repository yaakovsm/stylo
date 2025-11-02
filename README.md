# Stylo – AI Fashion Stylist  

**Stylo** is an AI-powered fashion assistant that generates personalized outfit recommendations and photo-realistic visuals.  
This project showcases **end-to-end DevOps practices** — from containerized microservices and CI/CD automation to cloud deployment and AI integration.


![stylo-preview](https://github.com/yaakovsm/stylo/assets/preview-example.png)
*(Application preview – AI-generated fashion recommendations and images)*

---

## Table of Contents

1. [Key Features](#key-features)  
2. [Project Architecture](#project-architecture)  
3. [Project Prerequisites](#project-prerequisites)  
4. [Tech Stack](#tech-stack)
5. [Example API Endpoints](#example-api-endpoints)  
6. [CI/CD Flow](#cicd-flow)  

---

## Key Features

- **AI-Generated Fashion**: Combines GPT-4o-mini (OpenAI) for outfit logic and Replicate SDXL for image generation.  
- **Modern Full-Stack Architecture**: React frontend and FastAPI backend, both containerized.  
- **Real-Time Streaming**: Live AI responses using Server-Sent Events (SSE).  
- **CI/CD Automation**: GitHub Actions builds, tests, and deploys via DockerHub and Render.  
- **Cloud Deployment**: Production-ready environment with CORS, health checks, and secret management.  
- **Scalable Design**: Async Python backend and modular code structure.

---

## Project Architecture

The project is structured as a **full DevOps pipeline** deployed to the cloud:

1. **Application Layer (this repository)**  
   - **Frontend**: React + Vite + TypeScript interface for generating and displaying outfits.  
   - **Backend**: FastAPI (Python 3.11) providing RESTful endpoints and integrating OpenAI & Replicate models.  
   - **Docker Compose**: Orchestrates multi-service setup with isolated networks and health checks.

2. **CI/CD Pipeline (GitHub Actions)**  
   - Builds and tests Docker images for both services.  
   - Pushes versioned tags (by commit SHA) to **DockerHub**.  
   - Cleans outdated image tags automatically.  
   - Uploads digest artifacts for deployment tracking.

3. **Deployment (Render Cloud)**  
   - Automatically pulls latest Docker images from DockerHub.  
   - Environment variables (API keys, URLs) securely managed.  
   - Includes `/health` endpoint for liveness monitoring.

---

## Project Prerequisites

To run or extend this project, ensure you have:

- **Docker & Docker Compose**  
- **Python 3.11+** (for local backend testing)  
- **Node.js 18+** (for frontend builds)  
- **GitHub Account** (for CI/CD pipeline)  
- **Render Account** (for cloud hosting)  
- **API Keys** from:
  - [OpenAI](https://platform.openai.com/)
  - [Replicate](https://replicate.com/)

---

## Tech Stack

| Category | Technology |
|-----------|-------------|
| **Frontend** | React + Vite + TypeScript + TailwindCSS |
| **Backend** | FastAPI (Python 3.11, async) |
| **AI Integration** | OpenAI GPT-4o-mini · Replicate SDXL |
| **Containerization** | Docker & Docker Compose |
| **CI/CD** | GitHub Actions → DockerHub → Render |
| **Monitoring** | Health Checks (`/` and `/health`) |
| **Architecture** | Asynchronous, modular, production-ready |

---

## Example API Endpoints

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/` | GET | Liveness check |
| `/health` | GET | Health status |
| `/ai/recommendations` | POST | Generate outfit recommendations |
| `/ai/recommendations/stream` | POST | Stream real-time recommendations |
| `/ai/generate-image` | POST | Generate AI fashion image |

**Example Request:**
```bash
curl -X POST http://localhost:8000/ai/recommendations \
  -H "Content-Type: application/json" \
  -d '{
        "clothing_item": "jacket",
        "color": "black",
        "style": ["streetwear"],
        "gender": "men"
      }'
```

---

## CI/CD Flow

1. Developer pushes code → GitHub Actions triggered.  

2. Workflow builds backend & frontend Docker images.

3. Images tagged and pushed to DockerHub (`latest` + commit SHA).

4. Render automatically pulls and deploys latest containers.

5. Health checks confirm successful deployment.

---
