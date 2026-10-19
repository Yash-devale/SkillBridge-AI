"""
relevance.py
-------------
Measures how relevant a resume's Projects, Experience, and Internships
sections are to a specific job description, using the same TF-IDF +
cosine similarity approach as matcher.py (kept consistent so the whole
app uses one explainable similarity method throughout).

We also split the Projects section into individual project "entries" so
we can tell the user *which specific project* is most relevant to the
job - this is more actionable than a single relevance number for the
whole section.
"""

import re
from .preprocessor import preprocess_for_similarity
from .matcher import compute_similarity

RELEVANT_SECTIONS = ["Projects", "Experience", "Internships"]

# A line that looks like a new project/experience title: short and
# doesn't start with a bullet character.
_BULLET_PREFIX = re.compile(r"^\s*[-•*▪‣]\s*")


def split_into_entries(section_text: str) -> list:
    """
    Heuristically split a section's text (e.g. the Projects section) into
    separate entries/projects.

    Rule of thumb: a line that is NOT a bullet point and is reasonably
    short is treated as a new entry's title (e.g. "Resume Analyzer -
    Python NLP Tool"). Bullet lines that follow belong to that entry,
    until the next title line appears.

    This is a simple heuristic, not a perfect parser - resumes vary a lot
    in formatting. It's intentionally simple so it stays easy to explain.
    """
    lines = [ln for ln in section_text.split("\n") if ln.strip()]
    if not lines:
        return []

    entries = []
    current_title = None
    current_lines = []

    for line in lines:
        is_bullet = bool(_BULLET_PREFIX.match(line))
        is_title_like = (not is_bullet) and len(line.strip()) <= 90

        if is_title_like:
            # Save the previous entry before starting a new one
            if current_title is not None or current_lines:
                entries.append({
                    "title": current_title or "Entry",
                    "text": "\n".join(current_lines).strip(),
                })
            current_title = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save the last entry
    if current_title is not None or current_lines:
        entries.append({
            "title": current_title or "Entry",
            "text": "\n".join(current_lines).strip(),
        })

    # Merge title into the text so short entries still have something to
    # compare against the JD (titles often contain the most relevant tech).
    for entry in entries:
        entry["full_text"] = f"{entry['title']}. {entry['text']}".strip()

    return entries


def analyze_relevance(detected_sections: dict, jd_text: str) -> dict:
    """
    Compute relevance scores for each resume section that describes
    real-world work (Projects, Experience, Internships), plus an overall
    "Project/Experience Relevance" score used in final scoring.

    Returns
    -------
    dict: {
        "section_scores": {"Projects": 62.3, "Experience": 40.1, ...},
        "overall_relevance": float (0-100, average of present sections),
        "most_relevant_entry": {"section": "Projects", "title": "...", "score": 78.2} or None,
    }
    """
    jd_processed = preprocess_for_similarity(jd_text)

    section_scores = {}
    all_entries_scored = []

    for section_name in RELEVANT_SECTIONS:
        info = detected_sections.get(section_name, {"present": False, "content": ""})
        if not info["present"] or not info["content"].strip():
            continue

        section_processed = preprocess_for_similarity(info["content"])
        score = round(compute_similarity(section_processed, jd_processed) * 100, 2)
        section_scores[section_name] = score

        # Break the section into entries to find the single most relevant one
        for entry in split_into_entries(info["content"]):
            if not entry["full_text"].strip():
                continue
            entry_processed = preprocess_for_similarity(entry["full_text"])
            entry_score = round(compute_similarity(entry_processed, jd_processed) * 100, 2)
            all_entries_scored.append({
                "section": section_name,
                "title": entry["title"],
                "score": entry_score,
            })

    overall_relevance = (
        round(sum(section_scores.values()) / len(section_scores), 2)
        if section_scores else 0.0
    )

    most_relevant_entry = None
    if all_entries_scored:
        most_relevant_entry = max(all_entries_scored, key=lambda e: e["score"])

    return {
        "section_scores": section_scores,
        "overall_relevance": overall_relevance,
        "most_relevant_entry": most_relevant_entry,
    }
