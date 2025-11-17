from fastapi import APIRouter
from fastapi import Depends, HTTPException
from app.models.example import ExampleRequest, ExampleResponse
from app.utils.security import verify_token

router = APIRouter(
    prefix="/api",
    tags=["bubble"]
)

@router.get("/ping")
async def ping():
    return {"status": "success", "message": "FastAPI répond à Bubble !"}


@router.post("/generate", response_model=ExampleResponse)
async def generate(req: ExampleRequest):
    result = req.text.upper()
    return ExampleResponse(
        original=req.text,
        transformed=result
    )


@router.post("/secure-endpoint", response_model=ExampleResponse)
async def secure_generate(
    req: ExampleRequest,
    token: str = Depends(verify_token)
):
    result = f"Secure reverse: {req.text[::-1]}"
    return ExampleResponse(
        original=req.text,
        transformed=result
    )
