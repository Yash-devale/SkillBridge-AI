
"""Local account management for the SkillBridge AI MVP."""
import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "skillbridge_users.db"


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                role TEXT NOT NULL CHECK(role IN ('employee', 'employer')),
                company TEXT,
                salt BLOB NOT NULL,
                password_hash BLOB NOT NULL
            )
        """)


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 310_000
    )


def create_user(name, email, password, role, company=""):
    init_db()
    name = name.strip()
    email = email.strip().lower()
    role = role.lower()

    if len(name) < 2:
        return False, "Enter your full name."
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return False, "Enter a valid email address."
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."
    if role not in ("employee", "employer"):
        return False, "Choose Employee or Employer."
    if role == "employer" and len(company.strip()) < 2:
        return False, "Enter your company name."

    salt = os.urandom(16)
    digest = hash_password(password, salt)

    try:
        with connect() as db:
            db.execute(
                """INSERT INTO users
                (name, email, role, company, salt, password_hash)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (name, email, role, company.strip(), salt, digest),
            )
        return True, "Account created. You can now sign in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def authenticate(email, password):
    init_db()
    with connect() as db:
        row = db.execute(
            """SELECT id, name, email, role, company, salt, password_hash
               FROM users WHERE email = ?""",
            (email.strip().lower(),),
        ).fetchone()

    if not row:
        return None

    candidate = hash_password(password, row[5])
    if not hmac.compare_digest(candidate, row[6]):
        return None

    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[3],
        "company": row[4] or "",
    }
