# AWS EC2 + Google Drive AI

A beginner-friendly project for running a local open-source language model on an EC2 instance.
The model file will be stored in your Google Drive and downloaded to EC2 during a later setup step.

## Architecture

- FastAPI: provides `/health` and `/ask`.
- Ollama: runs the local language model.
- Docker Compose: runs the API and Ollama.
- `models/model.gguf`: expected location for a GGUF model downloaded from Google Drive in a later step.
- Terraform and Jenkins deploy/destroy files will be added in later project steps.

## Important

- Do not commit model files, Google credentials, OAuth tokens, or AWS credentials to Git.
- This starter intentionally binds API and Ollama ports to `127.0.0.1` only. Do not expose them publicly yet.
- A model must be downloaded and imported into Ollama before `/ask` can return an answer.
- This repository does not yet create AWS resources or configure Google Drive access. We will add and test those steps separately.

## Repository layout

```text
aws-ec2-google-drive-ai/
├── app/
│   ├── __init__.py
│   └── main.py
├── models/
│   └── .gitkeep
├── scripts/
│   ├── health_check.sh
│   └── import_gguf_into_ollama.sh
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Modelfile
├── requirements.txt
└── README.md
```

## Prerequisites for a local smoke test

- Git
- Docker Engine and Docker Compose plugin
- An open-source GGUF model file you are legally allowed to use

## 1. Configure the model

Copy `.env.example` to `.env`. Choose a model name:

```bash
cp .env.example .env
```

The Google Drive download step will eventually place the model file at:

```text
models/model.gguf
```

The model file is intentionally not included in Git.

## 2. Import the GGUF file into Ollama

After the model file has been downloaded to `models/model.gguf`, run:

```bash
chmod +x scripts/import_gguf_into_ollama.sh
docker compose up -d ollama
./scripts/import_gguf_into_ollama.sh
```

The script creates the Ollama model named in `.env` (default `drive-model`).

## 3. Start the API

```bash
docker compose up -d --build
```

Check health:

```bash
./scripts/health_check.sh
```

Test the AI API:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain AWS EC2 in simple words."}'
```

## API endpoints

- `GET /health` — confirms the API is running and reports whether Ollama is reachable.
- `POST /ask` — accepts `{"question":"..."}` and returns `{"answer":"..."}`.

## Next project steps

1. Create this GitHub repository and push these starter files.
2. Select and validate a small model.
3. Set up authenticated Google Drive model download without storing secrets in Git.
4. Add isolated Terraform for EC2.
5. Add `Jenkinsfile_ai_deploy` and `Jenkinsfile_ai_destroy` to the existing CI/CD repository, as requested.
