"""Tests for matcher.py (TF-IDF + cosine similarity)"""

from src.matcher import compute_similarity


def test_identical_documents_have_high_similarity():
    text = "python developer with machine learning experience"
    score = compute_similarity(text, text)
    assert score > 0.99  # identical text -> similarity ~1.0


def test_completely_different_documents_have_low_similarity():
    resume = "python developer machine learning data science"
    jd = "chef cooking recipe kitchen restaurant"
    score = compute_similarity(resume, jd)
    assert score < 0.3


def test_similarity_score_within_bounds():
    resume = "python developer web application backend"
    jd = "looking for python backend developer"
    score = compute_similarity(resume, jd)
    assert 0.0 <= score <= 1.0


def test_empty_text_returns_zero():
    assert compute_similarity("", "python developer") == 0.0
    assert compute_similarity("python developer", "") == 0.0
    assert compute_similarity("", "") == 0.0
