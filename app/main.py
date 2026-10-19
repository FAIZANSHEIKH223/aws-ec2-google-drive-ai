import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_NAME = "ec2-google-drive-ai"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "drive-model")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))

app = FastAPI(
    title="EC2 Google Drive AI API",
    description="A small API that forwards questions to a local Ollama model.",
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class AskResponse(BaseModel):
    answer: str
    model: str


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": APP_NAME,
        "status": "running",
        "health": "/health",
        "ask": "/ask",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
        tags = response.json().get("models", [])
        available_models = [item.get("name", "") for item in tags]
        model_available = any(
            name == OLLAMA_MODEL or name.startswith(f"{OLLAMA_MODEL}:")
            for name in available_models
        )
        return {
            "status": "ok",
            "ollama_reachable": True,
            "configured_model": OLLAMA_MODEL,
            "model_available": model_available,
        }
    except (requests.RequestException, ValueError):
        return {
            "status": "degraded",
            "ollama_reachable": False,
            "configured_model": OLLAMA_MODEL,
            "model_available": False,
        }


@app.post("/ask", response_model=AskResponse)
def ask(request_data: AskRequest) -> AskResponse:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": request_data.question}],
        "stream": False,
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Model '{OLLAMA_MODEL}' is not available in Ollama yet. "
                    "Download the model and run scripts/import_gguf_into_ollama.sh."
                ),
            )
        response.raise_for_status()
        result = response.json()
        answer = result.get("message", {}).get("content", "").strip()
        if not answer:
            raise HTTPException(status_code=502, detail="The model returned an empty answer.")
        return AskResponse(answer=answer, model=OLLAMA_MODEL)
    except HTTPException:
        raise
    except requests.Timeout as exc:
        raise HTTPException(status_code=504, detail="The model took too long to respond.") from exc
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not get a valid response from the local Ollama service.",
        ) from exc
