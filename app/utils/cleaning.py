import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove NULL bytes
    text = text.replace("\x00", "")

    # Remove all control characters except tab and newline
    text = re.sub(r"[\x00-\x09\x0B-\x1F\x7F]", "", text)

    # Normalize weird Unicode escapes
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")

    return text
