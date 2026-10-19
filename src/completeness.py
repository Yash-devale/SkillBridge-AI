"""
completeness.py
----------------
Turns the output of section_detector.py into a "Resume Completeness"
score: what % of the expected resume structure is actually present.

The score is a weighted sum (see sections_data.SECTION_WEIGHTS), not a
simple count, because some sections (Skills, Experience) matter more for
a technical resume than others (Certifications, Achievements). A resume
missing "Certifications" isn't penalized much; one missing "Skills" is.
"""

from .sections_data import SECTION_WEIGHTS, CORE_SECTIONS


def calculate_completeness(detected_sections: dict) -> dict:
    """
    Parameters
    ----------
    detected_sections : dict
        Output of section_detector.detect_sections()

    Returns
    -------
    dict: {
        "percentage": float (0-100),
        "present_sections": [names...],
        "missing_sections": [names...],
        "missing_core_sections": [names...],  # subset of missing that are important
    }
    """
    present_sections = []
    missing_sections = []
    score = 0.0

    for section_name, weight in SECTION_WEIGHTS.items():
        info = detected_sections.get(section_name, {"present": False})
        if info["present"]:
            present_sections.append(section_name)
            score += weight
        else:
            missing_sections.append(section_name)

    missing_core_sections = [s for s in missing_sections if s in CORE_SECTIONS]

    return {
        "percentage": round(score * 100, 2),
        "present_sections": present_sections,
        "missing_sections": missing_sections,
        "missing_core_sections": missing_core_sections,
    }
