from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config.supabase import supabase

router = APIRouter(
    prefix="/api/prompts",
    tags=["prompts"]
)

# Structure attendue depuis Bubble ou ton backend LLM
class PromptEntry(BaseModel):
    prompt: str
    completion: str

@router.post("/")
def create_prompt(entry: PromptEntry):
    # insertion dans Supabase
    response = supabase.table("prompts").insert({
        "prompt": entry.prompt,
        "completion": entry.completion
    }).execute()

    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)

    return {
        "status": "success",
        "data": response.data[0]
    }

@router.get("/")
def list_prompts():
    response = supabase.table("prompts").select("*").order("created_at", desc=True).execute()
    data=response.data

    if data is None:
        return []


    return data
