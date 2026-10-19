# SkillBridge AI — Explainable Resume Intelligence & Skill-Gap Analyzer

SkillBridge AI is a Python-based web application that helps job seekers understand how their resumes match a target job description. It provides transparent resume–job matching scores, skill-gap analysis, resume completeness feedback, recommendations, and learning roadmaps.

The project also includes a recruiter workspace for bulk resume analysis, candidate comparison, manual shortlisting, analytics, and recruitment history backed by SQLite.

> **Important:** SkillBridge AI provides an explainable resume–job match estimate. It is not a real Applicant Tracking System (ATS), and its scores do not guarantee interview selection or hiring outcomes.

## Features

### Employee Workspace
- Upload and analyze resumes in PDF format.
- Compare resume content with a target job description.
- Identify matched and missing skills.
- Review keyword coverage and resume completeness.
- View resume feedback and improvement recommendations.
- Explore a learning roadmap for skills to develop.
- Access analysis results and available report exports.

### Recruiter Workspace
- Upload multiple PDF resumes for a common job description.
- Compare candidates using resume–job match scores.
- Review matched and missing skills, keyword coverage, and resume completeness.
- Manually shortlist candidates for further review.
- Export candidate comparison and shortlist data as CSV.
- View analytics, including match-score distribution and common skill gaps.
- Access saved recruitment batches through Recruitment History.

### Authentication and Storage
- Separate employee and employer account roles.
- SQLite-based account storage.
- SQLite storage for recruitment batches and candidate analysis results.
- Database functions for retrieving recruitment history and updating shortlist selections.

### Explainable Analysis
- PDF text extraction.
- Alias-based skill detection.
- Resume section detection and completeness scoring.
- TF-IDF and cosine similarity.
- Keyword coverage and project/experience relevance analysis.
- Evidence-based recommendations and learning-roadmap generation.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Web interface | Streamlit |
| Data handling | Pandas |
| Database | SQLite |
| PDF extraction | PyMuPDF |
| NLP processing | spaCy |
| Similarity analysis | scikit-learn, TF-IDF, cosine similarity |
| Testing | pytest |
| Visualizations | Streamlit charts and existing project visualization tools |

## Project Structure

```text
HireLens-main/
├── app.py
├── portal.py
├── src/
│   ├── __init__.py
│   ├── portal_auth.py
│   ├── recruiter_storage.py
│   ├── pdf_extractor.py
│   ├── preprocessor.py
│   ├── skill_extractor.py
│   ├── learning_roadmap.py
│   ├── recommendations.py
│   ├── matcher.py
│   ├── section_detector.py
│   ├── completeness.py
│   ├── keyword_analyzer.py
│   ├── relevance.py
│   ├── bullet_analyzer.py
│   └── scorer.py
├── tests/
├── requirements.txt
├── README.md
└── skillbridge_users.db   # Generated locally; do not commit
```

The structure above highlights the main files. Other existing modules and project configuration files should remain in place.

### Important files added during this development

- **`src/recruiter_storage.py`** — SQLite functions for saving recruitment batches, retrieving batch history, retrieving an individual batch, and updating candidate shortlist status.
- **`portal.py`** — Updated recruiter interface with candidate comparison, analytics, shortlist handling, CSV exports, and the Recruitment History tab.

The existing `src/portal_auth.py` continues to manage account creation and authentication. It should not be replaced with a separate authentication implementation.

## Installation and Setup

Use the existing project directory.

### 1. Create and activate a virtual environment (recommended)

On Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bat
python -m pip install -r requirements.txt
```

If the application requires the spaCy English language model and it is not installed:

```bat
python -m spacy download en_core_web_sm
```

### 3. Run the application

Launch the main employee application:

```bat
python -m streamlit run app.py
```

Launch the employee/recruiter portal:

```bat
python -m streamlit run portal.py
```

Use the appropriate entry point for the workflow you want to demonstrate.

## Testing

Run the existing test suite:

```bat
python -m pytest -q
```

Check Python syntax for the main portal and recruiter-storage module:

```bat
python -m py_compile portal.py src\recruiter_storage.py
```

The existing test suite previously reported **72 passing tests**. Run it again after the final changes to confirm the current project state.

## Database and Privacy

The application uses SQLite for local account and recruiter data storage. The recruiter storage module uses the project's `skillbridge_users.db` database.

- Keep the database file out of public repositories.
- Do not commit real candidate resumes, personal information, passwords, or analysis reports.
- Use fictional or consented sample resumes for demonstrations.
- Review the `.gitignore` file before committing changes.
- Verify that shortlist updates and historical records persist correctly before relying on them.

Resume analysis scores are estimates based on the application's configured scoring methods. A failed analysis must not be interpreted as a low candidate score.

## Limitations

- Skill detection is based on known skills and aliases, not proof of actual proficiency.
- TF-IDF similarity depends on text overlap and vocabulary.
- Unusual resume formatting may affect section detection.
- Scanned or image-only PDFs may require OCR support, which is not guaranteed by the current extraction pipeline.
- The scoring system has not been validated against representative hiring-outcome data.
- Historical records and shortlist persistence depend on the database integration being configured and verified correctly.
- The system is a decision-support tool, not an automated hiring or rejection system.

## Future Improvements

- DOCX resume support.
- PDF and DOCX report exports.
- Broader skill coverage.
- More advanced semantic matching.
- Configurable scoring weights.
- Additional historical analytics and recruiter reporting.
- Deployment to a suitable hosting platform.

## Author and Attribution

Developed as an engineering portfolio project to demonstrate practical Python development, explainable NLP, data processing, resume analysis, database integration, and interactive web application design.

This project is adapted from the supplied `HireLens-main` source. Confirm the original project's licensing and attribution requirements before publicly redistributing the adapted source.
