
import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "")

app = FastAPI(title="ECS Bedrock AI Service", version="1.0.0")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class AskResponse(BaseModel):
    answer: str


@app.get("/health")
def health():
    return {"status": "healthy", "service": "bedrock-ai"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not MODEL_ID:
        raise HTTPException(
            status_code=500,
            detail="BEDROCK_MODEL_ID is not configured",
        )

    try:
        response = bedrock.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": request.question}],
                }
            ],
            inferenceConfig={
                "maxTokens": 300,
                "temperature": 0.2,
            },
        )

        answer = response["output"]["message"]["content"][0]["text"]
        return AskResponse(answer=answer)

    except (ClientError, BotoCoreError):
        logger.exception("Bedrock invocation failed")
        raise HTTPException(
            status_code=502,
            detail="AI provider request failed",
        ) from None
