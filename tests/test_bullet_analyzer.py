"""Tests for bullet_analyzer.py"""

from src.bullet_analyzer import (
    extract_bullets,
    analyze_bullet,
    analyze_section_bullets,
)


def test_extract_bullets_finds_dash_bullets():
    section_text = """
    - Developed REST APIs using Flask
    - Built data pipelines using Pandas
    Not a bullet line
    """
    bullets = extract_bullets(section_text)
    assert len(bullets) == 2
    assert "Developed REST APIs using Flask" in bullets


def test_extract_bullets_empty_text_returns_empty_list():
    assert extract_bullets("") == []


def test_analyze_bullet_strong_bullet_detects_all_positives():
    bullet = "Developed a REST API using Python and Flask, reducing response time by 30%"
    result = analyze_bullet(bullet)
    assert result["has_strong_verb"] is True
    assert result["has_technology"] is True
    assert result["has_quantified_result"] is True
    assert result["has_weak_phrase"] is False
    assert len(result["weaknesses"]) == 0


def test_analyze_bullet_weak_bullet_detects_weaknesses():
    bullet = "Responsible for helping the team with various tasks"
    result = analyze_bullet(bullet)
    assert result["has_strong_verb"] is False
    assert result["has_weak_phrase"] is True
    assert result["has_technology"] is False
    assert result["has_quantified_result"] is False
    assert len(result["weaknesses"]) > 0


def test_analyze_bullet_never_fabricates_missing_data():
    bullet = "Worked on some backend features"
    result = analyze_bullet(bullet)
    # Suggestion should not contain any invented number or fake percentage
    assert "%" not in result["suggestion"]
    assert "fabricate" in result["suggestion"] or "factually true" in result["suggestion"]


def test_analyze_section_bullets_returns_list_of_analyses():
    section = """
    - Developed internal dashboard using React and Python
    - Worked on miscellaneous tasks
    """
    results = analyze_section_bullets(section)
    assert len(results) == 2
    assert all("suggestion" in r for r in results)
