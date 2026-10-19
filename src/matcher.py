"""
matcher.py
----------
Computes "semantic similarity" between a resume and a job description
using TF-IDF (Term Frequency - Inverse Document Frequency) and cosine
similarity - both from scikit-learn.

Why TF-IDF + cosine similarity (instead of a heavier deep-learning model)?
- It's fast, free, needs no GPU or paid API, and runs anywhere.
- It's easy to explain in an interview: "I represent each document as a
  vector of weighted word importances, then measure the angle between the
  two vectors - a smaller angle (cosine similarity closer to 1) means the
  documents use more of the same important words."
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity(resume_text: str, jd_text: str) -> float:
    """
    Compute the cosine similarity between a preprocessed resume and a
    preprocessed job description.

    Parameters
    ----------
    resume_text : str
        Preprocessed (cleaned + lemmatized) resume text.
    jd_text : str
        Preprocessed (cleaned + lemmatized) job description text.

    Returns
    -------
    float
        A similarity score between 0.0 and 1.0. 0 means the documents
        share no meaningful vocabulary; 1 means they are identical in
        terms of word usage patterns.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    # TfidfVectorizer converts each document into a vector where each
    # dimension is a word, and the value reflects how important that word
    # is to that document (frequent in this doc, but rare across all docs).
    vectorizer = TfidfVectorizer()

    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    except ValueError:
        # This happens if, after preprocessing, there are no usable words
        # left at all (e.g. text was only stopwords/symbols).
        return 0.0

    # cosine_similarity returns a 2x2 matrix comparing every pair of the
    # two documents with each other. We want the similarity between
    # document 0 (resume) and document 1 (job description).
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    score = float(similarity_matrix[0][0])

    # Clamp for safety (floating point can rarely nudge just past bounds)
    return max(0.0, min(1.0, score))
