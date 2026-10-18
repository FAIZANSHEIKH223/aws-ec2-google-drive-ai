
# AWS ECS Bedrock AI Service

A Python REST API running in Amazon ECS that uses Amazon Bedrock.

## Endpoints

- GET /health
- POST /ask

## Local setup

Install Python 3.12 and run:

    python -m venv .venv

Activate the virtual environment and install:

    pip install -r requirements.txt

Set AWS_REGION and BEDROCK_MODEL_ID, then configure AWS
authentication through your approved AWS profile or role.

Start the API:

    uvicorn app.main:app --reload --port 8000

Open http://127.0.0.1:8000/docs.

## Request example

POST /ask

    {
      "question": "Explain AWS ECS in simple words."
    }

Never commit AWS credentials. In ECS, use a dedicated task IAM role.
