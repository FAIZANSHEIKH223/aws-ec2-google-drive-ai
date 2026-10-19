#!/usr/bin/env bash
set -euo pipefail

MODEL_FILE="models/model.gguf"
MODEL_NAME="${OLLAMA_MODEL:-drive-model}"

if [[ ! -f "$MODEL_FILE" ]]; then
  echo "ERROR: $MODEL_FILE does not exist."
  echo "The Google Drive download step has not been completed yet."
  exit 1
fi

if ! docker compose ps --status running --services | grep -qx ollama; then
  echo "Starting Ollama service..."
  docker compose up -d ollama
fi

echo "Waiting for Ollama API..."
for attempt in $(seq 1 30); do
  if curl --silent --fail http://127.0.0.1:11434/api/tags >/dev/null; then
    break
  fi
  sleep 2
done

if ! curl --silent --fail http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "ERROR: Ollama did not become ready."
  exit 1
fi

echo "Creating model '$MODEL_NAME' from $MODEL_FILE..."
docker compose exec -T ollama ollama create "$MODEL_NAME" -f /project/Modelfile
echo "Model '$MODEL_NAME' created."
echo "The model file is mounted read-only at /models/model.gguf inside the Ollama container."
