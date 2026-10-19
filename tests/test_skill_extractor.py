"""Tests for skill_extractor.py"""

from src.skill_extractor import extract_skills, compare_skills, prioritize_missing_skills


def test_extract_skills_finds_known_skills():
    text = "I have experience with Python, React, and SQL databases."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "React" in skills
    assert "SQL" in skills


def test_extract_skills_handles_aliases():
    text = "Experienced in JS, reactjs, and scikit-learn."
    skills = extract_skills(text)
    assert "JavaScript" in skills
    assert "React" in skills
    assert "scikit-learn" in skills


def test_extract_skills_avoids_partial_word_matches():
    # "java" should NOT match inside "javascript"
    text = "I only know javascript, not java."
    skills = extract_skills(text)
    assert "JavaScript" in skills
    assert "Java" in skills  # "java" appears as its own word too ("not java")


def test_extract_skills_no_false_positive_substring():
    text = "javascript expert"
    skills = extract_skills(text)
    assert "JavaScript" in skills
    assert "Java" not in skills  # "java" should not match inside "javascript"


def test_extract_skills_empty_text_returns_empty_set():
    assert extract_skills("") == set()


def test_extract_skills_no_recognizable_skills_returns_empty_set():
    text = "I enjoy hiking, reading novels, and playing the guitar on weekends."
    assert extract_skills(text) == set()


def test_compare_skills_matched_missing_additional():
    resume_skills = {"Python", "SQL", "Excel"}
    jd_skills = {"Python", "SQL", "AWS"}

    result = compare_skills(resume_skills, jd_skills)
    assert result["matched"] == {"Python", "SQL"}
    assert result["missing"] == {"AWS"}
    assert result["additional"] == {"Excel"}


def test_prioritize_missing_skills_counts_mentions():
    jd_text = "We need AWS experience. AWS AWS is critical. Also Docker."
    missing = {"AWS", "Docker"}
    priorities = prioritize_missing_skills(missing, jd_text)

    assert "AWS" in priorities["High"]  # mentioned 3 times
    assert "Docker" in priorities["Low"]  # mentioned once
