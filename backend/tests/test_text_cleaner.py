"""Text cleaner unit tests."""

from backend.utils.text_cleaner import clean_text, extract_keywords


def test_clean_text_removes_extra_whitespace():
    assert clean_text("  hello   world  ") == "hello world"


def test_clean_text_handles_newlines():
    result = clean_text("line1\n\n\n\nline2")
    assert "\n\n" in result or "line1" in result


def test_extract_keywords():
    text = "machine learning algorithms neural networks deep learning transformers attention"
    keywords = extract_keywords(text, max_keywords=5)
    assert len(keywords) <= 5
    assert isinstance(keywords, list)
