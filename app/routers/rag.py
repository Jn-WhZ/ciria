from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config.supabase import supabase
from app.utils.text_extraction import extract_text
from app.utils.cleaning import clean_text
from app.utils.chunking import split_into_chunks
from app.utils.embeddings import embed_text
from app.config.rag import client
import threading

router = APIRouter(prefix="/api/rag", tags=["RAG"])


def process_rag_background(source_id, text):
    chunks = split_into_chunks(text)

    for i, chunk in enumerate(chunks):
        try:
            chunk = clean_text(chunk)
            vector = embed_text(chunk)
            supabase.table("chunks").insert({
                "source_id": source_id,
                "chunk_index": i,
                "chunk_text": chunk,
                "vector": vector
            }).execute()
        except:
            continue



# 1. UPLOAD DOCUMENT → CHUNKS → EMBEDDINGS → SUPABASE
@router.post("/upload")
async def upload_document(project_id: str, file: UploadFile = File(...)):
    try:
        # 1) Extraction du texte
        text = extract_text(file)

        # 2) Enregistrer la source brute
        source = supabase.table("sources").insert({
            "project_id": project_id,
            "filename": file.filename,
            "original_text": clean_text(text)
        }).execute()

        source_id = source.data[0]["id"]
        threading.Thread(target=process_rag_background, args=(source_id, clean_text(text))).start()
        return {"status": "processing", "source_id": source_id}
