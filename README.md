# Welcome to Chat with Your Docs Repo
A lightweight Retrieval-Augmented Generation (RAG) demo that answers questions over uploaded documents. Built as an assignment project to demonstrate design choices, engineering standards, and a minimal working solution with LangChain + FastAPI backend and a Gradio frontend.

Here is a quick demo of application:

<video src="./src/resources/App_live_demo.mp4" controls width="600"></video>


## Task receipt & plan
I'll add a single, focused README that documents: quick setup, architecture, RAG decisions, productionization notes, engineering trade-offs, and how AI tools were used. After this change the repo will have a ready-to-read guide for reviewers.

## Requirements checklist
- Provide quick setup instructions — Done
- Architecture overview and simple diagram — Done
- Productionization & scaling notes for AWS/GCP/Azure — Done
- RAG/LLM approach, model choices and decisions — Done
- Key technical decisions and rationale — Done
- Engineering standards used — Done
- How AI tools were used in development — Done
- What would be done with more time — Done

## TL;DR
- What this repo contains: a FastAPI-based API (src/app) that performs ingestion and RAG-style question answering, a small Gradio UI (src/frontend/gradio_app.py), and Docker/Docker Compose files for quick local runs.
- Run locally: create a Python venv, install requirements, and start the API and optional Gradio UI. See Quick start below.

## Quick start (local)
Prereqs:
1. You need to have Git CLI, Make tools and Docker installed.
2. You would need an OpenAI API key.

### Quick start (Docker):
1. **Clone and create venv**

```bash
git clone https://github.com/geekychandraul/chat-with-your-docs.git
cd chat-with-your-docs
```
2. **Create local config file**
```bash
cp src/config/serverlocal_template.cfg src/config/serverlocal.cfg
```
Update values of `OPENAI_API_KEY` with the api key. You can change other configs as per your requirement.

3. **Run `make` command**
```bash
make init`
```
This will start docker container for the app and also set up application with db migrations.
4. **Access the application**
Access the frontend app on `http://localhost:7860/`
Access the backend app on `http://localhost:9000/docs`

## How to use the App:
1. Open `http://localhost:7860/`
2. Click on `Register`.
3. Login with your creds.
4. Upload .pdf, .docx or .txt file.
5. Start having conversation on all the docs you have added.


## Architecture (simple)
**ASCII diagram (simple)**
```
[User / Gradio UI] <---> [FastAPI (src/app)] <---> [RAG service: retriever + LLM]

|---> Vector DB (Chroma / in-repo directory)
|---> Embedding model / LLM (configurable)
|---> Postgres (metadata, users)
```

**Components**
- FastAPI: REST endpoints for ingest, auth, chat, health.
- Ingest pipeline: chunking -> embedding -> upsert into vector store
- Retriever: nearest-neighbor search using vector DB
- LLM: accepts retrieved context + user prompt, returns answer
- Gradio frontend: small demo UI for file upload and chat
- Metrics & observability: LangSmith is added

**Folder Structure**:

`src/app` -> Fastapi backend project directory

`src/frontend` -> Gradio frontend of app

`src/config` -> config files for each env to chagne values per env

`src/resources` -> static content for repo

`src/app/apis` -> contains all api routes from fastapi.

`src/app/core` -> Contains all core logic like setting up db, configs, llms etc

`src/app/models` -> Contains tables/models which needs to be added.

`src/app/repositories` -> Contains db operation on models

`src/app/schemas` -> Pydantic schema for apis

`src/app/services` -> Core business logic

`src/app/utils` -> helper functions

## RAG / LLM approach & decisions
This repo is a demonstration; the code is built to let you swap providers and vector stores via config.

**Choices I considered**
- LLM providers: OpenAI, Anthropic, local (e.g., Ollama)
- Embedding models: OpenAI text-embedding-3-small, or local SentenceTransformers
- Vector DB: Chroma (lightweight, embeddable), Pinecone, or FAISS
- Orchestration: simple monolith with separate services (FastAPI + Gradio) vs microservices with queues (Celery / Kafka) for large-scale ingestion

**Final choices for this assignment**
- LLM: defaulted to the project-configurable provider (commented in `src/app/core/config.py`). I kept the integration generic so reviewers can plug their API keys. For quick tests use a local or low-cost provider.
- Embeddings: pluggable; default configuration references a commonly available model in `config.py`.
- Vector DB: Chroma (lightweight and file-backed; present under `data/chroma/`) to keep the repo self-contained.
- Orchestration: simple monolith (FastAPI + background tasks). This keeps the surface small and easy to evaluate in a timed assignment.

**Prompt & context management**
- The app retrieves top-k (4) documents, concatenates short summaries or chunks, and injects them into a template prompt. The prompt template is editable in code and stored as a constant for easy iteration.

**Guardrails, quality and observability**
- Input size checks and chunking limits are enforced at ingestion.
- Response streaming for LLMs (where supported) is implemented in `src/app/apis/v1/chat.py`.
- Basic logging is set up in `src/app/core/logging.py`. Health checks live under `src/app/apis/v1/health.py`.

**Why these choices**
- Use lightweight, swappable components so the assignment focuses on architecture and trade-offs rather than vendor lock-in.

## What would be required to productionize and scale
- Move to managed vector DB (e.g., Pinecone or managed Milvus) for multi-node availability and fast ANN search.
- Use managed LLM endpoints or autoscaled model-serving infra (e.g., AWS Bedrock, Azure OpenAI, or dedicated inference clusters).
- Add an ingestion queue (e.g., SQS + worker autoscaling or Kafka + consumers) for large/slow uploads.
- Add robust auth (OAuth2 / OIDC), rate limiting, and per-user quotas.
- Metrics & observability: instrument with Prometheus + Grafana, export logs to ELK or a log provider, and trace requests with OpenTelemetry.
- Security: secret management (AWS Secrets Manager / HashiCorp Vault), network isolation (VPCs), and hardening of DB access.
- CI/CD: pipeline for linting, tests, container build, and infra-as-code (Terraform / CloudFormation) for reproducible deploys.

Below is the architechture diagram I would propose:
![High Level Architecture Diagram](./src/resources/HLD.png)

## Key technical decisions and rationale
- Monolith + background tasks: faster to iterate and evaluate in an assignment setting.
- Chroma as vector DB: local, file-backed, easy to demo without external keys.
- Pluggable model integrations: reviewers can swap providers by changing config.

## Engineering standards followed
- Python typing where practical in src/ (pydantic models for API schemas).
- Structured logging, modular service separation (apis/services/repositories).
- Dockerfile + docker-compose for reproducible env.
- Small unit of functionality per endpoint and single-responsibility for services.

**Standards skipped (due to time)**
- Full e2e tests and performance benchmarks, advanced security hardening, multi-region deployment examples.

## How I used AI tools during development
- I used AI coding assistants to generate small helper snippets and to summarize complex pieces of documentation. For each generated patch I:
	- Reviewed and edited the output manually.
	- Ensured it matched project style and type hints.
	- Wrote tests or manual checks for core paths rather than blindly accepting generated code.

Notes on provenance: This README documents my thoughts and decisions. I used AI tools sparingly to accelerate boilerplate creation and then validated everything by hand.

## What I'd do differently with more time
- Add thorough unit and integration tests (ingest pipeline + retrieval accuracy tests).
- Add more observability (tracing + dashboards) and structured benchmarks for retrieval latency and end-to-end QA.
- Implement multi-tenant and RBAC controls for enterprise use.

## Running tests (if present)
- There are limited unit tests in the repo. To run tests (if pytest is added):

```bash
pytest -q
```

## Files / where to look
- `src/app` — API and services
- `src/frontend/gradio_app.py` — simple Gradio demo
- `src/run_server.py` — uvicorn launcher
- `docker-compose.yml`, `Dockerfile-gradio` — containers and demo UI
- `Makefile` - contains make commands to work with app.
## Submission checklist (for the assignment)
1. GitHub repo with code — this repository
2. README.md (this file) with:
	 a. Quick setup instructions — see Quick start
	 b. Architecture overview — see Architecture
	 c. Productionization notes — see Productionize
	 d. RAG/LLM approach & decisions — see RAG / LLM approach
	 e. Key technical decisions — see Key technical decisions
	 f. Engineering standards — see Engineering standards
	 g. How AI tools were used — see How I used AI tools
	 h. What I’d do differently — see What I'd do differently with more time

## Notes & known limitations
- This is a demo assignment; some operational concerns are intentionally simplified to fit time constraints (see "Standards skipped").
