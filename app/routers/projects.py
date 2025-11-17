from fastapi import APIRouter
from app.config.supabase import supabase

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/")
def list_projects():
    response = supabase.table("projects").select("*").execute()
    return response.data
