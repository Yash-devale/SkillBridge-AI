"""Explainable skill evidence and learning-roadmap utilities.

Recommendations are based on an explicit, editable prerequisite map. They are
not claims about a candidate's proficiency or course completion.
"""
from __future__ import annotations

import re
from .skills_data import SKILL_ALIASES

# Small, transparent prerequisite map. Extend it as the supported skill set grows.
PREREQUISITES = {
    "Machine Learning": ["Python", "Statistics", "Data Analysis"],
    "Deep Learning": ["Python", "Machine Learning"],
    "Natural Language Processing": ["Python", "Machine Learning"],
    "TensorFlow": ["Python", "Machine Learning"],
    "PyTorch": ["Python", "Machine Learning"],
    "scikit-learn": ["Python", "Statistics"],
    "Data Analysis": ["Python", "Statistics"],
    "Data Visualization": ["Data Analysis"],
    "Docker": ["Linux"],
    "Kubernetes": ["Docker"],
    "FastAPI": ["Python", "REST API"],
    "Django": ["Python"],
    "Flask": ["Python"],
    "React": ["JavaScript", "HTML", "CSS"],
    "Node.js": ["JavaScript"],
    "AWS": ["Linux", "Docker"],
    "CI/CD": ["Git"],
}

# Related technologies are suggestions for exploration, not inferred equivalence.
RELATED_SKILLS = {
    "Machine Learning": ["Deep Learning", "scikit-learn", "Statistics"],
    "Natural Language Processing": ["Machine Learning", "spaCy", "NLTK"],
    "PyTorch": ["TensorFlow", "Deep Learning"],
    "TensorFlow": ["PyTorch", "Deep Learning"],
    "SQL": ["PostgreSQL", "MySQL"],
    "Docker": ["Kubernetes", "CI/CD"],
    "AWS": ["Azure", "Google Cloud Platform"],
    "React": ["JavaScript", "TypeScript"],
    "Data Analysis": ["Pandas", "Data Visualization"],
}


def _aliases(skill: str) -> list[str]:
    return sorted(set([skill, *SKILL_ALIASES.get(skill, [])]), key=len, reverse=True)


def find_skill_evidence(text: str, skills) -> dict[str, str]:
    """Return the first short source sentence that literally supports each skill."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?\n])\s+", text or "") if s.strip()]
    evidence = {}
    for skill in sorted(skills):
        patterns = [re.compile(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", re.I)
                    for a in _aliases(skill)]
        for sentence in sentences:
            if any(p.search(sentence) for p in patterns):
                evidence[skill] = sentence[:280]
                break
    return evidence


def build_learning_roadmap(missing_skills, resume_skills, jd_text: str, priorities: dict) -> list[dict]:
    """Order missing skills by JD priority and known prerequisite relationships."""
    missing = set(missing_skills)
    priority_rank = {skill: rank for rank, level in enumerate(("High", "Medium", "Low"))
                     for skill in priorities.get(level, [])}
    # If a prerequisite is also missing, place it before the dependent skill.
    def depth(skill, seen=None):
        seen = set() if seen is None else seen
        if skill in seen:
            return 0
        seen.add(skill)
        prereqs = [p for p in PREREQUISITES.get(skill, []) if p in missing]
        return 1 + max((depth(p, seen.copy()) for p in prereqs), default=0)

    ordered = sorted(missing, key=lambda s: (depth(s), priority_rank.get(s, 2), s.lower()))
    roadmap = []
    for skill in ordered:
        prereqs = PREREQUISITES.get(skill, [])
        unmet = [p for p in prereqs if p not in resume_skills and p in missing]
        mentions = sum(len(re.findall(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", jd_text, re.I))
                       for a in _aliases(skill))
        roadmap.append({
            "skill": skill,
            "priority": next((level for level in ("High", "Medium", "Low")
                               if skill in priorities.get(level, [])), "Low"),
            "prerequisites": prereqs,
            "learn_first": unmet,
            "reason": f"Appears {mentions} time(s) in the target description and was not detected in the resume text.",
            "related_skills": [s for s in RELATED_SKILLS.get(skill, []) if s not in missing][:3],
        })
    return roadmap
