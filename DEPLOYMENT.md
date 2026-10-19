# Deployment and operations

## Supported baseline

- Python 3.11 or 3.12
- Streamlit web UI
- Local text processing; no paid API key required
- Uploaded PDF is processed in memory; the app does not intentionally persist the original PDF

## Run locally (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

The English spaCy model is installed by `requirements.txt`. If you already created a virtual environment with an incompatible spaCy version, recreate the environment rather than mixing versions.

## Run with Docker

From the repository root:

```powershell
docker build -t skillbridge-ai:local .
docker run --rm -p 8501:8501 skillbridge-ai:local
```

Open `http://localhost:8501`. The container includes a health check at Streamlit's `/_stcore/health` endpoint. Docker must be installed and running.

## Deploy on Streamlit Community Cloud

1. Confirm the upstream license/permission before publishing the adapted code. The supplied upstream ZIP did not include a license file.
2. Push the repository to GitHub with `app.py`, `requirements.txt`, `src/`, `tests/`, and `.streamlit/config.toml` at the repository root.
3. In Streamlit Community Cloud, create an app, select the repository/branch, and set the main file to `app.py`.
4. Deploy and verify a text-based PDF, a job description, the analysis, and JSON report download.
5. Do not upload real resumes to a public demo unless you understand the host's data-handling terms. Use synthetic/demo resumes for screenshots and presentations.

## Operational safeguards

- The uploader is configured for a 10 MB maximum.
- PDF extraction rejects files larger than 10 MB and documents over 20 pages.
- The app limits job-description input length to 50,000 characters.
- The CI workflow runs tests and byte-compilation on Python 3.11 and 3.12.
- Never commit resumes, exported reports, `.env` files, secrets, or personal candidate data.

## Known limitations before production use

- The final score is a heuristic with hand-set weights; it has not been validated against hiring outcomes and must not be used to automatically reject candidates.
- The similarity feature is TF-IDF/cosine lexical similarity, not transformer-based semantic understanding.
- Skill extraction is dictionary/alias matching and cannot prove proficiency, infer context reliably, or detect all technologies.
- The prerequisite roadmap is manually curated and not an experimentally validated learning recommender.
- Scanned/image-only PDFs are not OCR processed.
- No labeled benchmark, subgroup/fairness audit, authentication, rate limiting, or persistent model monitoring is included. Treat hosted use as an educational demo, not a hiring product.

## Automated deployment verification

The GitHub Actions workflow `.github/workflows/ci.yml` now performs the following on pushes and pull requests:

- Installs the pinned runtime dependencies on Python 3.11 and 3.12.
- Runs the unit test suite and compiles the application, source, tests, and smoke-test script.
- Starts Streamlit and checks `/_stcore/health` using `scripts/smoke_test.py`.
- Builds the Docker image in a separate job.

These checks only count as verified after the GitHub Actions workflow completes successfully. They have not been run remotely from this local working session.

### Run with Docker Compose

```powershell
docker compose up --build -d
docker compose ps
```

Open `http://localhost:8501`. Check logs with `docker compose logs -f skillbridge-ai`, and stop the service with `docker compose down`.

### Local smoke test

After installing dependencies and from the repository root:

```powershell
python scripts/smoke_test.py
```

The smoke test starts Streamlit on a free local port and checks its health endpoint. It does not prove every UI workflow is correct; manually test PDF upload, analysis, and JSON export as well.
