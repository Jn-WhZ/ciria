import threading
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config.supabase import supabase
from app.utils.cleaning import clean_text
from app.utils.text_extraction import extract_text
from app.utils.chunking import split_into_chunks
from app.utils.embeddings import embed_text
from app.config.rag import client

router = APIRouter(prefix="/api/rag", tags=["RAG"])

# ---------- BACKGROUND PROCESS ----------
def process_full_rag_pipeline(source_id: str, file_path: str, filename: str):
    try:
        # 1. Télécharger le fichier depuis Supabase Storage
        print("Downloading file from storage...")
        file_resp = supabase.storage.from_("RAG_uploads").download(file_path)
        file_bytes = file_resp  # raw bytes

        # 2. Extraire le texte
        print("Extracting text...")
        text = extract_text_from_bytes(file_bytes, filename)
        text = clean_text(text)

        # 3. Stocker le texte brut dans la table sources
        supabase.table("sources").update({
            "original_text": text
        }).eq("id", source_id).execute()

        # 4. Chunking
        chunks = split_into_chunks(text)

        # 5. Embeddings + insertion
        for idx, chunk in enumerate(chunks):
            try:
                chunk = clean_text(chunk)
                vector = embed_text(chunk)

                supabase.table("chunks").insert({
                    "source_id": source_id,
                    "chunk_index": idx,
                    "chunk_text": chunk,
                    "vector": vector
                }).execute()
            except Exception as e:
                print("Chunk failed:", idx, str(e))
                continue

        print("RAG ingestion complete for source:", source_id)

    except Exception as e:
        print("Background task error:", str(e))


# ---------- UPLOAD ENDPOINT ----------
@router.post("/upload")
async def upload_document(project_id: str, file: UploadFile = File(...)):
    try:
        # 1. Upload du fichier vers Supabase Storage
        print("Uploading file to storage...")
        file_bytes = await file.read()

        file_path = f"{project_id}/{file.filename}"

        supabase.storage.from_("RAG_uploads").upload(
            file_path,
            file_bytes,
            {"content-type": file.content_type}
        )

        # 2. Créer entrée source avec texte vide
        source = supabase.table("sources").insert({
            "project_id": project_id,
            "filename": file.filename,
            "original_text": ""
        }).execute()

        source_id = source.data[0]["id"]

        # 3. Lancer la pipeline entière en async
        threading.Thread(
            target=process_full_rag_pipeline,
            args=(source_id, file_path, file.filename)
        ).start()

        # 4. Retourner immédiatement une réponse rapide
        return {
            "status": "processing",
            "source_id": source_id,
            "file_stored": file.filename
        }

    except Exception as e:
        raise HTTPException(500, str(e))
