"""Tests for preprocessor.py"""

from src.preprocessor import clean_text, preprocess_for_similarity


def test_clean_text_lowercases_and_strips_symbols():
    result = clean_text("Hello, World!!! I know C++ and Node.js")
    assert result == "hello world i know c++ and node.js"


def test_clean_text_handles_empty_string():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_clean_text_collapses_whitespace():
    result = clean_text("too    many\n\nspaces")
    assert result == "too many spaces"


def test_preprocess_for_similarity_removes_stopwords():
    result = preprocess_for_similarity("I am a developer and I love programming")
    # Stopwords like "i", "am", "a", "and" should be removed
    assert "developer" in result
    assert " a " not in f" {result} "
    assert " and " not in f" {result} "


def test_preprocess_for_similarity_lemmatizes():
    result = preprocess_for_similarity("developing developers who developed apps")
    # All forms of "develop" should reduce to the same lemma
    assert "develop" in result


def test_preprocess_empty_input_returns_empty():
    assert preprocess_for_similarity("") == ""
