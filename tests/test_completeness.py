"""Tests for completeness.py"""

from src.completeness import calculate_completeness
from src.section_detector import detect_sections


def test_full_resume_scores_100_percent():
    resume = """
    Summary
    A passionate developer.

    Education
    B.Tech Computer Science

    Skills
    Python, SQL

    Projects
    Built a chatbot.

    Experience
    Software Intern.

    Internships
    Data Science Internship.

    Certifications
    AWS Certified.

    Achievements
    Hackathon winner.
    """
    sections = detect_sections(resume)
    result = calculate_completeness(sections)
    assert result["percentage"] == 100.0
    assert result["missing_sections"] == []


def test_empty_resume_scores_zero_percent():
    sections = detect_sections("")
    result = calculate_completeness(sections)
    assert result["percentage"] == 0.0
    assert len(result["missing_sections"]) == 8


def test_partial_resume_scores_partial_percentage():
    resume = """
    Skills
    Python, Java

    Education
    B.Tech
    """
    sections = detect_sections(resume)
    result = calculate_completeness(sections)
    # Skills (0.20) + Education (0.15) = 35%
    assert result["percentage"] == 35.0
    assert "Skills" in result["present_sections"]
    assert "Education" in result["present_sections"]
    assert "Projects" in result["missing_sections"]


def test_missing_core_sections_flagged():
    resume = """
    Achievements
    Won a hackathon.
    """
    sections = detect_sections(resume)
    result = calculate_completeness(sections)
    assert "Skills" in result["missing_core_sections"]
    assert "Education" in result["missing_core_sections"]


def test_completeness_handles_whitespace_only_resume():
    sections = detect_sections("     \n\n   \t  ")
    result = calculate_completeness(sections)
    assert result["percentage"] == 0.0
