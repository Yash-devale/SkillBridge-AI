"""Tests for relevance.py"""

from src.relevance import split_into_entries, analyze_relevance
from src.section_detector import detect_sections


def test_split_into_entries_finds_multiple_projects():
    section_text = """Resume Analyzer
- Built a Python NLP tool using scikit-learn
- Used TF-IDF and cosine similarity

Stock Predictor
- Implemented machine learning models using TensorFlow
"""
    entries = split_into_entries(section_text)
    assert len(entries) == 2
    assert entries[0]["title"] == "Resume Analyzer"
    assert entries[1]["title"] == "Stock Predictor"


def test_split_into_entries_empty_text_returns_empty_list():
    assert split_into_entries("") == []


def test_analyze_relevance_scores_relevant_project_higher():
    resume = """
    Projects
    Python Backend API
    - Developed REST APIs using Flask and Python for a backend service

    Cooking Blog Website
    - Created a static website about recipes using HTML and CSS
    """
    jd_text = "Looking for a Python backend developer with Flask and REST API experience."

    sections = detect_sections(resume)
    result = analyze_relevance(sections, jd_text)

    assert "Projects" in result["section_scores"]
    assert result["most_relevant_entry"] is not None
    # The Python Backend API project should be more relevant than the cooking blog
    assert "Backend" in result["most_relevant_entry"]["title"] or \
           "Python" in result["most_relevant_entry"]["title"]


def test_analyze_relevance_no_relevant_sections_returns_zero():
    resume = "Education\nB.Tech Computer Science"
    sections = detect_sections(resume)
    result = analyze_relevance(sections, "Looking for a Python developer.")
    assert result["overall_relevance"] == 0.0
    assert result["most_relevant_entry"] is None
