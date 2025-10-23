# Stylo – AI Fashion Stylist

Stylo is an AI-powered fashion assistant that generates personalized outfit recommendations and photo-realistic visuals.  
It combines OpenAI (GPT-4o-mini) for fashion logic with Stable Diffusion XL (via Replicate) for image generation.  
The backend is built with FastAPI, fully asynchronous, containerized with Docker, automated through GitHub Actions, and deployable on Render.

---

## Tech Stack

- **Backend:** FastAPI (Python 3.11, async)
- **AI Models:** OpenAI GPT-4o-mini + Replicate SDXL
- **Infrastructure:** Docker & Docker Compose
- **CI/CD:** GitHub Actions → DockerHub → Render
- **Architecture:** Async, modular, and stream-enabled

---

## Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/stylo.git
cd stylo
```
### 2. (Optional) Create a local .env file
OPENAI_API_KEY=sk-xxxx
REPLICATE_API_TOKEN=r8_xxxx
REPLICATE_MODEL=stability-ai/sdxl
ENV=development

(In CI/CD and production, secrets are managed via GitHub Secrets and Render Environment variables.)

### 3. Run with Docker
docker compose up --build

The backend will be available at http://localhost:8000

API Overview

| Endpoint                     | Method | Description                            |
| ---------------------------- | ------ | -------------------------------------- |
| `/`                          | GET    | Liveness check                         |
| `/health`                    | GET    | Health status                          |
| `/ai/recommendations`        | POST   | Generate outfit recommendations (JSON) |
| `/ai/recommendations/stream` | POST   | Stream response in real time           |
| `/ai/generate-image`         | POST   | Generate AI image using SDXL           |


Example request:
curl -X POST http://localhost:8000/ai/recommendations \
  -H "Content-Type: application/json" \
  -d '{"clothing_item":"jacket","color":"black","style":["streetwear"],"gender":"men"}'


Key Features
- Generates outfit and color palette recommendations using OpenAI
- Produces AI-based fashion images via Stable Diffusion XL (Replicate)
- Supports real-time streaming (Server-Sent Events)
- Fully asynchronous and production-ready architecture
- Automated CI/CD pipeline that builds, tests, and pushes Docker images

Project Structure
backend/
├── app/
│   ├── main.py
│   ├── routers/
│   │   └── ai.py
│   ├── services/
│   │   └── recommendation_service.py
│   └── __init__.py
├── Dockerfile
└── requirements.txt

CI/CD Summary
GitHub Actions:
Builds → Tests → Pushes to DockerHub (with SHA and latest tags)
Cleans old tags automatically

Render:
Deploys the Docker image directly from DockerHub

Author
Jacob S.
DevOps & AI Developer – building systems that combine intelligent functionality with reliable infrastructure.