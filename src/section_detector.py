"""
section_detector.py
--------------------
Detects which standard resume sections (Summary, Education, Skills,
Projects, Experience, Internships, Certifications, Achievements) are
present in a resume, and extracts the text belonging to each section.

Approach (simple and explainable):
1. Split the resume into individual lines (PyMuPDF preserves line breaks
   reasonably well for most resumes).
2. For each line, check if it looks like a section heading - i.e. the
   line (after cleaning) matches one of our known section aliases almost
   exactly. Headings are usually short, standalone lines (unlike normal
   sentences), so we also require the line to be reasonably short.
3. Once we know which line each heading starts on, the "content" of a
   section is everything between that heading and the next detected
   heading (or the end of the document).

This is a rule-based/regex approach, not a machine-learned classifier -
intentionally, so it stays simple enough to explain in an interview and
never "guesses" a section that isn't really there.
"""

import re
from .sections_data import SECTION_ALIASES

# A heading line is expected to be short. This avoids accidentally matching
# a heading name that appears inside a long sentence (e.g. "...responsible
# for skills training...")
MAX_HEADING_LINE_LENGTH = 40


def _normalize_line(line: str) -> str:
    """Lowercase, strip trailing colons/punctuation, collapse whitespace."""
    line = line.strip().lower()
    line = re.sub(r"[:\-–—•*]+$", "", line).strip()
    line = re.sub(r"\s+", " ", line)
    return line


def _find_matching_section(normalized_line: str):
    """
    Check whether a normalized line exactly matches one of our known
    section aliases. Returns the canonical section name, or None.
    """
    for canonical, aliases in SECTION_ALIASES.items():
        if normalized_line in aliases or normalized_line == canonical.lower():
            return canonical
    return None


def detect_sections(resume_text: str) -> dict:
    """
    Scan resume text line-by-line to find section headings and the text
    belonging to each one.

    Returns
    -------
    dict: {
        "Skills": {"present": True, "heading": "Skills", "content": "..."},
        "Certifications": {"present": False, "heading": None, "content": ""},
        ...
    }
    Every known section name is always a key in the result, even if not
    found (present=False), so calling code never needs to guess.
    """
    lines = resume_text.split("\n")

    # Step 1: find the line index and canonical name of every heading found
    headings_found = []  # list of (line_index, canonical_section_name)
    for idx, raw_line in enumerate(lines):
        if len(raw_line.strip()) == 0 or len(raw_line) > MAX_HEADING_LINE_LENGTH:
            continue
        normalized = _normalize_line(raw_line)
        if not normalized:
            continue
        matched_section = _find_matching_section(normalized)
        if matched_section:
            headings_found.append((idx, matched_section, raw_line.strip()))

    # Step 2: build the result dict, extracting content between headings
    result = {name: {"present": False, "heading": None, "content": ""}
               for name in SECTION_ALIASES}

    for i, (line_idx, section_name, raw_heading) in enumerate(headings_found):
        # Content runs from just after this heading to just before the
        # next detected heading (or end of document).
        next_line_idx = (
            headings_found[i + 1][0] if i + 1 < len(headings_found) else len(lines)
        )
        content_lines = lines[line_idx + 1: next_line_idx]
        content = "\n".join(content_lines).strip()

        # If the same section heading appears more than once (unusual but
        # possible), keep the version with more content.
        existing = result[section_name]
        if not existing["present"] or len(content) > len(existing["content"]):
            result[section_name] = {
                "present": True,
                "heading": raw_heading,
                "content": content,
            }

    return result


def get_section_text(sections: dict, section_name: str) -> str:
    """Convenience getter: returns a section's content, or '' if absent."""
    section = sections.get(section_name)
    return section["content"] if section and section["present"] else ""
