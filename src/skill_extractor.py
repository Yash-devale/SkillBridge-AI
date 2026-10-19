"""
skill_extractor.py
-------------------
Finds which known technical skills appear in a piece of text (resume or
job description), and compares two skill sets to find matches/gaps.

Approach: alias-based regex matching.
- We already built a lookup of alias -> canonical skill name (skills_data.py)
- For each alias, we search the raw text using a regex with WORD BOUNDARIES
  so that "java" doesn't accidentally match inside "javascript".
- Special characters like '+', '#', '.' are escaped in the regex since
  they have special meaning in regex syntax.

This is intentionally simple (no ML model) so it's 100% explainable and
never "fabricates" a skill: a skill is only reported if its exact text
(or a known alias) is genuinely present in the document.
"""

import re
from .skills_data import build_alias_lookup, SKILL_ALIASES

# Built once at import time - rebuilding this dict on every extract_skills()
# call would be wasteful since bullet_analyzer.py and relevance.py call it
# once per bullet/project entry.
_ALIAS_LOOKUP = build_alias_lookup()


def _build_alias_pattern(alias: str) -> re.Pattern:
    """
    Build a compiled regex pattern that matches an alias as a whole word/
    phrase, case-insensitively.

    We escape the alias first (so symbols like '+', '#', '.' are treated
    literally, not as regex operators), then wrap it with word-boundary
    markers. Word boundaries (\\b) don't work perfectly around symbols like
    '+' or '#', so for aliases containing such symbols we instead require
    that they aren't immediately preceded/followed by a letter or digit.
    """
    escaped = re.escape(alias)
    pattern = r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])"
    return re.compile(pattern, re.IGNORECASE)


def extract_skills(text: str) -> set:
    """
    Scan `text` for any known skill aliases and return the set of
    canonical skill names found.

    Parameters
    ----------
    text : str
        Raw or lightly-cleaned text (resume or job description).

    Returns
    -------
    set of str
        Canonical skill names detected, e.g. {"Python", "React", "SQL"}.
    """
    if not text:
        return set()

    text_lower = text.lower()
    found_skills = set()

    for alias, canonical in _ALIAS_LOOKUP.items():
        pattern = _build_alias_pattern(alias)
        if pattern.search(text_lower):
            found_skills.add(canonical)

    return found_skills


def compare_skills(resume_skills: set, jd_skills: set) -> dict:
    """
    Compare the skills found in a resume against the skills required by a
    job description.

    Returns a dictionary with three sets:
    - "matched":  skills present in BOTH resume and job description
    - "missing":  skills the job description asks for but the resume lacks
    - "additional": skills the resume has that the job description didn't ask for
    """
    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    additional = resume_skills - jd_skills

    return {
        "matched": matched,
        "missing": missing,
        "additional": additional,
    }


def prioritize_missing_skills(missing_skills: set, jd_text: str) -> dict:
    """
    Assign a priority (High / Medium / Low) to each missing skill, based on
    how many times it's mentioned in the job description. The idea:
    a skill mentioned repeatedly (e.g. in both "Requirements" and
    "Responsibilities") is probably more important to the employer than
    one mentioned only once, in passing.

    Rules (simple and explainable):
    - Mentioned 3+ times  -> High priority
    - Mentioned 2 times   -> Medium priority
    - Mentioned 1 time    -> Low priority

    Returns
    -------
    dict: {"High": [...], "Medium": [...], "Low": [...]}
    """
    priorities = {"High": [], "Medium": [], "Low": []}
    jd_lower = jd_text.lower()

    for skill in missing_skills:
        aliases = set(SKILL_ALIASES.get(skill, [])) | {skill.lower()}
        mention_count = 0
        for alias in aliases:
            pattern = _build_alias_pattern(alias)
            mention_count += len(pattern.findall(jd_lower))

        if mention_count >= 3:
            priorities["High"].append(skill)
        elif mention_count == 2:
            priorities["Medium"].append(skill)
        else:
            priorities["Low"].append(skill)

    # Sort each priority list alphabetically for clean, stable display
    for level in priorities:
        priorities[level] = sorted(priorities[level])

    return priorities
