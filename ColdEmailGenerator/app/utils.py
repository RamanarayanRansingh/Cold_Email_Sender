import re

def clean_text(text: str) -> str:
    """Clean up raw text."""
    # Add your text-cleaning logic (e.g., removing unnecessary line breaks, HTML tags, etc.)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_emails(text: str):
    """Extract email addresses from text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)
