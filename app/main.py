from fastapi import FastAPI
from app.routers import test, projects, llm, rag, prompts
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="CIR Backend API",
    description="Backend utilisé par Bubble.io pour le projet CIR",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre plus tard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# On branche nos routes
app.include_router(test.router)
app.include_router(projects.router)
app.include_router(llm.router)
app.include_router(prompts.router)
app.include_router(rag.router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "ciria-api"}