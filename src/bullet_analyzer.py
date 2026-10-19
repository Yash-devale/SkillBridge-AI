"""
bullet_analyzer.py
-------------------
Analyzes individual resume bullet points (from Experience, Internships,
and Projects sections) for writing quality - specifically, whether a
bullet demonstrates the "Action + Task + Technology + Result" pattern
that's widely recommended for technical resumes.

This module NEVER invents or edits factual content. It only detects
patterns that are already present in the text (a strong action verb, a
mentioned technology, a number/percentage) and gives feedback based on
what it actually finds - it never adds achievements, numbers, or skills
that aren't already written by the candidate.
"""

import re
from .skill_extractor import extract_skills

STRONG_ACTION_VERBS = [
    "developed", "built", "implemented", "designed", "automated",
    "optimized", "analyzed", "integrated", "improved", "created",
    "engineered", "architected", "deployed", "launched", "led",
    "managed", "reduced", "increased", "streamlined", "refactored",
]

WEAK_PHRASES = [
    "worked on", "responsible for", "helped with", "assisted with",
    "involved in", "participated in", "tasked with",
]

# A quantified result: a number, percentage, or common metric-style phrase
_NUMBER_PATTERN = re.compile(r"\b\d+(\.\d+)?\s*%?|\b\d+x\b", re.IGNORECASE)

_BULLET_PREFIX = re.compile(r"^\s*[-•*▪‣]\s*")


def extract_bullets(section_text: str) -> list:
    """Pull out individual bullet lines (lines starting with -, •, *, etc.)."""
    if not section_text:
        return []
    bullets = []
    for line in section_text.split("\n"):
        if _BULLET_PREFIX.match(line):
            cleaned = _BULLET_PREFIX.sub("", line).strip()
            if cleaned:
                bullets.append(cleaned)
    return bullets


def analyze_bullet(bullet: str) -> dict:
    """
    Analyze a single bullet point.

    Returns
    -------
    dict: {
        "text": original bullet text,
        "has_strong_verb": bool,
        "has_weak_phrase": bool,
        "has_technology": bool,
        "has_quantified_result": bool,
        "strengths": [str, ...],
        "weaknesses": [str, ...],
        "suggestion": str,
    }
    """
    bullet_lower = bullet.lower().strip()

    first_word = bullet_lower.split(" ")[0].strip(".,") if bullet_lower else ""
    has_strong_verb = first_word in STRONG_ACTION_VERBS

    has_weak_phrase = any(phrase in bullet_lower for phrase in WEAK_PHRASES)
    has_technology = len(extract_skills(bullet)) > 0
    has_quantified_result = bool(_NUMBER_PATTERN.search(bullet))

    strengths = []
    weaknesses = []

    if has_strong_verb:
        strengths.append(f"Starts with a strong action verb (\"{first_word}\").")
    if has_technology:
        strengths.append("Mentions a specific technology/tool.")
    if has_quantified_result:
        strengths.append("Includes a quantified result or metric.")

    if not has_strong_verb:
        weaknesses.append("Doesn't start with a strong action verb.")
    if has_weak_phrase:
        weaknesses.append(
            "Uses a passive/weak phrase (e.g. \"worked on\", \"responsible for\")."
        )
    if not has_technology:
        weaknesses.append("Doesn't mention a specific technology or tool.")
    if not has_quantified_result:
        weaknesses.append("Has no quantified result (a number, %, or measurable outcome).")

    # Build a suggestion from only what's actually missing - never invent
    # a metric or technology on the candidate's behalf.
    if not weaknesses:
        suggestion = "Strong bullet - follows the Action + Task + Technology + Result pattern well."
    else:
        missing_parts = []
        if not has_strong_verb:
            missing_parts.append("a strong action verb at the start")
        if not has_technology:
            missing_parts.append("the specific technology/tool used")
        if not has_quantified_result:
            missing_parts.append("a real, measurable result (if one exists)")
        suggestion = (
            "Consider rewriting this bullet to include " + ", ".join(missing_parts) +
            ". Only add details that are factually true - never fabricate numbers or tools."
        )

    return {
        "text": bullet,
        "has_strong_verb": has_strong_verb,
        "has_weak_phrase": has_weak_phrase,
        "has_technology": has_technology,
        "has_quantified_result": has_quantified_result,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestion": suggestion,
    }


def analyze_section_bullets(section_text: str) -> list:
    """Extract and analyze every bullet in a section's text."""
    bullets = extract_bullets(section_text)
    return [analyze_bullet(b) for b in bullets]


def analyze_all_bullets(detected_sections: dict) -> dict:
    """
    Run bullet analysis across all bullet-bearing sections
    (Experience, Internships, Projects).

    Returns
    -------
    dict: {"Experience": [analyzed_bullet, ...], "Projects": [...], ...}
    Only includes sections that are present and contain at least one bullet.
    """
    results = {}
    for section_name in ["Experience", "Internships", "Projects"]:
        info = detected_sections.get(section_name, {"present": False, "content": ""})
        if info["present"]:
            analyzed = analyze_section_bullets(info["content"])
            if analyzed:
                results[section_name] = analyzed
    return results
