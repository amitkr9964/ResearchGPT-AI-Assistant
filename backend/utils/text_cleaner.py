"""Text cleaning utilities for document processing."""

import re
import unicodedata


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\x00", "")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    text = text.strip()
    return text


def extract_keywords(text: str, max_keywords: int = 20) -> list[str]:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    stopwords = {
        "that", "this", "with", "from", "have", "been", "were", "their",
        "which", "would", "there", "about", "these", "other", "into",
        "more", "also", "such", "than", "then", "some", "only", "over",
    }
    freq: dict[str, int] = {}
    for word in words:
        if word not in stopwords:
            freq[word] = freq.get(word, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_keywords]]
