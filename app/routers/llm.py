from fastapi import APIRouter
from pydantic import BaseModel
from app.config.llm import client

router = APIRouter(prefix="/api/llm", tags=["llm"])

class PromptRequest(BaseModel):
    prompt: str

@router.post("/generate")
def generate_text(request: PromptRequest):
    # Utilise GPT-4.1 (qualité optimale)
    response = client.responses.create(
        model="gpt-4.1-mini",  # simple et pas cher pour commencer
        input=request.prompt,
    )

    # La réponse est toujours dans response.output_text
    output = response.output_text

    return {
        "prompt": request.prompt,
        "completion": output
    }