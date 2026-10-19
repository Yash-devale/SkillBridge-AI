"""
sections_data.py
-----------------
Defines the resume sections we look for, the different heading text that
commonly represents each section, and how much each section "weighs"
toward a resume's completeness score.

Just like skills_data.py, this is alias-based: a section is recognized by
matching a resume heading line against a list of known alternate phrasings
(e.g. "Work Experience", "Professional Experience", and "Employment
History" all mean "Experience").

WEIGHTS below reflect how important each section typically is for a
technical/engineering resume. They are fixed and disclosed to the user -
not learned from data - so the completeness score stays explainable.
Weights sum to 1.0.
"""

SECTION_ALIASES = {
    "Summary": ["summary", "objective", "professional summary",
                "career objective", "profile", "about me"],
    "Education": ["education", "academic background",
                  "academic qualifications", "educational qualifications"],
    "Skills": ["skills", "technical skills", "core competencies",
               "skill set", "key skills"],
    "Projects": ["projects", "academic projects", "personal projects",
                 "key projects"],
    "Experience": ["experience", "work experience",
                   "professional experience", "employment history",
                   "work history"],
    "Internships": ["internship", "internships", "internship experience"],
    "Certifications": ["certifications", "certificates", "licenses",
                        "certifications & courses"],
    "Achievements": ["achievements", "awards", "honors", "honours",
                      "accomplishments", "awards & achievements"],
}

# How much each section contributes to the completeness score.
# A student resume isn't expected to have every section (e.g. not everyone
# has certifications), so these weights are deliberately uneven: core
# sections (Skills, Experience, Education, Projects) matter more than
# "nice to have" sections.
SECTION_WEIGHTS = {
    "Summary": 0.10,
    "Education": 0.15,
    "Skills": 0.20,
    "Projects": 0.20,
    "Experience": 0.20,
    "Internships": 0.05,
    "Certifications": 0.05,
    "Achievements": 0.05,
}

# Sections we treat as "core" - always recommended even if a resume is
# otherwise unusual (e.g. no certifications is fine, but no Skills or
# Experience/Projects section is a real gap for a technical resume).
CORE_SECTIONS = ["Skills", "Education"]
