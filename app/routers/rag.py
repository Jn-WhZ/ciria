import threading
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config.supabase import supabase
from app.utils.text_extraction import extract_text_from_bytes
from app.utils.cleaning import clean_text
from app.utils.chunking import split_into_chunks
from app.utils.embeddings import embed_text
from app.utils.file_naming import sanitize_filename


router = APIRouter(prefix="/api/rag", tags=["RAG"])


# ------------------------------
# BACKGROUND RAG INGESTION
# ------------------------------
def process_full_rag_pipeline(source_id: str, file_path: str, filename: str):
    try:
        # 1. Download file from storage
        try:
            file_bytes = supabase.storage.from_("rag_uploads").download(file_path)
            supabase.table("sources").update({"status": "extracting"}).eq("id", source_id).execute()
        except Exception as e:
            print("❌ Storage download failed:", str(e))
            supabase.table("sources").update({
                "original_text": f"ERROR: cannot download file: {str(e)}"
            }).eq("id", source_id).execute()
            return

        # 2. Extract text
        try:
            text = extract_text_from_bytes(file_bytes, filename)
            text = clean_text(text)
            supabase.table("sources").update({"status": "extracted"}).eq("id", source_id).execute()
        except Exception as e:
            print("❌ Text extraction failed:", str(e))
            supabase.table("sources").update({
                "original_text": f"ERROR: extraction failed: {str(e)}"
            }).eq("id", source_id).execute()
            return

        # 3. Save extracted text into source
        supabase.table("sources").update({
            "original_text": text
        }).eq("id", source_id).execute()

        # 4. Chunking
        try:
            chunks = split_into_chunks(text)
            supabase.table("sources").update({"status": "chunking"}).eq("id", source_id).execute()
        except Exception as e:
            print("❌ Chunking failed:", str(e))
            supabase.table("sources").update({
                "original_text": f"ERROR: chunking failed: {str(e)}"
            }).eq("id", source_id).execute()
            return

        # 5. Embeddings + DB insert
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
                print(f"⚠️ Chunk {idx} skipped:", str(e))
                continue
        supabase.table("sources").update({"status": "indexed"}).eq("id", source_id).execute()
        print(f"✅ RAG ingestion complete for source {source_id}")

    except Exception as unexpected:
        print("🔥 Unexpected error in background task:", str(unexpected))
        supabase.table("sources").update({
            "original_text": f"ERROR: unexpected failure: {str(unexpected)}",
            "status":"error"
        }).eq("id", source_id).execute()


# ------------------------------
# UPLOAD DOCUMENT (STORAGE + BACKGROUND PROCESS)
# ------------------------------
@router.post("/upload")
async def upload_document(project_id: str, file: UploadFile = File(...)):
    try:
        # Read file bytes
        file_bytes = await file.read()
        sanitized_filename = sanitize_filename(file.filename)
        file_path = f"{project_id}/{sanitized_filename}"


        # 1. TRY UPLOAD TO STORAGE (WITH UPSERT)
        try:
            supabase.storage.from_("RAG_uploads").upload(
                file_path,
                file_bytes,
                {
                    "content-type": file.content_type,
                    "upsert": "true"  # <---- KEY FIX !!
                }
            )
        except Exception as e:
            # If failure, return controlled error
            return {
                "status": "error",
                "message": f"Storage upload failed: {str(e)}"
            }

        # 2. INSERT SOURCE RECORD
        try:
            source = supabase.table("sources").insert({
                "project_id": [int(project_id)],
                "filename": sanitize_filename,
                "original_text": "",  # filled later
                "file_type":str(file.content_type),
                "status":"analyse"
            }).execute()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Supabase insert failed: {str(e)}"
            }

        source_id = source.data[0]["id"]

        # 3. START BACKGROUND THREAD
        threading.Thread(
            target=process_full_rag_pipeline,
            args=(source_id, file_path, filename)
        ).start()

        # 4. RETURN IMMEDIATE RESPONSE
        return {
            "status": "processing",
            "source_id": source_id,
            "filename": filename
        }

    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")


@router.get("/sources/{project_id}")
def list_sources(project_id: str):
    try:
        response = supabase.table("sources") \
            .select("filename, created_at, file_type, status") \
            .contains("project_id", [int(project_id)]) \
            .order("created_at", desc=True) \
            .execute()

        return {
            "project_id": project_id,
            "count": len(response.data),
            "sources": response.data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch sources: {str(e)}"
        }