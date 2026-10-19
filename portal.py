import json
import streamlit as st
import pandas as pd

from src.portal_auth import init_db, create_user, authenticate
from src.recruiter_storage import (
    init_recruiter_db,
    save_recruiter_batch,
    get_recruiter_history,
    get_recruiter_batch,
    update_candidate_shortlist,
)
# Resume analysis imports are loaded lazily so the login screen can still open
# even if an optional analysis dependency is not installed.
st.set_page_config(page_title="SkillBridge AI", page_icon="✦", layout="wide")
init_db()
init_recruiter_db()
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp { background: #F5F7FC; }
.block-container { max-width: 1250px; padding-top: 2rem; }
h1, h2, h3 { font-family: Manrope, sans-serif; color: #172033; }
.stButton > button { border-radius: 10px; min-height: 2.7rem; font-weight: 700; }
.stButton > button[kind="primary"] { background: #5548D9; color: white; border: none; }
div[data-testid="stTextInput"] input { border-radius: 10px; background: white; }
.hero {
    background: radial-gradient(circle at 90% 15%, #6D63E8, transparent 35%),
                linear-gradient(120deg, #111827, #312E81);
    padding: 2.2rem; border-radius: 22px; color: white; margin-bottom: 1.5rem;
}
.hero h1 { color: white; font-size: 2.6rem; }
.hero p { color: #DDE2FF; max-width: 700px; }
.card { background: white; border: 1px solid #E1E6F0; border-radius: 16px;
        padding: 1.2rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)


def hero(title, description):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{description}</p></div>',
        unsafe_allow_html=True,
    )


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def authentication_screen():
    hero("Your next move starts here.",
         "One workspace for career growth and evidence-based recruitment.")
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown("## Better matches. Clearer decisions.")
        st.markdown("""
        <div class="card"><h3>✦ Employee workspace</h3>
        Analyze your resume, understand skill gaps, and plan next steps.</div>
        <div class="card"><h3>◈ Employer workspace</h3>
        Compare candidate resumes against job requirements and review evidence.</div>
        <div class="card"><h3>✓ Explainable by design</h3>
        Scores support human review; they do not make hiring decisions.</div>
        """, unsafe_allow_html=True)

    with right:
        login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            st.subheader("Welcome back")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Sign in →", type="primary", use_container_width=True):
                user = authenticate(email.strip(), password)
                if user:
                    st.session_state["user"] = user
                    st.session_state.pop("employee_result", None)
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")
        with signup_tab:
            st.subheader("Create your account")
            role = st.radio("I am joining as", ["Employee", "Employer"],
                            horizontal=True, key="signup_role")
            name = st.text_input("Full name", key="signup_name")
            email = st.text_input("Email address", key="signup_email")
            company = st.text_input("Company / organization", key="signup_company") if role == "Employer" else ""
            password = st.text_input("Create password (8+ characters)",
                                      type="password", key="signup_password")
            confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
            st.caption("This local prototype stores account data in SQLite. Use a unique password.")
            if st.button("Create account →", type="primary", use_container_width=True):
                if not name.strip() or not email.strip():
                    st.error("Please enter your name and email.")
                elif role == "Employer" and not company.strip():
                    st.error("Please enter your company or organization.")
                elif len(password) < 8:
                    st.error("Password must contain at least 8 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, message = create_user(name.strip(), email.strip(), password,
                                              role.lower(), company.strip())
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)



def analyze_resume(pdf_bytes, job_description):
    """Connect to the existing SkillBridge analysis modules."""

    from src.pdf_extractor import extract_text_from_pdf
    from src.preprocessor import preprocess_for_similarity
    from src.section_detector import detect_sections
    from src.completeness import calculate_completeness
    from src.skill_extractor import (
        extract_skills,
        compare_skills,
        prioritize_missing_skills,
    )
    from src.bullet_analyzer import analyze_all_bullets
    from src.keyword_analyzer import calculate_keyword_coverage
    from src.relevance import analyze_relevance
    from src.matcher import compute_similarity
    from src.scorer import (
        calculate_skill_match_score,
        calculate_final_score,
        get_score_label,
    )
    from src.learning_roadmap import (
        find_skill_evidence,
        build_learning_roadmap,
    )
    from src.recommendations import generate_recommendations

    # Keep the remainder of your existing analyze_resume()
    # function below this point.

    resume_text = extract_text_from_pdf(pdf_bytes)
    if not resume_text or not resume_text.strip():
        raise ValueError("No readable text was extracted. Try a text-based PDF.")

    sections = detect_sections(resume_text)
    completeness = calculate_completeness(sections)
    skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)
    comparison = compare_skills(skills, jd_skills)
    priorities = prioritize_missing_skills(comparison["missing"], job_description)
    bullets = analyze_all_bullets(sections)
    keyword = calculate_keyword_coverage(resume_text, job_description)
    relevance = analyze_relevance(sections, job_description)
    similarity = compute_similarity(
        preprocess_for_similarity(resume_text),
        preprocess_for_similarity(job_description),
    )
    skill_score = calculate_skill_match_score(comparison["matched"], jd_skills)

    components = {
        "skill_match": skill_score,
        "semantic_similarity": similarity * 100,
        "keyword_coverage": keyword["coverage_percentage"],
        "completeness": completeness["percentage"],
        "relevance": relevance["overall_relevance"],
    }
    final = calculate_final_score(components)
    roadmap = build_learning_roadmap(comparison["missing"], skills, job_description, priorities)
    recommendations = generate_recommendations(priorities, completeness, keyword, bullets)

    return {
        "score": float(final["final_score"]),
        "label": get_score_label(final["final_score"]),
        "skills": sorted(skills),
        "matched": sorted(comparison["matched"]),
        "missing": sorted(comparison["missing"]),
        "components": components,
        "completeness": completeness,
        "keyword": keyword,
        "resume_evidence": find_skill_evidence(resume_text, skills),
        "roadmap": roadmap,
        "recommendations": recommendations,
        "bullets": bullets,
        "resume_text": resume_text,
    }


def employee_resume_studio():
    hero("Resume Studio",
         "Understand your resume, identify role-specific skill gaps, and plan your next steps.")
    with st.container(border=True):
        st.markdown("### 01 · Define your target")
        pdf = st.file_uploader("Upload your resume (PDF)", type=["pdf"],
                               key="employee_resume_pdf")
        jd = st.text_area("Target job description", height=190,
                          placeholder="Paste the job responsibilities, required skills, and qualifications...",
                          key="employee_job_description")
        if st.button("Analyze my resume", type="primary", use_container_width=True):
            if pdf is None:
                st.error("Please upload a PDF resume.")
            elif not jd.strip() or len(jd.strip()) < 30:
                st.error("Please enter a more complete job description (at least 30 characters).")
            elif len(pdf.getvalue()) > 10 * 1024 * 1024:
                st.error("The PDF is larger than 10 MB.")
            else:
                try:
                    with st.spinner("Analyzing your resume..."):
                        st.session_state["employee_result"] = analyze_resume(pdf.getvalue(), jd.strip())
                    st.success("Analysis completed.")
                except Exception as exc:
                    st.error("Resume analysis failed. Check the module names and function signatures in your existing src folder.")
                    st.code(f"{type(exc).__name__}: {exc}")

    result = st.session_state.get("employee_result")
    if not result:
        st.info("Upload a resume and job description to see your analysis.")
        return

    st.markdown("### 02 · Your role-fit overview")
    a, b, c = st.columns(3)
    a.metric("Resume–role match", f"{result['score']:.1f}/100")
    b.metric("Recognized skills", len(result["skills"]))
    c.metric("Skills to review", len(result["missing"]))
    st.caption(f"{result['label']}. This is a heuristic estimate, not a guaranteed ATS result or hiring outcome.")

    tabs = st.tabs(["Overview", "Skills & evidence", "Resume quality", "Learning roadmap", "Recommendations", "Export"])
    with tabs[0]:
        st.markdown("#### Score breakdown")
        labels = {
            "skill_match": "Skill match",
            "semantic_similarity": "Text similarity",
            "keyword_coverage": "Keyword coverage",
            "completeness": "Resume completeness",
            "relevance": "Role relevance",
        }
        st.dataframe(pd.DataFrame([
            {"Assessment": label, "Score (%)": round(float(result["components"].get(key, 0)), 1)}
            for key, label in labels.items()
        ]), hide_index=True, use_container_width=True)
        keyword = result["keyword"]
        st.metric("Keyword coverage", f"{keyword['coverage_percentage']:.1f}%")
        missing_keywords = keyword.get("missing_keywords", [])
        if missing_keywords:
            st.write("**Terms to review:** " + ", ".join(map(str, missing_keywords)))
            st.caption("Only add a keyword if it accurately reflects your experience.")
    with tabs[1]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Matched skills")
            st.write("\n".join(f"- {x}" for x in result["matched"]) if result["matched"] else "No matches detected.")
        with col2:
            st.markdown("#### Skills not detected")
            st.write("\n".join(f"- {x}" for x in result["missing"]) if result["missing"] else "No gaps detected by the current skill dictionary.")
        st.markdown("#### Resume evidence")
        evidence = result["resume_evidence"]
        if evidence:
            st.dataframe(pd.DataFrame([{"Skill": k, "Evidence": v} for k, v in evidence.items()]),
                         hide_index=True, use_container_width=True)
        else:
            st.info("No skill evidence was returned.")
        with st.expander("View extracted resume text"):
            st.text_area("Extracted text", result["resume_text"], height=220, disabled=True)
    with tabs[2]:
        completeness = result["completeness"]
        st.metric("Completeness assessment", f"{completeness.get('percentage', 0):.1f}%")
        st.write("**Detected sections:**", ", ".join(map(str, completeness.get("present_sections", []))) or "None reported")
        st.write("**Core sections not detected:**", ", ".join(map(str, completeness.get("missing_core_sections", []))) or "None reported")
        st.markdown("#### Bullet-point feedback")
        bullets = result["bullets"]
        has_bullets = False
        if isinstance(bullets, dict):
            for section, items in bullets.items():
                if not items:
                    continue
                has_bullets = True
                with st.expander(str(section)):
                    for item in items:
                        if isinstance(item, dict):
                            st.markdown(f"**{item.get('text', '')}**")
                            if item.get("weaknesses"):
                                st.write("Points to improve: " + ", ".join(map(str, item["weaknesses"])))
                            if item.get("suggestion"):
                                st.info(str(item["suggestion"]))
                        else:
                            st.write(str(item))
        if not has_bullets:
            st.info("No bullet feedback was generated.")
    with tabs[3]:
        roadmap = result["roadmap"]
        if not roadmap:
            st.success("No missing skills were identified by the current skill dictionary.")
        else:
            for i, item in enumerate(roadmap, start=1):
                if isinstance(item, dict):
                    with st.container(border=True):
                        st.markdown(f"**{i}. {item.get('skill', 'Skill')}**")
                        st.caption(f"Priority: {item.get('priority', 'Review')}")
                        if item.get("reason"):
                            st.write(item["reason"])
                        if item.get("learn_first"):
                            st.write("Consider learning first: " + ", ".join(map(str, item["learn_first"])))
                        if item.get("related_skills"):
                            st.write("Related skills: " + ", ".join(map(str, item["related_skills"])))
                else:
                    st.write(f"{i}. {item}")
    with tabs[4]:
        recommendations = result["recommendations"]
        if not recommendations:
            st.info("No specific recommendations were generated.")
        else:
            for i, item in enumerate(recommendations, start=1):
                if isinstance(item, dict):
                    with st.container(border=True):
                        st.markdown(f"**{i}. {item.get('issue', 'Recommendation')}**")
                        if item.get("why_it_matters"):
                            st.write("**Why it matters:** " + str(item["why_it_matters"]))
                        if item.get("suggestion"):
                            st.write("**Suggested next step:** " + str(item["suggestion"]))
                else:
                    st.write(f"{i}. {item}")
    with tabs[5]:
        report = {k: v for k, v in result.items() if k != "resume_text"}
        report_json = json.dumps(report, ensure_ascii=False, indent=2, default=str)
        st.download_button("Download JSON report", report_json.encode("utf-8"),
                           "skillbridge_resume_report.json", "application/json",
                           type="primary", use_container_width=True)


def employee_dashboard(user):
    hero(f"Welcome, {user['name'].split()[0]}.",
         "Your workspace for resume insights, skill development, and career growth.")
    a, b, c = st.columns(3)
    a.metric("Workspace", "Active")
    b.metric("Career tools", "2")
    c.metric("Account", "Employee")
    st.markdown("## Your career toolkit")
    x, y = st.columns(2)
    with x:
        st.markdown('<div class="card"><h3>01 · Resume Studio</h3>Analyze your resume against a target job description.</div>', unsafe_allow_html=True)
        if st.button("Open Resume Studio", use_container_width=True):
            st.session_state["employee_page"] = "Resume Studio"
    with y:
        st.markdown('<div class="card"><h3>02 · Skill roadmap</h3>Review skills to develop and plan learning steps.</div>', unsafe_allow_html=True)
        if st.button("Open Skill Roadmap", use_container_width=True):
            st.session_state["employee_page"] = "Skill Roadmap"
    page = st.session_state.get("employee_page", "Dashboard")
    if page == "Resume Studio":
        employee_resume_studio()
    elif page == "Skill Roadmap":
        hero("Skill Roadmap", "Your learning priorities will be generated after resume analysis.")
        result = st.session_state.get("employee_result")
        if result and result.get("roadmap"):
            for item in result["roadmap"]:
                st.write(item.get("skill", str(item)) if isinstance(item, dict) else item)
        else:
            st.info("Run a resume analysis first to populate your skill roadmap.")




def employer_dashboard(user):
    hero(
        f"Welcome, {user['name'].split()[0]}.",
        "Compare candidate resumes against job requirements and manage "
        "a human-reviewed shortlist.",
    )

    a, b, c = st.columns(3)
    a.metric("Account", "Employer")
    b.metric("Review mode", "Human-led")
    c.metric("Automatic rejection", "Disabled")

    workspace_tab, shortlist_tab, analytics_tab, history_tab = st.tabs(
    [
        "Recruiter Workspace",
        "Candidate Shortlist",
        "Recruiter Analytics",
        "Recruitment History",
    ]
)

    # =====================================================
    # TAB 1: RECRUITER WORKSPACE
    # =====================================================
    with workspace_tab:
        st.markdown("### 01 · Job Requirements")

        job_description = st.text_area(
            "Job description",
            height=180,
            placeholder=(
                "Paste responsibilities, required technical skills, "
                "qualifications, and experience..."
            ),
            key="recruiter_job_description",
        )

        uploaded_files = st.file_uploader(
            "Upload candidate resumes (PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            key="recruiter_resume_uploads",
            help=(
            "Upload up to 50 PDF resumes, maximum 10 MB each. "
            "Use text-based PDFs for the most reliable extraction."
            ),
        )

        if st.button(
            "Analyze candidate batch",
            type="primary",
            use_container_width=True,
        ):
            jd = job_description.strip()

            if len(jd) < 30:
                st.error(
                    "Enter a complete job description "
                    "(at least 30 characters)."
                )
            elif not uploaded_files:
                st.error("Upload at least one candidate PDF.")
            elif len(uploaded_files) > 50:
                st.error("Please analyze a maximum of 50 resumes per batch.")
            elif any(
                len(file.getvalue()) > 10 * 1024 * 1024
                for file in uploaded_files
            ):
                st.error("Each PDF must be 10 MB or smaller.")
            else:
                candidates = []
                progress = st.progress(0)
                status = st.empty()

                # Clear the old editable table for the new batch.
                st.session_state.pop("recruiter_editor", None)

                for index, pdf in enumerate(uploaded_files, start=1):
                    candidate_name = f"{index}. {pdf.name}"

                    status.write(
                        f"Analyzing {index} of {len(uploaded_files)}: "
                        f"{pdf.name}"
                    )

                    try:
                        # Use the existing resume analysis pipeline.
                        result = analyze_resume(
                            pdf.getvalue(),
                            jd,
                        )

                        keyword = result.get("keyword", {})
                        completeness = result.get("completeness", {})

                        candidates.append(
                            {
                                "Candidate": candidate_name,
                                "Match score": round(
                                    float(result.get("score", 0)), 1
                                ),
                                "Assessment": str(
                                    result.get("label", "Reviewed")
                                ),
                                "Matched skills": ", ".join(
                                    map(str, result.get("matched", []))
                                ),
                                "Missing skills": ", ".join(
                                    map(str, result.get("missing", []))
                                ),
                                "Keyword coverage (%)": round(
                                    float(
                                        keyword.get(
                                            "coverage_percentage", 0
                                        )
                                    ),
                                    1,
                                ),
                                "Completeness (%)": round(
                                    float(
                                        completeness.get("percentage", 0)
                                    ),
                                    1,
                                ),
                                "Shortlist": False,
                                "Analysis status": "Completed",
                            }
                        )

                    except Exception as exc:
                        candidates.append(
                            {
                                "Candidate": candidate_name,
                                "Match score": 0.0,
                                "Assessment": "Not assessed",
                                "Matched skills": "",
                                "Missing skills": "",
                                "Keyword coverage (%)": 0.0,
                                "Completeness (%)": 0.0,
                                "Shortlist": False,
                                "Analysis status": (
                                    f"Failed: {type(exc).__name__}: {exc}"
                                ),
                            }
                        )

                    progress.progress(index / len(uploaded_files))

                st.session_state["recruiter_candidates"] = candidates
                st.session_state["recruiter_job_saved"] = jd
                batch_id = save_recruiter_batch(
    employer_id=user["id"],
    job_description=jd,
    candidates=candidates,
)
                   

                st.session_state["recruiter_last_batch_id"] = batch_id
                st.session_state["recruiter_job_saved"] = jd

                status.empty()
                progress.empty()

                successful_count = sum(
                    candidate["Analysis status"] == "Completed"
                    for candidate in candidates
                )

                st.success(
                    f"Batch finished: {successful_count} of "
                    f"{len(candidates)} resumes analyzed successfully."
                )

        candidates = st.session_state.get("recruiter_candidates", [])

        if candidates:
            st.divider()
            st.markdown("### 02 · Candidate comparison")

            st.caption(
                "Match scores are estimates. Review job-related evidence "
                "before making recruitment decisions. Failed analyses "
                "must be reviewed separately."
            )

            table_data = pd.DataFrame(candidates)

            edited_data = st.data_editor(
                table_data,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                key="recruiter_editor",
                disabled=[
                    "Candidate",
                    "Match score",
                    "Assessment",
                    "Matched skills",
                    "Missing skills",
                    "Keyword coverage (%)",
                    "Completeness (%)",
                    "Analysis status",
                ],
                column_config={
                    "Shortlist": st.column_config.CheckboxColumn(
                        "Shortlist",
                        help="Select candidates for further human review.",
                        default=False,
                    ),
                    "Match score": st.column_config.NumberColumn(
                        "Match score",
                        format="%.1f",
                    ),
                },
            )

            updated_candidates = edited_data.to_dict(orient="records")
            st.session_state["recruiter_candidates"] = updated_candidates
            # Save shortlist selections to SQLite.
            batch_id = st.session_state.get("recruiter_last_batch_id")

            if batch_id is not None:
                for candidate in updated_candidates:
                    if candidate.get("Analysis status") == "Completed":
                        update_candidate_shortlist(
                            employer_id=user["id"],
                            batch_id=batch_id,
                            candidate_name=candidate["Candidate"],
                            shortlisted=candidate.get("Shortlist", False),
                        )
            completed = [
                candidate
                for candidate in updated_candidates
                if candidate["Analysis status"] == "Completed"
            ]

            shortlisted = [
                candidate
                for candidate in completed
                if candidate["Shortlist"]
            ]

            col1, col2, col3 = st.columns(3)
            col1.metric("Resumes uploaded", len(updated_candidates))
            col2.metric("Successfully analyzed", len(completed))
            col3.metric("Shortlisted", len(shortlisted))

            with st.expander("Review candidate skill details"):
                for candidate in updated_candidates:
                    st.markdown(f"**{candidate['Candidate']}**")
                    st.write(f"Status: {candidate['Analysis status']}")

                    if candidate["Analysis status"] == "Completed":
                        st.write(
                            "**Matched skills:** "
                            + (
                                candidate["Matched skills"]
                                or "None detected"
                            )
                        )
                        st.write(
                            "**Skills not detected:** "
                            + (
                                candidate["Missing skills"]
                                or "None detected"
                            )
                        )

                    st.divider()

            csv_columns = [
                "Candidate",
                "Match score",
                "Assessment",
                "Matched skills",
                "Missing skills",
                "Keyword coverage (%)",
                "Completeness (%)",
                "Shortlist",
                "Analysis status",
            ]

            comparison_csv = pd.DataFrame(updated_candidates)[
                csv_columns
            ].to_csv(index=False)

            st.download_button(
                "Download candidate comparison (CSV)",
                data=comparison_csv.encode("utf-8-sig"),
                file_name="skillbridge_candidate_comparison.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # =====================================================
    # TAB 2: CANDIDATE SHORTLIST
    # =====================================================
    with shortlist_tab:
        st.markdown("### Candidate Shortlist")

        candidates = st.session_state.get("recruiter_candidates", [])

        shortlisted = [
            candidate
            for candidate in candidates
            if candidate.get("Shortlist", False)
            and candidate.get("Analysis status") == "Completed"
        ]

        if shortlisted:
            st.write(
                f"**{len(shortlisted)} candidate(s)** selected "
                "for further review."
            )

            shortlist_columns = [
                "Candidate",
                "Match score",
                "Assessment",
                "Matched skills",
                "Missing skills",
            ]

            shortlist_df = pd.DataFrame(shortlisted)[shortlist_columns]

            st.dataframe(
                shortlist_df,
                hide_index=True,
                use_container_width=True,
            )

            st.download_button(
                "Download candidate shortlist (CSV)",
                data=shortlist_df.to_csv(index=False).encode("utf-8-sig"),
                file_name="skillbridge_candidate_shortlist.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info(
                "No candidates selected yet. Open Recruiter Workspace, "
                "analyze resumes, and select the Shortlist checkboxes."
            )

        st.caption(
            "Shortlisting is a manual review aid. Candidates are not "
            "automatically rejected or contacted."
        )

    # =====================================================
    # TAB 3: RECRUITER ANALYTICS
    # =====================================================
    with analytics_tab:
        st.markdown("### Recruiter Analytics & Insights")

        candidates = st.session_state.get("recruiter_candidates", [])

        if not candidates:
            st.info(
                "Analyze resumes in Recruiter Workspace to view analytics."
            )
        else:
            successful = [
                candidate
                for candidate in candidates
                if candidate.get("Analysis status") == "Completed"
            ]

            failed = [
                candidate
                for candidate in candidates
                if candidate.get("Analysis status") != "Completed"
            ]

            shortlisted = [
                candidate
                for candidate in successful
                if candidate.get("Shortlist", False)
            ]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Resumes", len(candidates))
            col2.metric("Analyzed Successfully", len(successful))
            col3.metric("Shortlisted", len(shortlisted))
            col4.metric("Analysis Failures", len(failed))

            if successful:
                st.divider()
                st.markdown("#### Candidate Match Scores")

                score_df = pd.DataFrame(
                    [
                        {
                            "Candidate": candidate["Candidate"],
                            "Match Score": float(
                                candidate.get("Match score", 0)
                            ),
                        }
                        for candidate in successful
                    ]
                )

                st.bar_chart(score_df.set_index("Candidate"))

                st.markdown("#### Match Score Distribution")

                score_ranges = pd.cut(
                    score_df["Match Score"],
                    bins=[-0.01, 40, 60, 80, 100],
                    labels=["0–40", "41–60", "61–80", "81–100"],
                    include_lowest=True,
                )

                distribution_df = (
                    score_ranges.value_counts(sort=False)
                    .rename_axis("Score Range")
                    .reset_index(name="Candidates")
                )

                st.bar_chart(distribution_df.set_index("Score Range"))

                st.markdown("#### Most Common Skill Gaps")

                from collections import Counter

                missing_skill_counts = Counter()

                for candidate in successful:
                    missing_skills = candidate.get("Missing skills", "")

                    if isinstance(missing_skills, str):
                        missing_skills = [
                            skill.strip()
                            for skill in missing_skills.split(",")
                            if skill.strip()
                        ]

                    missing_skill_counts.update(missing_skills)

                if missing_skill_counts:
                    gaps_df = pd.DataFrame(
                        missing_skill_counts.most_common(10),
                        columns=["Skill", "Candidates Missing Skill"],
                    )

                    st.bar_chart(gaps_df.set_index("Skill"))

                    st.dataframe(
                        gaps_df,
                        hide_index=True,
                        use_container_width=True,
                    )
                else:
                    st.info("No missing-skill data is available.")

                summary_df = pd.DataFrame(
                    [
                        {
                            "Metric": "Total resumes",
                            "Value": len(candidates),
                        },
                        {
                            "Metric": "Successfully analyzed",
                            "Value": len(successful),
                        },
                        {
                            "Metric": "Analysis failures",
                            "Value": len(failed),
                        },
                        {
                            "Metric": "Shortlisted",
                            "Value": len(shortlisted),
                        },
                    ]
                )

                st.download_button(
                    "Download analytics summary (CSV)",
                    data=summary_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="skillbridge_recruiter_analytics.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            else:
                st.info(
                    "No resumes were analyzed successfully. Review the "
                    "failure statuses before drawing conclusions."
                )

            if failed:
                with st.expander("Review analysis failures"):
                    for candidate in failed:
                        st.write(
                            f"**{candidate['Candidate']}** — "
                            f"{candidate['Analysis status']}"
                        )
    
    # =====================================================
    # TAB 4: RECRUITMENT HISTORY
    # =====================================================
    with history_tab:
        st.markdown("### Recruitment History")
        st.caption(
        "Review previous recruitment batches, compare saved candidate results, "
        "and export historical reports."
        )
        history = get_recruiter_history(user["id"])

        if not history:
            st.info(
                "No saved recruitment batches found. "
                "Analyze a batch in Recruiter Workspace first."
            )
        else:
            history_options = {
                (
                    f"Batch #{batch['batch_id']} · "
                    f"{batch['created_at']} · "
                    f"{len(batch['candidates'])} candidates"
                ): batch["batch_id"]
                for batch in history
            }

            selected_label = st.selectbox(
                "Select a saved recruitment batch",
                options=list(history_options.keys()),
                key="recruiter_history_selection",
            )

            selected_batch_id = history_options[selected_label]

            selected_batch = get_recruiter_batch(
                employer_id=user["id"],
                batch_id=selected_batch_id,
            )

            if selected_batch:
                st.markdown("#### Job Description")
                st.write(selected_batch["job_description"])

                saved_candidates = selected_batch["candidates"]

                successful = [
                    candidate
                    for candidate in saved_candidates
                    if candidate["Analysis status"] == "Completed"
                ]

                shortlisted = [
                    candidate
                    for candidate in successful
                    if candidate["Shortlist"]
                ]

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Candidates", len(saved_candidates))
                col2.metric("Successfully Analyzed", len(successful))
                col3.metric("Shortlisted", len(shortlisted))

                if saved_candidates:
                    st.markdown("#### Saved Candidate Results")

                    history_df = pd.DataFrame(saved_candidates)

                    st.dataframe(
                        history_df,
                        hide_index=True,
                        use_container_width=True,
                    )

                    st.download_button(
                        "Download Historical Batch (CSV)",
                        data=history_df.to_csv(
                            index=False
                        ).encode("utf-8-sig"),
                        file_name=(
                            f"skillbridge_batch_"
                            f"{selected_batch_id}.csv"
                        ),
                        mime="text/csv",
                        use_container_width=True,
                        key=f"download_history_{selected_batch_id}",
                    )
    

def main():
    if "user" not in st.session_state:
        authentication_screen()
        return
    user = st.session_state["user"]
    st.sidebar.markdown("## ✦ SkillBridge AI")
    st.sidebar.caption(f"{user['name']} · {user['role'].title()}")
    if st.sidebar.button("Sign out", use_container_width=True):
        logout()
        st.rerun()
    if user["role"] == "employee":
        employee_dashboard(user)
    else:
        employer_dashboard(user)


if __name__ == "__main__":
    main()
