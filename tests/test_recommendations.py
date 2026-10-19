"""Tests for recommendations.py"""

from src.recommendations import generate_recommendations


def test_recommendations_include_high_priority_skills():
    skill_priorities = {"High": ["AWS"], "Medium": [], "Low": []}
    completeness_result = {"missing_core_sections": []}
    keyword_result = {"missing_keywords": []}
    bullet_results = {}

    recs = generate_recommendations(
        skill_priorities, completeness_result, keyword_result, bullet_results
    )
    assert any("AWS" in r["issue"] for r in recs)
    # Must never tell the user to just add the skill outright
    aws_rec = next(r for r in recs if "AWS" in r["issue"])
    assert "if you genuinely" in aws_rec["suggestion"].lower()


def test_recommendations_include_missing_core_sections():
    skill_priorities = {"High": [], "Medium": [], "Low": []}
    completeness_result = {"missing_core_sections": ["Skills"]}
    keyword_result = {"missing_keywords": []}
    bullet_results = {}

    recs = generate_recommendations(
        skill_priorities, completeness_result, keyword_result, bullet_results
    )
    assert any("Skills" in r["issue"] for r in recs)


def test_recommendations_no_issues_returns_minimal_list():
    skill_priorities = {"High": [], "Medium": [], "Low": []}
    completeness_result = {"missing_core_sections": []}
    keyword_result = {"missing_keywords": []}
    bullet_results = {}

    recs = generate_recommendations(
        skill_priorities, completeness_result, keyword_result, bullet_results
    )
    assert recs == []


def test_recommendations_every_item_has_required_fields():
    skill_priorities = {"High": ["Docker"], "Medium": [], "Low": []}
    completeness_result = {"missing_core_sections": ["Education"]}
    keyword_result = {"missing_keywords": ["deployment", "scalability"]}
    bullet_results = {
        "Experience": [{
            "text": "Responsible for helping the team",
            "weaknesses": ["a", "b", "c"],
            "suggestion": "Rewrite using an action verb.",
        }]
    }

    recs = generate_recommendations(
        skill_priorities, completeness_result, keyword_result, bullet_results
    )
    assert len(recs) > 0
    for r in recs:
        assert "issue" in r
        assert "why_it_matters" in r
        assert "suggestion" in r
