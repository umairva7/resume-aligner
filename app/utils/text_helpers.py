import re

def clean_extracted_text(text: str) -> str:
    """Clean extra whitespaces, weird symbols, and normalize lines."""
    if not text:
        return ""
    # Normalize multiple whitespace lines
    cleaned = re.sub(r'\n\s*\n', '\n\n', text)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    return cleaned.strip()

def truncate_text(text: str, max_chars: int = 10000) -> str:
    """Safely truncate text if it exceeds maximum context limits."""
    return text[:max_chars] if len(text) > max_chars else text
