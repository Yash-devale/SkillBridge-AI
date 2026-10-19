"""
recommendations.py
-------------------
Generates actionable, honest recommendations based ONLY on the analysis
already performed by the other modules (skill_extractor, completeness,
keyword_analyzer, bullet_analyzer). This module does not run any new
analysis of its own - it just turns existing findings into structured,
readable advice.

Every recommendation follows the same transparent structure:
    Issue:                 what the analysis found
    Why it matters:        why this could affect the match
    Suggested improvement: a concrete, honest next step

CRITICAL: recommendations never suggest adding a skill or achievement the
candidate doesn't actually have. Suggestions about missing skills always
include a conditional ("if you genuinely have this skill...").
"""


def _skill_priority_recommendations(missing_skills_by_priority: dict) -> list:
    """One recommendation per HIGH priority missing skill (capped), since
    those are the gaps most likely to hurt the match."""
    recs = []
    high_priority = missing_skills_by_priority.get("High", [])
    for skill in high_priority[:5]:  # cap to avoid overwhelming the user
        recs.append({
            "issue": f'"{skill}" is heavily emphasized in the job description '
                     f"but wasn't detected in your resume.",
            "why_it_matters": f'"{skill}" appears to be a key requirement for this role '
                               f"(mentioned multiple times in the job description).",
            "suggestion": f"If you genuinely have experience with {skill}, make sure it's "
                          f"clearly listed in your Skills section and demonstrated in a "
                          f"project or work experience bullet. Never add a skill you don't "
                          f"actually have.",
        })
    return recs


def _completeness_recommendations(completeness_result: dict) -> list:
    """One recommendation for each missing core section."""
    recs = []
    for section in completeness_result.get("missing_core_sections", []):
        recs.append({
            "issue": f'No "{section}" section was detected in your resume.',
            "why_it_matters": f"A {section} section is considered a core part of a "
                               f"technical resume and its absence can make your resume "
                               f"look incomplete to a recruiter or ATS.",
            "suggestion": f"Add a clearly labeled \"{section}\" section with a "
                          f"standard heading so it's easy to detect and read.",
        })
    return recs


def _keyword_recommendations(keyword_result: dict, max_items: int = 5) -> list:
    """One combined recommendation about missing JD keywords/terminology."""
    missing = keyword_result.get("missing_keywords", [])
    if not missing:
        return []
    sample = missing[:max_items]
    return [{
        "issue": f"Your resume doesn't use {len(missing)} important term(s) that "
                 f"appear frequently in the job description, including: "
                 f"{', '.join(sample)}.",
        "why_it_matters": "Job descriptions often repeat the terminology they most "
                           "care about. Using similar language (where accurate) can "
                           "make your resume's relevance clearer to both recruiters "
                           "and automated screening tools.",
        "suggestion": "Review these terms and, where they honestly describe your "
                      "experience, incorporate the same wording naturally into your "
                      "resume. Don't force in terms that don't reflect real experience.",
    }]


def _bullet_recommendations(bullet_results: dict, max_items: int = 3) -> list:
    """Recommendations for the weakest bullets found."""
    recs = []
    count = 0
    for section_name, bullets in bullet_results.items():
        for b in bullets:
            if count >= max_items:
                break
            if len(b["weaknesses"]) >= 2:  # only flag noticeably weak bullets
                recs.append({
                    "issue": f'A bullet in your {section_name} section reads: '
                             f'"{b["text"][:100]}{"..." if len(b["text"]) > 100 else ""}"',
                    "why_it_matters": "Bullets that lack a strong action verb, a "
                                       "specific technology, or a measurable result "
                                       "are less impactful and harder for a reader to "
                                       "quickly evaluate.",
                    "suggestion": b["suggestion"],
                })
                count += 1
        if count >= max_items:
            break
    return recs


def generate_recommendations(skill_priorities: dict, completeness_result: dict,
                              keyword_result: dict, bullet_results: dict) -> list:
    """
    Combine findings from every analysis module into a single, ordered
    list of recommendations (skills first, then structure, then keywords,
    then bullet quality - roughly in order of typical impact).
    """
    recommendations = []
    recommendations.extend(_skill_priority_recommendations(skill_priorities))
    recommendations.extend(_completeness_recommendations(completeness_result))
    recommendations.extend(_keyword_recommendations(keyword_result))
    recommendations.extend(_bullet_recommendations(bullet_results))
    return recommendations
