"""
scorer.py
---------
Combines individual signals into one final "Resume-Job Match Score" from
0-100.

IMPORTANT (per project requirements): this is a "Resume-Job Match Score",
NOT a guaranteed ATS (Applicant Tracking System) score. Real ATS systems
are proprietary and vary by company - we make no claim to replicate them.

PHASE 2 SCORING MODEL (current):
This score is a weighted average of FIVE signals:

    1. Skill Match                   - 40%  (% of JD skills found in resume)
    2. Text Similarity               - 25%  (TF-IDF + cosine similarity)
    3. Keyword Coverage              - 15%  (% of JD's frequent keywords found in resume)
    4. Resume Completeness           - 10%  (% of expected resume sections present)
    5. Project/Experience Relevance  - 10%  (similarity of Projects/Experience to JD)

The weights are fixed, disclosed to the user, and sum to 1.0, so the
score is fully transparent and explainable - never a "black box".
Skill Match and Text Similarity carry the most weight because they
most directly reflect whether a candidate can do the job; the remaining
three signals capture resume quality/structure and are weighted lower.
"""

# Weights must sum to 1.0. Shown to the user so the score is transparent.
WEIGHTS = {
    "skill_match": 0.40,
    "semantic_similarity": 0.25,
    "keyword_coverage": 0.15,
    "completeness": 0.10,
    "relevance": 0.10,
}

# Human-readable labels for displaying each component in the UI.
COMPONENT_LABELS = {
    "skill_match": "Skill Match",
    "semantic_similarity": "Text Similarity (TF-IDF)",
    "keyword_coverage": "Keyword Coverage",
    "completeness": "Resume Completeness",
    "relevance": "Project/Experience Relevance",
}


def calculate_skill_match_score(matched_skills: set, jd_skills: set) -> float:
    """
    What % of the skills the job description asks for does the resume
    actually contain?

    Returns a score from 0 to 100. If the job description has no
    recognizable skills at all, we return 0 (we can't claim a match
    against nothing) rather than dividing by zero.
    """
    if not jd_skills:
        return 0.0
    return round((len(matched_skills) / len(jd_skills)) * 100, 2)


def calculate_final_score(component_scores: dict) -> dict:
    """
    Combine all five component scores into one final weighted score.

    Parameters
    ----------
    component_scores : dict
        Must contain all keys in WEIGHTS, each mapped to a raw score on a
        0-100 scale, e.g.:
        {
            "skill_match": 80.0,
            "semantic_similarity": 45.5,   # already converted to 0-100
            "keyword_coverage": 60.0,
            "completeness": 75.0,
            "relevance": 50.0,
        }

    Returns
    -------
    dict
        {
            "final_score": float (0-100, rounded),
            "breakdown": {
                "skill_match": {"raw": ..., "weight": ..., "contribution": ..., "label": ...},
                ...
            }
        }
        The "breakdown" lets the UI show exactly how the final number was
        produced - this is what makes the score "explainable".
    """
    missing_keys = set(WEIGHTS) - set(component_scores)
    if missing_keys:
        raise ValueError(
            f"calculate_final_score is missing required component(s): {missing_keys}"
        )

    breakdown = {}
    total = 0.0
    for component, weight in WEIGHTS.items():
        raw = float(component_scores[component])
        raw = max(0.0, min(100.0, raw))  # guard against out-of-range inputs
        contribution = round(raw * weight, 2)
        total += contribution
        breakdown[component] = {
            "raw": round(raw, 2),
            "weight": weight,
            "contribution": contribution,
            "label": COMPONENT_LABELS[component],
        }

    final_score = round(max(0.0, min(100.0, total)), 2)

    return {"final_score": final_score, "breakdown": breakdown}


def get_score_label(final_score: float) -> str:
    """
    Translate a numeric score into a human-friendly label. Thresholds are
    simple, fixed, and disclosed - not learned from data - so they stay
    easy to explain.
    """
    if final_score >= 75:
        return "Strong Match"
    elif final_score >= 50:
        return "Moderate Match"
    elif final_score >= 25:
        return "Weak Match"
    else:
        return "Low Match"
