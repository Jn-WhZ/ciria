from fastapi import FastAPI
from app.routers import test

app = FastAPI(
    title="CIR Backend API",
    description="Backend utilisé par Bubble.io pour le projet CIR",
    version="0.1.0"
)

# On branche nos routes
app.include_router(test.router)

@app.get("/")
async def root():
    return {"message": "API FastAPI opérationnelle !"}