"""Tests for section_detector.py"""

from src.section_detector import detect_sections, get_section_text

SAMPLE_RESUME = """John Doe
Software Engineer

Summary
Final year engineering student passionate about backend development.

Skills
Python, Java, SQL, React, Git, Docker

Experience
Software Engineering Intern - TechCorp
- Developed REST APIs using Flask and Python
- Built data pipelines using Pandas

Projects
Resume Analyzer
- Built a Python NLP tool using scikit-learn

Education
B.Tech in Computer Science, XYZ University
"""


def test_detects_all_standard_sections_present():
    sections = detect_sections(SAMPLE_RESUME)
    assert sections["Summary"]["present"] is True
    assert sections["Skills"]["present"] is True
    assert sections["Experience"]["present"] is True
    assert sections["Projects"]["present"] is True
    assert sections["Education"]["present"] is True


def test_detects_missing_sections_as_false():
    sections = detect_sections(SAMPLE_RESUME)
    assert sections["Certifications"]["present"] is False
    assert sections["Achievements"]["present"] is False
    assert sections["Internships"]["present"] is False


def test_section_content_extraction():
    sections = detect_sections(SAMPLE_RESUME)
    skills_content = get_section_text(sections, "Skills")
    assert "Python" in skills_content
    assert "React" in skills_content
    # Should not bleed into the next section
    assert "Experience" not in skills_content


def test_alternative_headings_recognized():
    resume = """
    Career Objective
    Aspiring developer looking for opportunities.

    Technical Skills
    Python, C++, SQL

    Work Experience
    - Built internal tools
    """
    sections = detect_sections(resume)
    assert sections["Summary"]["present"] is True  # matched via "career objective"
    assert sections["Skills"]["present"] is True   # matched via "technical skills"
    assert sections["Experience"]["present"] is True  # matched via "work experience"


def test_empty_resume_returns_all_absent():
    sections = detect_sections("")
    assert all(info["present"] is False for info in sections.values())


def test_get_section_text_returns_empty_string_when_absent():
    sections = detect_sections(SAMPLE_RESUME)
    assert get_section_text(sections, "Certifications") == ""


def test_heading_inside_long_sentence_not_falsely_matched():
    # "skills" appears mid-sentence but the line is long, so it should NOT
    # be treated as a section heading.
    resume = "I am responsible for training junior developers on core skills and best practices daily."
    sections = detect_sections(resume)
    assert sections["Skills"]["present"] is False
