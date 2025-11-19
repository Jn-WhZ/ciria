from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config.supabase import supabase
from app.utils.text_extraction import extract_text
from app.utils.chunking import split_into_chunks
from app.utils.embeddings import embed_text
from app.config.rag import client

router = APIRouter(prefix="/api/rag", tags=["RAG"])

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
            "original_text": text
        }).execute()

        source_id = source.data[0]["id"]

        # 3) Chunking
        chunks = split_into_chunks(text)

        # 4) Embeddings + stockage
        for i, chunk in enumerate(chunks):
            vector = embed_text(chunk)

            supabase.table("chunks").insert({
                "source_id": source_id,
                "chunk_index": i,
                "chunk_text": chunk,
                "vector": vector
            }).execute()

        return {"status": "ok", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(500, str(e))


# 2. RETRIEVAL VECTORIEL
@router.post("/search")
async def search_context(query: str, match_count: int = 5):
    try:
        query_embedding = embed_text(query)

        response = supabase.rpc("match_chunks", {
            "query_embedding": query_embedding,
            "match_count": match_count
        }).execute()

        return response.data
    except Exception as e:
        raise HTTPException(500, str(e))


# 3. GENERATION RAG
@router.post("/generate")
async def rag_generate(query: str, match_count: int = 5):
    try:
        # 1) Récupérer les meilleurs chunks
        contexts = await search_context(query, match_count)

        context_text = "\n\n---\n\n".join([c["chunk_text"] for c in contexts])

        prompt = f"""
Tu es un expert CIR/CII.
Réponds uniquement en utilisant les sources ci-dessous.
Ne fais aucune supposition.

=== CONTEXTES ===
{context_text}

=== QUESTION ===
{query}

Fournis une réponse technique, structurée et sourcée.
"""

        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )

        return {
            "answer": response.output_text,
            "sources": context_text
        }
    except Exception as e:
        raise HTTPException(500, str(e))
