"""
preprocessor.py
---------------
Cleans and normalizes raw text (resume or job description) so that later
steps (skill extraction, TF-IDF) work with consistent, "clean" input.

We use spaCy for tokenization and lemmatization because it's a well-known,
production-grade NLP library that's easy to explain in an interview:
"I used spaCy to break text into tokens, remove stopwords/punctuation,
and reduce words to their base (lemma) form before comparing documents."

We load the small English model 'en_core_web_sm'. It's free and fast,
which fits the "no paid APIs" requirement.
"""

import re
import spacy

# Load the spaCy model once at import time. Loading a model is relatively
# slow, so we don't want to reload it every time a function is called.
try:
    _nlp = spacy.load("en_core_web_sm")
except OSError as exc:
    raise OSError(
        "spaCy model 'en_core_web_sm' is not installed. Run:\n"
        "    python -m spacy download en_core_web_sm\n"
        "and try again."
    ) from exc


def get_nlp():
    """
    Public accessor for the shared spaCy pipeline. Other modules (e.g.
    keyword_analyzer.py) that need spaCy's POS tagging or lemmatization
    should use this instead of importing the private `_nlp` object
    directly, so the model stays loaded exactly once, in one place.
    """
    return _nlp


def clean_text(text: str) -> str:
    """
    Basic text cleanup before NLP processing:
    - Lowercase the text
    - Replace weird whitespace/newlines with single spaces
    - Remove characters that aren't letters, numbers, or common symbols
      used in tech terms (e.g. '+', '#', '.', '-') so things like
      'C++', 'C#', 'Node.js' survive cleaning.

    This is a regex-based step (as required by the tech stack) that runs
    BEFORE the heavier spaCy processing.
    """
    if not text:
        return ""

    text = text.lower()
    # Collapse all whitespace (tabs, newlines, multiple spaces) into one space
    text = re.sub(r"\s+", " ", text)
    # Keep letters, digits, spaces, and a small set of symbols common in
    # tech/skill names (+, #, ., -, /)
    text = re.sub(r"[^a-z0-9\+\#\.\-\/\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_for_similarity(text: str) -> str:
    """
    Prepare text for TF-IDF / cosine similarity comparison.

    Steps:
    1. Basic regex cleaning (clean_text)
    2. spaCy tokenization
    3. Remove stopwords ("the", "and", "is", ...) and punctuation tokens
    4. Lemmatize each remaining token (e.g. "developing" -> "develop")

    Returns a single string of space-separated lemmas, ready to be fed
    into scikit-learn's TfidfVectorizer.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return ""

    doc = _nlp(cleaned)
    lemmas = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
        and token.lemma_.strip() != ""
    ]
    return " ".join(lemmas)
