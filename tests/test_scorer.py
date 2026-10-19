"""Tests for scorer.py (Phase 2: 5-component weighted score)"""

import pytest
from src.scorer import (
    calculate_skill_match_score,
    calculate_final_score,
    get_score_label,
    WEIGHTS,
)


def test_calculate_skill_match_score_full_match():
    matched = {"Python", "SQL"}
    jd_skills = {"Python", "SQL"}
    assert calculate_skill_match_score(matched, jd_skills) == 100.0


def test_calculate_skill_match_score_partial_match():
    matched = {"Python"}
    jd_skills = {"Python", "SQL", "AWS", "Docker"}
    assert calculate_skill_match_score(matched, jd_skills) == 25.0


def test_calculate_skill_match_score_no_jd_skills():
    assert calculate_skill_match_score(set(), set()) == 0.0


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_calculate_final_score_all_components_full_marks():
    components = {
        "skill_match": 100.0,
        "semantic_similarity": 100.0,
        "keyword_coverage": 100.0,
        "completeness": 100.0,
        "relevance": 100.0,
    }
    result = calculate_final_score(components)
    assert result["final_score"] == 100.0


def test_calculate_final_score_all_zero():
    components = {
        "skill_match": 0.0,
        "semantic_similarity": 0.0,
        "keyword_coverage": 0.0,
        "completeness": 0.0,
        "relevance": 0.0,
    }
    result = calculate_final_score(components)
    assert result["final_score"] == 0.0


def test_calculate_final_score_breakdown_sums_to_final():
    components = {
        "skill_match": 80.0,
        "semantic_similarity": 40.0,
        "keyword_coverage": 60.0,
        "completeness": 75.0,
        "relevance": 50.0,
    }
    result = calculate_final_score(components)
    breakdown_total = round(
        sum(c["contribution"] for c in result["breakdown"].values()), 2
    )
    assert result["final_score"] == breakdown_total


def test_calculate_final_score_contribution_matches_weight():
    components = {
        "skill_match": 100.0,
        "semantic_similarity": 0.0,
        "keyword_coverage": 0.0,
        "completeness": 0.0,
        "relevance": 0.0,
    }
    result = calculate_final_score(components)
    # skill_match weight is 40%, so 100 * 0.40 = 40
    assert result["breakdown"]["skill_match"]["contribution"] == 40.0
    assert result["final_score"] == 40.0


def test_calculate_final_score_missing_component_raises():
    incomplete_components = {
        "skill_match": 80.0,
        "semantic_similarity": 40.0,
        # missing keyword_coverage, completeness, relevance
    }
    with pytest.raises(ValueError):
        calculate_final_score(incomplete_components)


def test_calculate_final_score_clamps_out_of_range_values():
    components = {
        "skill_match": 150.0,   # out of range, should clamp to 100
        "semantic_similarity": -20.0,  # out of range, should clamp to 0
        "keyword_coverage": 50.0,
        "completeness": 50.0,
        "relevance": 50.0,
    }
    result = calculate_final_score(components)
    assert result["breakdown"]["skill_match"]["raw"] == 100.0
    assert result["breakdown"]["semantic_similarity"]["raw"] == 0.0


def test_get_score_label_thresholds():
    assert get_score_label(90) == "Strong Match"
    assert get_score_label(60) == "Moderate Match"
    assert get_score_label(30) == "Weak Match"
    assert get_score_label(10) == "Low Match"
