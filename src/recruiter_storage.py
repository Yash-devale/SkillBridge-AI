
"""SQLite storage for SkillBridge AI recruiter history."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "skillbridge_users.db"


def connect():
    return sqlite3.connect(DB_PATH)


def init_recruiter_db():
    """Create recruiter history tables without modifying user accounts."""
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS recruiter_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer_id INTEGER NOT NULL,
                job_description TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS recruiter_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                candidate_name TEXT NOT NULL,
                match_score REAL,
                assessment TEXT,
                matched_skills TEXT,
                missing_skills TEXT,
                keyword_coverage REAL,
                completeness REAL,
                shortlisted INTEGER NOT NULL DEFAULT 0,
                analysis_status TEXT NOT NULL,
                FOREIGN KEY (batch_id)
                    REFERENCES recruiter_batches(id)
                    ON DELETE CASCADE
            )
        """)


def save_recruiter_batch(employer_id, job_description, candidates):
    """Save a completed batch and its candidate analysis results."""
    init_recruiter_db()

    with connect() as db:
        cursor = db.execute(
            """
            INSERT INTO recruiter_batches (employer_id, job_description)
            VALUES (?, ?)
            """,
            (employer_id, job_description),
        )
        batch_id = cursor.lastrowid

        for candidate in candidates:
            db.execute(
                """
                INSERT INTO recruiter_candidates (
                    batch_id,
                    candidate_name,
                    match_score,
                    assessment,
                    matched_skills,
                    missing_skills,
                    keyword_coverage,
                    completeness,
                    shortlisted,
                    analysis_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    candidate.get("Candidate", ""),
                    candidate.get("Match score", 0),
                    candidate.get("Assessment", ""),
                    candidate.get("Matched skills", ""),
                    candidate.get("Missing skills", ""),
                    candidate.get("Keyword coverage (%)", 0),
                    candidate.get("Completeness (%)", 0),
                    int(bool(candidate.get("Shortlist", False))),
                    candidate.get("Analysis status", "Unknown"),
                ),
            )

    return batch_id


def get_recruiter_history(employer_id):
    """Return saved batches belonging to the specified employer."""
    init_recruiter_db()

    with connect() as db:
        batches = db.execute(
            """
            SELECT id, job_description, created_at
            FROM recruiter_batches
            WHERE employer_id = ?
            ORDER BY id DESC
            """,
            (employer_id,),
        ).fetchall()

        history = []

        for batch_id, job_description, created_at in batches:
            rows = db.execute(
                """
                SELECT candidate_name, match_score, assessment,
                       matched_skills, missing_skills, keyword_coverage,
                       completeness, shortlisted, analysis_status
                FROM recruiter_candidates
                WHERE batch_id = ?
                ORDER BY id
                """,
                (batch_id,),
            ).fetchall()

            candidates = [
                {
                    "Candidate": row[0],
                    "Match score": row[1],
                    "Assessment": row[2],
                    "Matched skills": row[3],
                    "Missing skills": row[4],
                    "Keyword coverage (%)": row[5],
                    "Completeness (%)": row[6],
                    "Shortlist": bool(row[7]),
                    "Analysis status": row[8],
                }
                for row in rows
            ]

            history.append({
                "batch_id": batch_id,
                "job_description": job_description,
                "created_at": created_at,
                "candidates": candidates,
            })

    return history

def get_recruiter_batch(employer_id, batch_id):
    """Return one saved recruitment batch owned by the specified employer."""
    init_recruiter_db()

    with connect() as db:
        batch = db.execute(
            """
            SELECT id, job_description, created_at
            FROM recruiter_batches
            WHERE id = ? AND employer_id = ?
            """,
            (batch_id, employer_id),
        ).fetchone()

        if batch is None:
            return None

        rows = db.execute(
            """
            SELECT candidate_name, match_score, assessment,
                   matched_skills, missing_skills, keyword_coverage,
                   completeness, shortlisted, analysis_status
            FROM recruiter_candidates
            WHERE batch_id = ?
            ORDER BY id
            """,
            (batch_id,),
        ).fetchall()

    candidates = [
        {
            "Candidate": row[0],
            "Match score": row[1],
            "Assessment": row[2],
            "Matched skills": row[3],
            "Missing skills": row[4],
            "Keyword coverage (%)": row[5],
            "Completeness (%)": row[6],
            "Shortlist": bool(row[7]),
            "Analysis status": row[8],
        }
        for row in rows
    ]

    return {
        "batch_id": batch[0],
        "job_description": batch[1],
        "created_at": batch[2],
        "candidates": candidates,
    }

def update_candidate_shortlist(employer_id, batch_id, candidate_name, shortlisted):
    """Update shortlist status only for a batch owned by this employer."""
    init_recruiter_db()

    with connect() as db:
        owner = db.execute(
            """
            SELECT id
            FROM recruiter_batches
            WHERE id = ? AND employer_id = ?
            """,
            (batch_id, employer_id),
        ).fetchone()

        if owner is None:
            return False

        cursor = db.execute(
            """
            UPDATE recruiter_candidates
            SET shortlisted = ?
            WHERE batch_id = ? AND candidate_name = ?
            """,
            (int(bool(shortlisted)), batch_id, candidate_name),
        )

        return cursor.rowcount > 0
