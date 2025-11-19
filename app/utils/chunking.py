import tiktoken

def split_into_chunks(text, max_tokens=800, overlap=200):
    encoding = tiktoken.encoding_for_model("gpt-4o")
    tokens = encoding.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + max_tokens
        chunk = tokens[start:end]
        chunks.append(encoding.decode(chunk))
        start += max_tokens - overlap

    return chunks
