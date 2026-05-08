import re

def clean_text(text: str) -> str:
    # Remove excessive whitespace and newlines
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    # Remove non-ascii characters to save tokens, keep common punctuation
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()
