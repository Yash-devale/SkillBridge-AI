"""
app.py
------
The Streamlit user interface for the SkillBridge AI — Resume Intelligence.

This file's job is ONLY to handle the UI: taking user input, calling the
functions in src/, and displaying results. All the actual logic (PDF
extraction, skill matching, scoring, section detection, etc.) lives in
src/, so this file stays focused on layout and presentation.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime, timezone

from src.learning_roadmap import find_skill_evidence, build_learning_roadmap

from src.pdf_extractor import extract_text_from_pdf, PDFExtractionError
from src.preprocessor import preprocess_for_similarity
from src.skill_extractor import extract_skills, compare_skills, prioritize_missing_skills
from src.matcher import compute_similarity
from src.section_detector import detect_sections
from src.completeness import calculate_completeness
from src.keyword_analyzer import calculate_keyword_coverage
from src.relevance import analyze_relevance
from src.bullet_analyzer import analyze_all_bullets
from src.recommendations import generate_recommendations
from src.scorer import calculate_skill_match_score, calculate_final_score, get_score_label, WEIGHTS

MIN_JD_LENGTH = 30  # characters - below this, a JD is too short to analyze meaningfully
MAX_JD_LENGTH = 50_000  # avoid excessive text processing in public deployments

# ----------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="SkillBridge AI — Resume Intelligence",
    page_icon="\U0001F4C4",
    layout="wide",
)

# ----------------------------------------------------------------------
# Professional light-theme styling
# ----------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    .stApp { background-color: #F8F9FB; }

    .app-header-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.1rem;
    }
    .app-header-subtitle {
        font-size: 1.02rem;
        color: #6B7280;
        margin-bottom: 1.2rem;
    }

    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .metric-card-label {
        font-size: 0.82rem;
        color: #6B7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .metric-card-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1F2937;
    }

    .skill-chip-matched {
        display: inline-block;
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        border-radius: 999px;
        padding: 3px 12px;
        margin: 3px 4px 3px 0;
        font-size: 0.85rem;
    }
    .skill-chip-missing {
        display: inline-block;
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
        border-radius: 999px;
        padding: 3px 12px;
        margin: 3px 4px 3px 0;
        font-size: 0.85rem;
    }
    .skill-chip-additional {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        border-radius: 999px;
        padding: 3px 12px;
        margin: 3px 4px 3px 0;
        font-size: 0.85rem;
    }

    .priority-high { color: #B91C1C; font-weight: 700; }
    .priority-medium { color: #B45309; font-weight: 700; }
    .priority-low { color: #6B7280; font-weight: 700; }

    .recommendation-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #4F46E5;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .recommendation-label {
        font-weight: 700;
        color: #374151;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }

    .section-badge-present {
        display: inline-block;
        background-color: #ECFDF5;
        color: #047857;
        border-radius: 6px;
        padding: 4px 10px;
        margin: 3px 4px 3px 0;
        font-size: 0.85rem;
        border: 1px solid #A7F3D0;
    }
    .section-badge-missing {
        display: inline-block;
        background-color: #F3F4F6;
        color: #6B7280;
        border-radius: 6px;
        padding: 4px 10px;
        margin: 3px 4px 3px 0;
        font-size: 0.85rem;
        border: 1px solid #E5E7EB;
    }

    .privacy-note {
        font-size: 0.82rem;
        color: #6B7280;
        margin-top: 1.5rem;
        border-top: 1px solid #E5E7EB;
        padding-top: 0.8rem;
    }
</style>
"""


def render_gauge(score: float) -> go.Figure:
    """Build a Plotly gauge chart to visually show the overall match score."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " / 100", "font": {"size": 40, "color": "#1F2937"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#9CA3AF"},
                "bar": {"color": "#4F46E5"},
                "bgcolor": "#FFFFFF",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 25], "color": "#FEE2E2"},
                    {"range": [25, 50], "color": "#FEF3C7"},
                    {"range": [50, 75], "color": "#DBEAFE"},
                    {"range": [75, 100], "color": "#D1FAE5"},
                ],
            },
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#1F2937"},
    )
    return fig


def render_score_breakdown_chart(breakdown: dict) -> go.Figure:
    """Horizontal bar chart showing each component's weighted contribution."""
    labels = [info["label"] for info in breakdown.values()]
    contributions = [info["contribution"] for info in breakdown.values()]
    raw_scores = [info["raw"] for info in breakdown.values()]
    weights = [info["weight"] for info in breakdown.values()]

    text_labels = [
        f"{raw:.1f}/100 raw x {w*100:.0f}% weight = {c:.1f} pts"
        for raw, w, c in zip(raw_scores, weights, contributions)
    ]

    fig = go.Figure(go.Bar(
        x=contributions,
        y=labels,
        orientation="h",
        marker_color="#4F46E5",
        text=text_labels,
        textposition="outside",
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title="Points contributed to final score",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#1F2937"},
        xaxis=dict(range=[0, max(WEIGHTS.values()) * 100 + 10]),
    )
    return fig


def render_metric_card(label: str, value: str):
    st.markdown(
        f"""<div class="metric-card">
                <div class="metric-card-label">{label}</div>
                <div class="metric-card-value">{value}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def run_full_analysis(resume_raw_text: str, resume_processed: str, resume_skills: set,
                       sections: dict, completeness_result: dict, bullet_results: dict,
                       jd_text: str) -> dict:
    """
    Run the full JD-dependent analysis pipeline (everything that changes
    depending on which job description is being compared against).

    Resume-only analysis (sections, completeness, bullets) is computed
    once by the caller and passed in, since it doesn't change per-JD -
    this avoids redundant work when comparing multiple job descriptions.
    """
    jd_processed = preprocess_for_similarity(jd_text)
    jd_skills = extract_skills(jd_text)
    comparison = compare_skills(resume_skills, jd_skills)
    priorities = prioritize_missing_skills(comparison["missing"], jd_text)

    similarity = compute_similarity(resume_processed, jd_processed)
    keyword_result = calculate_keyword_coverage(resume_raw_text, jd_text)
    relevance_result = analyze_relevance(sections, jd_text)

    skill_match_score = calculate_skill_match_score(comparison["matched"], jd_skills)
    components = {
        "skill_match": skill_match_score,
        "semantic_similarity": similarity * 100,
        "keyword_coverage": keyword_result["coverage_percentage"],
        "completeness": completeness_result["percentage"],
        "relevance": relevance_result["overall_relevance"],
    }
    score_result = calculate_final_score(components)
    label = get_score_label(score_result["final_score"])

    recs = generate_recommendations(priorities, completeness_result, keyword_result, bullet_results)
    resume_evidence = find_skill_evidence(resume_raw_text, resume_skills)
    jd_evidence = find_skill_evidence(jd_text, jd_skills)
    learning_roadmap = build_learning_roadmap(comparison["missing"], resume_skills, jd_text, priorities)

    return {
        "jd_skills": jd_skills,
        "comparison": comparison,
        "priorities": priorities,
        "similarity": similarity,
        "keyword_result": keyword_result,
        "relevance_result": relevance_result,
        "score_result": score_result,
        "label": label,
        "recommendations": recs,
        "resume_evidence": resume_evidence,
        "jd_evidence": jd_evidence,
        "learning_roadmap": learning_roadmap,
    }


def render_skill_chips(skills, css_class):
    if not skills:
        st.caption("None found.")
        return
    chips_html = "".join(f'<span class="{css_class}">{s}</span>' for s in sorted(skills))
    st.markdown(chips_html, unsafe_allow_html=True)


def render_section_badges(sections: dict, completeness_result: dict):
    badges_html = ""
    for section_name in sections:
        present = section_name in completeness_result["present_sections"]
        css_class = "section-badge-present" if present else "section-badge-missing"
        icon = "\u2713" if present else "\u2014"
        badges_html += f'<span class="{css_class}">{icon} {section_name}</span>'
    st.markdown(badges_html, unsafe_allow_html=True)


def render_result_dashboard(result: dict, resume_raw_text: str, sections: dict,
                             completeness_result: dict, bullet_results: dict, key_prefix: str = ""):
    """Renders the full results dashboard for one resume-vs-JD analysis."""
    score_result = result["score_result"]
    final_score = score_result["final_score"]
    breakdown = score_result["breakdown"]
    comparison = result["comparison"]
    priorities = result["priorities"]
    relevance_result = result["relevance_result"]
    keyword_result = result["keyword_result"]

    st.divider()
    st.header("Results")

    gauge_col, label_col = st.columns([2, 1])
    with gauge_col:
        st.plotly_chart(render_gauge(final_score), use_container_width=True,
                         key=f"{key_prefix}_gauge")
    with label_col:
        st.metric("Match Category", result["label"])
        st.caption("Resume-Job Match Score - not a guaranteed ATS score.")

    # ---- Metric cards for each component ----
    st.subheader("Score Components")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("Skill Match", f"{breakdown['skill_match']['raw']:.0f}%")
    with c2:
        render_metric_card("Text Similarity (TF-IDF)", f"{breakdown['semantic_similarity']['raw']:.0f}%")
    with c3:
        render_metric_card("Keyword Coverage", f"{breakdown['keyword_coverage']['raw']:.0f}%")
    with c4:
        render_metric_card("Resume Completeness", f"{breakdown['completeness']['raw']:.0f}%")
    with c5:
        render_metric_card("Project/Exp. Relevance", f"{breakdown['relevance']['raw']:.0f}%")

    with st.expander("How was this score calculated?", expanded=False):
        st.plotly_chart(render_score_breakdown_chart(breakdown), use_container_width=True,
                         key=f"{key_prefix}_breakdown_chart")
        st.markdown(
            "The final score is a **weighted average** of five signals: "
            "**Skill Match** (% of the JD's required skills found in your resume), "
            "**Text Similarity** (TF-IDF + cosine similarity between the full "
            "resume and JD text), **Keyword Coverage** (% of the JD's most frequent "
            "important terms present in your resume), **Resume Completeness** "
            "(% of expected resume sections detected), and **Project/Experience "
            "Relevance** (similarity of your Projects/Experience/Internships to the JD)."
        )

        # Build a small Pandas DataFrame to present the breakdown as a
        # clean, sortable table - a simple, genuine use of Pandas for
        # structuring tabular data (raw score, weight, contribution)
        # rather than hand-formatting a markdown table.
        breakdown_df = pd.DataFrame([
            {
                "Signal": info["label"],
                "Raw Score": f"{info['raw']:.1f}/100",
                "Weight": f"{info['weight']*100:.0f}%",
                "Contribution": f"{info['contribution']:.1f} pts",
            }
            for info in breakdown.values()
        ])
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

        st.markdown(
            "**Limitations:** This is a keyword- and similarity-based estimate, not a "
            "simulation of any specific company's ATS. It cannot judge soft skills, "
            "interview performance, or culture fit, and it can only recognize skills "
            "and sections written in a way it can detect (see README for details)."
        )

    # ---- Skills ----
    st.subheader("Skill Comparison")
    m_col, mi_col, a_col = st.columns(3)
    with m_col:
        st.markdown("**Matched Skills**")
        render_skill_chips(comparison["matched"], "skill-chip-matched")
    with mi_col:
        st.markdown("**Missing Skills**")
        render_skill_chips(comparison["missing"], "skill-chip-missing")
    with a_col:
        st.markdown("**Additional Skills** *(not required by JD)*")
        render_skill_chips(comparison["additional"], "skill-chip-additional")

    st.markdown("**Skill Gap Priority**")
    if any(priorities.values()):
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown('<span class="priority-high">HIGH PRIORITY</span>', unsafe_allow_html=True)
            for s in priorities["High"]:
                st.markdown(f"- {s}")
        with p2:
            st.markdown('<span class="priority-medium">MEDIUM PRIORITY</span>', unsafe_allow_html=True)
            for s in priorities["Medium"]:
                st.markdown(f"- {s}")
        with p3:
            st.markdown('<span class="priority-low">LOW PRIORITY</span>', unsafe_allow_html=True)
            for s in priorities["Low"]:
                st.markdown(f"- {s}")
        st.caption(
            "Priority is based on how many times each missing skill is mentioned "
            "in the job description: 3+ mentions = High, 2 = Medium, 1 = Low."
        )
    else:
        st.caption("No missing skills - great coverage!")

    # ---- Evidence-backed skill explanations ----
    st.subheader("Evidence Behind Skill Detection")
    st.caption("A detected skill means its name or known alias appears in the text; it does not prove proficiency.")
    evidence_rows = []
    for skill in sorted(comparison["matched"] | comparison["missing"]):
        if skill in comparison["matched"]:
            evidence_rows.append({"Skill": skill, "Status": "Detected in resume and role", "Resume evidence": result["resume_evidence"].get(skill, "No sentence-level evidence found"), "Role evidence": result["jd_evidence"].get(skill, "No sentence-level evidence found")})
        else:
            evidence_rows.append({"Skill": skill, "Status": "Not detected in resume", "Resume evidence": "No matching phrase detected", "Role evidence": result["jd_evidence"].get(skill, "No sentence-level evidence found")})
    if evidence_rows:
        st.dataframe(pd.DataFrame(evidence_rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No recognized skills were found in the target role text.")

    # ---- Adaptive learning roadmap ----
    st.subheader("Suggested Skill-Building Roadmap")
    st.caption("Order is based on target-role mention frequency and a small, transparent prerequisite map—not an assessment of your actual ability.")
    roadmap = result.get("learning_roadmap", [])
    if roadmap:
        for step, item in enumerate(roadmap, start=1):
            prereq_text = ", ".join(item["prerequisites"]) or "No prerequisite configured"
            learn_first = ", ".join(item["learn_first"]) or "None identified in the target skill gaps"
            with st.expander(f"{step}. {item['skill']} · {item['priority']} priority"):
                st.write(item["reason"])
                st.markdown(f"**Prerequisites in roadmap:** {learn_first}")
                st.markdown(f"**Suggested foundations:** {prereq_text}")
                if item["related_skills"]:
                    st.markdown("**Related topics to explore:** " + ", ".join(item["related_skills"]))
    else:
        st.success("No missing skills from the currently supported skill dictionary were detected.")

    # Downloadable report contains derived findings only; no model claims or invented credentials.
    export_report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "report_type": "explainable_resume_role_comparison",
        "report_schema_version": "1.0",
        "score_label": "Resume-Job Match Score (not a guaranteed ATS score)",
        "match_score": round(float(final_score), 2),
        "score_components": {k: {"raw_score": round(float(v["raw"]), 2), "weight": v["weight"]} for k, v in breakdown.items()},
        "matched_skills": sorted(comparison["matched"]),
        "missing_skills": sorted(comparison["missing"]),
        "additional_resume_skills": sorted(comparison["additional"]),
        "resume_skill_evidence": result["resume_evidence"],
        "job_description_skill_evidence": result["jd_evidence"],
        "learning_roadmap": roadmap,
        "limitations": ["Skill detection is phrase/alias based and does not prove proficiency.", "The score is a heuristic, has not been validated against hiring outcomes, and is not a proprietary ATS score or a hiring recommendation.", "TF-IDF cosine similarity measures lexical overlap rather than deep semantic understanding.", "Roadmap prerequisites are a small manually curated map."]
    }
    st.download_button("Download analysis report (JSON)", data=json.dumps(export_report, indent=2, ensure_ascii=False), file_name="skillbridge_analysis_report.json", mime="application/json", key=f"{key_prefix}_download_json")

    # ---- Resume structure analysis ----
    st.subheader("Resume Structure Analysis")
    st.markdown(f"**Completeness: {completeness_result['percentage']:.0f}%**")
    render_section_badges(sections, completeness_result)
    if completeness_result["missing_core_sections"]:
        st.caption(
            "Missing core section(s): " + ", ".join(completeness_result["missing_core_sections"])
        )

    # ---- Relevance ----
    if relevance_result["section_scores"]:
        st.markdown("**Project / Experience / Internship Relevance**")
        rel_cols = st.columns(len(relevance_result["section_scores"]))
        for col, (section_name, score) in zip(rel_cols, relevance_result["section_scores"].items()):
            with col:
                render_metric_card(f"{section_name} Relevance", f"{score:.0f}%")
        if relevance_result["most_relevant_entry"]:
            entry = relevance_result["most_relevant_entry"]
            st.caption(
                f"Most relevant entry: **{entry['title']}** ({entry['section']}) - "
                f"{entry['score']:.0f}% relevance to this job description."
            )
    else:
        st.caption("No Projects, Experience, or Internships section detected to analyze.")

    # ---- Keyword gap ----
    with st.expander(f"Keyword Gap Analysis ({keyword_result['coverage_percentage']:.0f}% coverage)"):
        kw1, kw2 = st.columns(2)
        with kw1:
            st.markdown("**Found in your resume:**")
            st.write(", ".join(keyword_result["found_keywords"]) or "None")
        with kw2:
            st.markdown("**Missing / not found:**")
            st.write(", ".join(keyword_result["missing_keywords"]) or "None")
        st.caption(
            "Keywords are the most frequent nouns/proper nouns in the job "
            "description (via spaCy part-of-speech tagging), not limited to "
            "our curated skill list - this catches broader role/domain terms."
        )

    # ---- Bullet analysis ----
    if bullet_results:
        st.subheader("Bullet-by-Bullet Analysis")
        for section_name, bullets in bullet_results.items():
            st.markdown(f"**{section_name}**")
            for i, b in enumerate(bullets):
                icon = "\u2705" if not b["weaknesses"] else "\u26A0\uFE0F"
                with st.expander(f"{icon} {b['text'][:80]}{'...' if len(b['text']) > 80 else ''}"):
                    st.markdown(f"**Original bullet:** {b['text']}")
                    if b["strengths"]:
                        st.markdown("**Strengths:**")
                        for s in b["strengths"]:
                            st.markdown(f"- {s}")
                    if b["weaknesses"]:
                        st.markdown("**Areas to improve:**")
                        for w in b["weaknesses"]:
                            st.markdown(f"- {w}")
                    st.markdown(f"**Suggestion:** {b['suggestion']}")
    else:
        st.caption("No bullet points detected in Experience, Internships, or Projects sections.")

    # ---- Recommendations ----
    st.subheader("Actionable Recommendations")
    recs = result["recommendations"]
    if recs:
        for r in recs:
            st.markdown(
                f"""<div class="recommendation-card">
                        <div class="recommendation-label">Issue</div>
                        <div>{r['issue']}</div>
                        <div class="recommendation-label" style="margin-top:8px;">Why it matters</div>
                        <div>{r['why_it_matters']}</div>
                        <div class="recommendation-label" style="margin-top:8px;">Suggested improvement</div>
                        <div>{r['suggestion']}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.success("No major issues detected - your resume looks well-aligned with this job description!")

    with st.expander("View extracted resume text"):
        st.text(resume_raw_text)


def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown('<div class="app-header-title">SkillBridge AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-header-subtitle">Explainable resume matching, evidence-backed skill gaps, and an adaptive learning roadmap.</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "Privacy: resume text is processed in the current app session and is not intentionally persisted by this application. Avoid uploading highly sensitive documents to any hosted demo.\n\n"
        "This score is a **Resume-Job Match Score**, not a guaranteed ATS "
        "(Applicant Tracking System) score. Real ATS tools are proprietary; "
        "this tool gives you an independent, explainable estimate to help "
        "you improve your resume.",
        icon="\u2139\uFE0F",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Upload Your Resume (PDF)")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    with col2:
        st.subheader("2. Paste the Job Description")
        jd_text = st.text_area(
            "Job description text", height=220,
            placeholder="Paste the full job description here...",
        )

    analyze_clicked = st.button("Analyze Resume", type="primary")

    if analyze_clicked:
        if uploaded_file is None:
            st.error("Please upload a resume PDF before analyzing.")
        elif not jd_text or not jd_text.strip():
            st.error("Please paste a job description before analyzing.")
        elif len(jd_text.strip()) > MAX_JD_LENGTH:
            st.error(f"The job description is too long. Please keep it under {MAX_JD_LENGTH:,} characters.")
        elif len(jd_text.strip()) < MIN_JD_LENGTH:
            st.error(
                f"The job description looks too short (under {MIN_JD_LENGTH} characters) "
                "to analyze meaningfully. Please paste the full job description."
            )
        else:
            with st.spinner("Extracting text from your resume..."):
                try:
                    resume_raw_text = extract_text_from_pdf(uploaded_file.getvalue())
                except PDFExtractionError as e:
                    st.error(f"Could not process your resume: {e}")
                    resume_raw_text = None

            if resume_raw_text:
                try:
                    with st.spinner("Analyzing your resume..."):
                        resume_processed = preprocess_for_similarity(resume_raw_text)
                        resume_skills = extract_skills(resume_raw_text)
                        sections = detect_sections(resume_raw_text)
                        completeness_result = calculate_completeness(sections)
                        bullet_results = analyze_all_bullets(sections)

                        if not resume_skills:
                            st.warning(
                                "No recognized technical skills were detected in your resume. "
                                "The skill-based portion of your score may be low as a result. "
                                "Consider adding a clearly labeled Skills section."
                            )

                        result = run_full_analysis(
                            resume_raw_text, resume_processed, resume_skills,
                            sections, completeness_result, bullet_results, jd_text,
                        )
                except Exception:
                    # Catch-all safety net: never show a raw Python traceback
                    # to the user. Analysis failures here are unexpected
                    # (all known edge cases are handled earlier/inside each
                    # module), so we fail gracefully instead.
                    st.error(
                        "Something went wrong while analyzing your resume. This can "
                        "happen with unusual PDF formatting or an extremely short/long "
                        "document. Please try a different PDF or job description."
                    )
                    result = None

                # Persist to session_state so the dashboard survives reruns
                # triggered by expanding/collapsing widgets below.
                if result is not None:
                    st.session_state["last_result"] = result
                    st.session_state["last_resume_raw_text"] = resume_raw_text
                    st.session_state["last_sections"] = sections
                    st.session_state["last_completeness"] = completeness_result
                    st.session_state["last_bullets"] = bullet_results
                    # Cache resume-only analysis for multi-JD comparison too
                    st.session_state["resume_processed"] = resume_processed
                    st.session_state["resume_skills"] = resume_skills

    if "last_result" in st.session_state:
        render_result_dashboard(
            st.session_state["last_result"],
            st.session_state["last_resume_raw_text"],
            st.session_state["last_sections"],
            st.session_state["last_completeness"],
            st.session_state["last_bullets"],
            key_prefix="single",
        )

        # ---- Multi-job-description comparison ----
        st.divider()
        st.header("Compare Against Multiple Job Descriptions")
        st.caption(
            "See which of several roles your resume currently aligns with most strongly."
        )

        if "extra_jds" not in st.session_state:
            st.session_state["extra_jds"] = [{"title": "", "text": ""}]

        for i, jd_entry in enumerate(st.session_state["extra_jds"]):
            with st.expander(f"Job Description #{i + 1}", expanded=(i == 0)):
                jd_entry["title"] = st.text_input(
                    "Role title (for display)", value=jd_entry["title"], key=f"jd_title_{i}",
                    placeholder="e.g. Backend Developer",
                )
                jd_entry["text"] = st.text_area(
                    "Job description text", value=jd_entry["text"], key=f"jd_text_{i}",
                    height=150,
                )

        add_col, compare_col = st.columns([1, 1])
        with add_col:
            if st.button("+ Add Another Job Description"):
                st.session_state["extra_jds"].append({"title": "", "text": ""})
                st.rerun()
        with compare_col:
            compare_clicked = st.button("Compare All Jobs", type="primary")

        if compare_clicked:
            valid_jds = [
                jd for jd in st.session_state["extra_jds"]
                if jd["text"].strip() and len(jd["text"].strip()) >= MIN_JD_LENGTH
            ]
            if not valid_jds:
                st.error("Please fill in at least one job description (30+ characters) to compare.")
            else:
                with st.spinner("Comparing your resume against each job description..."):
                    comparison_results = []
                    for jd in valid_jds:
                        r = run_full_analysis(
                            st.session_state["last_resume_raw_text"],
                            st.session_state["resume_processed"],
                            st.session_state["resume_skills"],
                            st.session_state["last_sections"],
                            st.session_state["last_completeness"],
                            st.session_state["last_bullets"],
                            jd["text"],
                        )
                        title = jd["title"].strip() or "Untitled Role"
                        comparison_results.append((title, r["score_result"]["final_score"]))

                comparison_results.sort(key=lambda x: x[1], reverse=True)
                titles = [t for t, _ in comparison_results]
                scores = [s for _, s in comparison_results]

                fig = go.Figure(go.Bar(
                    x=scores, y=titles, orientation="h",
                    marker_color="#4F46E5",
                    text=[f"{s:.0f}%" for s in scores],
                    textposition="outside",
                ))
                fig.update_layout(
                    height=max(200, 80 * len(titles)),
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis=dict(range=[0, 100], title="Match Score"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#1F2937"},
                )
                st.plotly_chart(fig, use_container_width=True, key="multi_jd_chart")
                st.success(
                    f"Your resume currently aligns most strongly with: **{titles[0]}** "
                    f"({scores[0]:.0f}/100)."
                )

    st.markdown(
        '<div class="privacy-note">Your resume is processed locally and is not '
        'permanently stored.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
