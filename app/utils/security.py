from fastapi import HTTPException, Header

API_TOKEN = "SUPER_SECRET_CLE_API"

async def verify_token(Authorization: str = Header(None)):
    if Authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Token invalide")
    return True
