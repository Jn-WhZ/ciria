import re
import unicodedata

def sanitize_filename(filename: str) -> str:
    # Normalize unicode → ascii
    filename = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode()

    # Replace apostrophes, quotes, punctuation
    filename = re.sub(r"[^\w\s.-]", "", filename)

    # Replace spaces by underscores
    filename = filename.replace(" ", "_")

    # Lowercase
    filename = filename.lower()

    return filename
