from app.config.supabase import supabase
from app.utils.embeddings import embed_text


def retrieve_relevant_chunks(project_id: int, query: str, top_k: int = 5):
    """
    Returns the top K most relevant chunks for a project.
    """

    # 1. Embed the user query
    query_vector = embed_text(query)

    # 2. Query Supabase with pgvector similarity search
    response = supabase.rpc(
        "match_chunks",
        {
            "query_vector": query_vector,
            "project": project_id,
            "match_count": top_k
        }
    ).execute()

    # Expected output:
    # [{"chunk_text": "...", "source_id": 3, "filename": "doc.pdf"}]

    return response.data or []
