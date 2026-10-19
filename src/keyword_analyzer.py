"""
keyword_analyzer.py
--------------------
"Keyword Gap Analysis" is intentionally broader than skill_extractor.py.

skill_extractor.py only recognizes skills from our curated database
(skills_data.py) - it's precise but limited to well-known tech terms.

keyword_analyzer.py instead pulls out the most FREQUENT meaningful nouns
and proper nouns from the job description - things like "stakeholder",
"deployment", "microservices", "agile", role titles, domain terms, etc.
This catches important JD language that isn't a formal "skill" but still
matters for a strong match (e.g. "cross-functional", "scalable").

Method (simple and explainable):
1. Run the job description through spaCy.
2. Keep only nouns and proper nouns (NOUN / PROPN part-of-speech tags) -
   these tend to carry the most topical meaning in job postings.
3. Remove stopwords, punctuation, and very short tokens.
4. Count frequency; the most frequently mentioned terms are treated as
   the most "important" keywords for that JD.
5. Check which of those keywords also appear (in lemma form) in the resume.
"""

from collections import Counter
from .preprocessor import get_nlp, clean_text

MIN_KEYWORD_LENGTH = 3

# Generic job-posting scaffolding words. These are common NOUN/PROPN tokens
# in almost any job description ("Job Title:", "Requirements:", "strong
# understanding of...") that carry little real signal about what the role
# actually needs. Filtering them out was added after end-to-end testing
# showed they were crowding out genuinely useful domain keywords.
JD_BOILERPLATE_WORDS = {
    "title", "role", "responsibility", "responsibilities", "requirement",
    "requirements", "experience", "understanding", "familiarity",
    "proficiency", "skill", "skills", "team", "candidate", "plus", "year",
    "years", "ability", "knowledge", "environment", "join", "job", "work",
    "opportunity", "member", "company",
}

# spaCy's lemmatizer sometimes produces grammatically "correct" but unnatural
# base forms (e.g. "data" -> "datum"). We map these back to the common form
# so keywords shown to the user look natural, without affecting matching
# logic (the override is applied consistently to both JD and resume lemmas).
LEMMA_OVERRIDES = {
    "datum": "data",
    "medium": "media",
}


def _apply_lemma_overrides(lemma: str) -> str:
    return LEMMA_OVERRIDES.get(lemma, lemma)


def extract_keywords(text: str, top_n: int = 25) -> list:
    """
    Extract the top N most frequent meaningful noun/proper-noun keywords
    from a piece of text (typically a job description).

    Returns a list of (keyword, count) tuples, ordered by frequency
    (highest first).
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    doc = get_nlp()(cleaned)
    candidates = [
        _apply_lemma_overrides(token.lemma_)
        for token in doc
        if token.pos_ in ("NOUN", "PROPN")
        and not token.is_stop
        and not token.is_punct
        and len(token.lemma_) >= MIN_KEYWORD_LENGTH
        and token.lemma_ not in JD_BOILERPLATE_WORDS
    ]

    counts = Counter(candidates)
    return counts.most_common(top_n)


def calculate_keyword_coverage(resume_text: str, jd_text: str, top_n: int = 25) -> dict:
    """
    Determine what % of the job description's important keywords also
    appear in the resume.

    Returns
    -------
    dict: {
        "coverage_percentage": float,
        "found_keywords": [...],
        "missing_keywords": [...],
        "total_keywords_checked": int,
    }
    """
    jd_keywords = extract_keywords(jd_text, top_n=top_n)

    if not jd_keywords:
        return {
            "coverage_percentage": 0.0,
            "found_keywords": [],
            "missing_keywords": [],
            "total_keywords_checked": 0,
        }

    # Build a lemmatized version of the resume so "developing" matches
    # a JD keyword lemma "develop", etc.
    resume_cleaned = clean_text(resume_text)
    resume_doc = get_nlp()(resume_cleaned) if resume_cleaned else None
    resume_lemmas = set()
    if resume_doc is not None:
        resume_lemmas = {_apply_lemma_overrides(token.lemma_) for token in resume_doc}

    found = []
    missing = []
    for keyword, _count in jd_keywords:
        if keyword in resume_lemmas:
            found.append(keyword)
        else:
            missing.append(keyword)

    coverage_pct = round((len(found) / len(jd_keywords)) * 100, 2)

    return {
        "coverage_percentage": coverage_pct,
        "found_keywords": found,
        "missing_keywords": missing,
        "total_keywords_checked": len(jd_keywords),
    }
