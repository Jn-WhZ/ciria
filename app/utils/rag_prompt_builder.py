def build_rag_prompt(question: str, chunks: list):
    """
    Construct a structured prompt with retrieved chunks.
    """

    context = ""

    for idx, chunk in enumerate(chunks):
        context += f"\n\n[EXTRAIT {idx+1} — source: {chunk['filename']}]\n{chunk['chunk_text']}\n"

    prompt = f"""
Tu es un expert CIR/CII/DGFIP.

Réponds STRICTEMENT en t'appuyant uniquement sur les extraits suivants :

{context}

QUESTION :
{question}

CONTRAINTES :
- Aucune invention.
- Pas d'informations hors des extraits ci-dessus.
- Présente une réponse structurée et synthétique.
- Mentionne clairement les limites et verrous décrits dans les extraits.
- Si l'information n'existe pas dans le CONTEXT, répond "L'information n'est pas présente dans les documents fournis."
"""

    return prompt.strip()
