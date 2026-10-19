# SkillBridge AI — Engineering audit

## Summary

This repository is a useful educational resume-analysis application, but it is not yet a validated ML product. Its current core is rule/alias-based extraction, spaCy text processing, TF-IDF/cosine similarity, and a manually weighted heuristic score. No trained model or labeled benchmark is bundled.

## Findings and changes in this hardening pass

| Finding | Risk | Change |
|---|---|---|
| PDF extraction had no explicit size/page guard | Resource exhaustion on very large uploads | Reject PDFs above 10 MB or 20 pages |
| Job-description input length was unbounded | Excessive CPU/memory work in hosted demo | Reject input above 50,000 characters |
| Similarity was described as semantic despite TF-IDF | Misleading technical claim | UI and documentation now call it TF-IDF text similarity |
| Dependencies were broad and the spaCy model setup was separate | Reproducibility/build failures | Constrained key dependency versions and included the compatible spaCy model wheel in requirements |
| No container build recipe | Deployment environment drift | Added Dockerfile, .dockerignore, health check, and run commands |
| No automated CI | Regressions could be merged unnoticed | Added GitHub Actions tests and syntax compilation for Python 3.11/3.12 |
| Intended use and evaluation limits needed clearer documentation | Risk of overstating suitability for hiring | Added MODEL_CARD.md and explicit non-employment-decision limitations |
| No additional PDF guard tests | Upload limits could regress | Added tests for byte-size and page-count limits |

## Remaining gaps before calling it production-ready

1. **Model validation:** No representative labeled resume/job-description benchmark, no baseline comparison, no repeated split evaluation, no confidence intervals, and no external validation.
2. **Score validity:** Fixed weights are hand-chosen and not calibrated against outcomes. Treat the score as a heuristic; never use it for automated candidate rejection.
3. **Semantic matching:** Current similarity is TF-IDF lexical overlap. Sentence embeddings can be added as an optional, separately benchmarked backend, but should not be called better without evidence.
4. **Skill extraction:** A finite alias dictionary can miss synonyms, misspellings, negation, and context. A mention is not proof of proficiency.
5. **Document handling:** Image-only/scanned PDFs are not OCR processed; unusual layouts may extract poorly.
6. **Privacy and access control:** The app has no authentication, quotas, or production-grade multi-tenant isolation. A public deployment should use synthetic demo resumes and clearly warn users about personal data.
7. **Observability:** No production metrics, structured request monitoring, alerting, or drift monitoring. Avoid logging resume content or PII.
8. **Licensing:** The supplied upstream archive contained no LICENSE file. Confirm upstream permission before public redistribution or hosting of the adapted code.
9. **Deployment verification:** Docker/CI configuration was added, but this environment could not build the container or install the spaCy model because outbound network access is unavailable. Validate the complete build and deployed smoke test in a network-enabled environment.

## Before public deployment checklist

- [ ] Verify permission/license for the upstream code.
- [ ] Run `python -m pip install -r requirements.txt` in a clean Python 3.11/3.12 environment.
- [ ] Run `python -m pytest -q` and confirm CI passes.
- [ ] Run `streamlit run app.py` and test valid, invalid, oversized, scanned, and multi-page PDFs.
- [ ] Build and run the Docker image; verify `/_stcore/health`.
- [ ] Deploy with a synthetic resume; verify report export and no unexpected persistence.
- [ ] Review all user-facing text to avoid claims of validated hiring prediction or proprietary ATS replication.
- [ ] Add screenshots and a short demo recording using synthetic data.
