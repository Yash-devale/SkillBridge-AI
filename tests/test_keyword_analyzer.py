"""Tests for keyword_analyzer.py"""

from src.keyword_analyzer import extract_keywords, calculate_keyword_coverage


def test_extract_keywords_returns_nouns():
    text = "We need a backend developer with strong database and deployment experience."
    keywords = extract_keywords(text, top_n=10)
    keyword_words = [k for k, _count in keywords]
    assert "developer" in keyword_words or "backend" in keyword_words
    assert len(keywords) > 0


def test_extract_keywords_empty_text_returns_empty_list():
    assert extract_keywords("") == []


def test_extract_keywords_frequency_ordering():
    text = "database database database server server api"
    keywords = extract_keywords(text, top_n=5)
    # "database" appears most frequently, should be first
    assert keywords[0][0] == "database"
    assert keywords[0][1] == 3


def test_extract_keywords_filters_jd_boilerplate():
    text = (
        "Job Title: Backend Developer. Requirements: strong understanding "
        "of database systems and API design. Team player with proficiency "
        "in Python and deployment pipelines."
    )
    keywords = extract_keywords(text, top_n=25)
    keyword_words = [k for k, _count in keywords]
    # Boilerplate scaffolding words should be filtered out
    assert "title" not in keyword_words
    assert "requirement" not in keyword_words
    assert "understanding" not in keyword_words
    assert "team" not in keyword_words
    assert "proficiency" not in keyword_words
    # Genuine domain terms should remain
    assert "database" in keyword_words


def test_extract_keywords_data_lemma_override():
    text = "We work with large amounts of data. Data analysis is core to this role."
    keywords = extract_keywords(text, top_n=10)
    keyword_words = [k for k, _count in keywords]
    assert "data" in keyword_words
    assert "datum" not in keyword_words


def test_keyword_coverage_full_overlap():
    jd = "database server api"
    resume = "I have experience with database server api systems."
    result = calculate_keyword_coverage(resume, jd)
    assert result["coverage_percentage"] == 100.0
    assert result["missing_keywords"] == []


def test_keyword_coverage_partial_overlap():
    jd = "database server deployment"
    resume = "I have experience with database systems."
    result = calculate_keyword_coverage(resume, jd)
    assert 0 < result["coverage_percentage"] < 100
    assert "database" in result["found_keywords"]


def test_keyword_coverage_no_jd_keywords_returns_zero():
    result = calculate_keyword_coverage("some resume text", "")
    assert result["coverage_percentage"] == 0.0
    assert result["total_keywords_checked"] == 0
