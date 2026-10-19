# Model and system card — SkillBridge AI

## Intended use

An educational resume self-review tool that compares text in a resume with a user-provided job description and surfaces possible skill gaps. It is intended for individual learning and career preparation.

## Out-of-scope use

- Automated candidate ranking, rejection, hiring, promotion, or other employment decisions.
- Claims that the output matches a specific company's Applicant Tracking System.
- Inferring personality, protected attributes, competence, or truthfulness from resume text.

## Methods

- PDF text extraction with PyMuPDF.
- Skill extraction through a manually curated alias dictionary and regular expressions.
- Text normalization and NLP features through spaCy.
- TF-IDF vectorization and cosine similarity for lexical overlap.
- Fixed, hand-authored score weights and rules for section completeness, keyword coverage, relevance, and skill-gap prioritization.
- A small manually curated prerequisite map for learning-roadmap suggestions.

This is not a trained end-to-end ML model. The current score is a heuristic and is not statistically calibrated.

## Data and evaluation

The app does not bundle a representative labeled resume/job-description dataset. Therefore, no accuracy, F1, calibration, or hiring-outcome performance claim is made. Before making model-quality claims, collect a consented and appropriately licensed evaluation set, define annotation guidelines, use held-out evaluation, report class-specific metrics and confidence intervals where appropriate, and check subgroup disparities.

## Risks and limitations

- Resume formatting, synonyms, abbreviations, missing skills from the dictionary, and PDF extraction quality can affect output.
- A phrase appearing in a resume is not proof of skill proficiency.
- TF-IDF similarity is sensitive to vocabulary overlap and document length.
- Fixed weights and roadmap prerequisites are design choices, not learned or validated truths.
- Resumes contain personal data. Prefer local execution and synthetic examples for public demos; do not commit uploaded files or reports.

## Human oversight

Use results as suggestions for the resume owner to review. Do not use the score as an employment decision or a proxy for a person's value or ability.
