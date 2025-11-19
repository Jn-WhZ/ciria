from app.config.rag import client, EMBEDDING_MODEL

def embed_text(text):
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding
