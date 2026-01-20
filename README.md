# Welcome to Chat with Your Docs Repo
A lightweight production grade Retrieval-Augmented Generation (RAG) demo that answers questions over uploaded documents. Built as an project to demonstrate design choices, engineering standards, and a minimal working solution with LangChain + FastAPI backend and a Gradio frontend.

Here is a quick demo of application:

<video src="./src/resources/App_live_demo.mp4" controls width="600"></video>


## TL;DR
- Core Idea: This app is a production grade starter app in modular fasion to enable developers to add more features.
- What this repo contains: a FastAPI-based API (src/app) that performs ingestion and RAG-style question answering, a small Gradio UI (src/frontend/gradio_app.py), and Docker/Docker Compose files for quick local runs.
- Run locally: create a Python venv, install requirements, and start the API and optional Gradio UI. See Quick start below.

## Local Setup

Prereqs:
1. You would need an OpenAI API key.
2. (Optional) LangSmith API key.
3. (Optional) You need to have Make tools and Docker installed.

**Steps**

1. **Clone and create venv**

```bash
git clone https://github.com/geekychandraul/chat-with-your-docs.git
cd chat-with-your-docs
```

2. **Create local config file**
```bash
cp src/config/serverlocal_template.cfg src/config/serverlocal.cfg
```
Update values of `LLM_API_KEY` with the OpenAI api key (if using OpenAI). You can change other configs as per your requirement.

3. **Run fastapi application**

    a. Option 1: Easiest way: Using Make command and docker command
    ```bash
    make init
    ```
    This will start docker container for the app and also set up application with db migrations.

    b. Option 2: Using `uvicorn`

    1. To create virtual env:

            ```shell
            python -m venv .venv
            source .venv/bin/activate
            pip install -r requirements.txt
            ```

       2. Install and connect to postgres db. Run

        ```shell
        psql postgres
        ```

        3. To setup db, run belwo sql:

        ```sql
        CREATE USER hello_fastapi WITH PASSWORD 'hello_fastapi';
        CREATE DATABASE rag_db OWNER hello_fastapi;
        ```
        We could automate that but we already have production grade docker compose file.

        4. Run below command to run mirgrations and run python server:

        ```shell
        cd src/
        alembic upgarde head
        python run_server.py
        ```

        5. To run Frontend

        ```shell
        python src/frontend/gradio_app_local.py
        ```

4 . **Access the application**

Access the backend app on `http://localhost:9000/docs`

Access the frontend app on `http://localhost:7860/`

## How to use the App:
1. Open `http://localhost:7860/`
2. Click on `Register` and enter details.
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

### Choices I considered
- Directory/code structure: The hardest decision was how to keep code. The options were a simple fastapi structure or a jupyter notebook or full fledged prod ready application. Considering we are building a prod ready app.
- Tech Stack: Python, JS, Docker, CI/CD deployments, Test cases, GenAI Framework(OpenAI sdk, Langchain, custom code, DSpy ).
- LLM providers: OpenAI, Anthropic, Google Gemini, local (e.g., Ollama)
- Embedding models: OpenAI text-embedding-3-small, Huggingface, or local (Ollama)
- Vector DB: Chroma (lightweight, embeddable), Pinecone, or FAISS
- RDBMS : MySQL, PostgresSQL
- Orchestration: simple monolith with separate services (FastAPI + Gradio) vs microservices with queues (Celery / Kafka) for large-scale ingestion


**Why these choices**

I have considered below based on the one fact: **Can the app be deployed and hosted as application.**

### Final choices for this project
- Modular Code: Production level code directories: creating a simple one file fastapi or a jupyter notebook is noobs way. Getting a full fledged repo with modular directory structure give us speed and enables to add more features quickly.
- LLM: Defaulted to gpt-5-mini. I kept the integration generic so developer can plug their API keys. For quick tests use a local or low-cost provider.
- Embeddings: text-embedding-3-small but pluggable; default configuration references in server config files.
- Vector DB: Chroma (lightweight and file-backed; present under `data/chroma/`) to keep the repo self-contained. For now when we have small dataset but would move to pgVector once the code is ready to deploy as it integrates very well with Postgres.
- RDBMS: Most prod app uses postgres as backend DB. using MySQL in memory might become a single point failure in future as chroma was already in memory db.
- Orchestration: simple monolith (FastAPI + background tasks). This keeps the surface small and easy to evaluate in a timed assignment.

### Prompt & context management
- The app retrieves top-k (4) documents, concatenates chunks, and injects them into a template prompt. The prompt template is editable in code and stored as a constant for easy iteration.
- A working example is also shown in attached recording.

### Guardrails, quality and observability
- Input size checks and chunking limits are enforced at ingestion.
- Response streaming for LLMs (where supported) is implemented in `src/app/apis/v1/chat.py`.
- Basic logging is set up in `src/app/core/logging.py`. Health checks live under `src/app/apis/v1/health.py`.

## Key Acomplishements and Challanges:
- **Boiler Plate Code:** Writing boiler plate code and converting a workign POC jupyter notebook to full fledged code.
- **Streaming:** I could have sent the full data in a single response. But having a prod ready feature to incorporate streaming was important which as per my analysis langchain does not support out of the box if we use chain. Converting the PoC code into a full SSE endpoint was really fun.
- **Gradio:** In PoC project, I had used a gradio's inbuilt simple chat interface but adding states and manage visibility was a learning curve to convert the app into a full prod ready app.
- **Permissioning:** User base permissioning around files. This prompted me to add auth module.
- **Containers:** Creating full fledged docker continer to run local servers. Writing docker files and make file was worth the effort. Adding config in make file to pick from server config file instead of hardcoding was a fun challange.
- **Observability & Telemerties:** I have extensively used otel module directly and controlling what gets sent. Comparning on how to do at code level without spending money and learning to use langsmith was a learning curve.
- **Config settings:** Creating a config setting files to think of all the secenarios and converting them to server configs.
- **Pre-commit and linting:** though Linting and fomratting will be handled in CI pipeline but adding it at commit level incresaes standards.
- **User based file segration**: Now different users can upload same files to create permission boundaries so that user data is independent.

## Other Features Skipped (due to time constraint)
- **LLM Core Class:** Common class to handle different LLM provider. This will enable us to use different models from dropdown.
- **Using correct embedding model per requirement:** Change embedding model on run time depending on the usecase by adding a plugin module and make sure that for future case, same model is used. Like for code parsing or meeting intelligence use `nomic-embed-code` or `text-embedding-3-large`. but for career intelligence a small model would suffice.
- **Enriching Embeddings:** Code to migarate or rank embeddings to get more relevant embeddings. Also converting each file into set of question answer pair using some low models would really improve the embeddings.
- Adding custom telemetries
- **Infra as code: **Terraform code to convert this repo into infra as code to enable self provisioning deployments.
- **Test Cases: **More refined unit and integration test cases with db and fake session(sessionFactory)
- **Re-Rank Retrieved Embeddings: **To make embedding context more richer, adding a rerank or fusion rag would make more sense. This is a future scope, which is must to the app to next level.
- Hosting app using gunicorn + uvicorn to give it more worked node.
- **Rate Limiting: **Handeling rate limiting and storing files in s3 or azure blob instead of temp memory.
- **Permissioning:** Conversation based permissioning on uploaded files. To make sure current converstion has context about current files uploaded.
- **Cache Layer:** adding a redis cache layer will enhance app speed and cost for same kind of application.


## What would be required to productionize and scale
- If the scale of application is huge, then move to managed vector DB (e.g., Pinecone or managed Milvus) for multi-node availability and fast ANN search.
- Use managed LLM endpoints or autoscaled model-serving infra (e.g., AWS Bedrock, Azure OpenAI, or dedicated inference clusters) to avoid rate limits.
- Add an ingestion queue (e.g., SQS + worker autoscaling or Kafka + consumers) for large/slow file uploads (text or audio, video).
- Add robust auth (OAuth2 / OIDC), rate limiting, and per-user quotas.
- Metrics & observability: instrument with Prometheus + Grafana, export logs to ELK or a log provider, and trace requests with OpenTelemetry.
- Security: secret management (AWS Secrets Manager / HashiCorp Vault), network isolation (VPCs), and hardening of DB access.
- CI/CD: pipeline for linting, tests, container build, and infra-as-code (Terraform / CloudFormation) for reproducible deploys.

Below is the architechture diagram I would propose:
![High Level Architecture Diagram](./src/resources/HLD.png)

## Key technical decisions and rationale
- Monolith + background tasks: faster to iterate and evaluate in an assignment or build fast, deploy fast setting.
- Chroma as vector DB: local, file-backed, easy to demo without external keys. But easily changable.
- Pluggable model integrations: reviewers can swap providers by changing config.

## Engineering standards followed
- Added Python typing where practical in all python code.
- Structured logging, modular service separation (apis/services/repositories).
- Dockerfile + docker-compose for reproducible env.
- Small unit of functionality per endpoint and single-responsibility for services.

## How I used AI tools during development
- I used copilot assistant to generate small helper snippets and to summarize complex pieces of documentation. For each generated patch I:
	- Reviewed and edited the output manually.
	- Ensured it matched project style and type hints.
	- Wrote tests or manual checks for core paths rather than blindly accepting generated code.

Note: 80% of this readme is written by hand to make sure correct picture of what can be achieved and what is needed to achieve the goal is provided.

## What I'd do differently with more time
- Add thorough unit and integration tests (ingest pipeline + retrieval accuracy tests).
- Add more observability (tracing + dashboards) and structured benchmarks for retrieval latency and end-to-end QA.
- Implement multi-tenant and RBAC controls for enterprise use.

## Running tests (if present)
- I will be adding test cases to the repo soon.


## Files / where to look
- `src/app` — API and services
- `src/app/services/chat_service.py` - core chat logic
- `src/app/services/ingest_service.py` - core ingestion logic
- `src/frontend/gradio_app.py` — simple Gradio demo
- `src/run_server.py` — uvicorn launcher
- `docker-compose.yml`, `Dockerfile-gradio` — containers and demo UI
- `Makefile` - contains make commands to work with app.

## Notes & known limitations
- This is a demo assignment; some operational concerns are intentionally simplified to fit time constraints (see "Standards skipped").
