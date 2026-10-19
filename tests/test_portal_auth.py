
import sqlite3

import pytest

from src import portal_auth


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """Use a temporary database instead of the real user database."""
    test_db = tmp_path / "test_users.db"
    monkeypatch.setattr(portal_auth, "DB_PATH", test_db)
    return test_db


def test_create_and_authenticate_user(isolated_db):
    created, message = portal_auth.create_user(
        "Test Employee",
        "employee@example.com",
        "StrongPass123",
        "employee",
    )

    assert created is True
    assert "created" in message.lower()

    user = portal_auth.authenticate(
        "EMPLOYEE@example.com",
        "StrongPass123",
    )

    assert user is not None
    assert user["name"] == "Test Employee"
    assert user["role"] == "employee"


def test_wrong_password_is_rejected(isolated_db):
    portal_auth.create_user(
        "Test Employee",
        "employee@example.com",
        "StrongPass123",
        "employee",
    )

    assert portal_auth.authenticate(
        "employee@example.com",
        "WrongPass123",
    ) is None


def test_duplicate_email_is_rejected(isolated_db):
    portal_auth.create_user(
        "Test Employee",
        "employee@example.com",
        "StrongPass123",
        "employee",
    )

    created, message = portal_auth.create_user(
        "Another Employee",
        "EMPLOYEE@example.com",
        "AnotherPass123",
        "employee",
    )

    assert created is False
    assert "already exists" in message.lower()


def test_short_password_is_rejected(isolated_db):
    created, message = portal_auth.create_user(
        "Test Employee",
        "employee@example.com",
        "short",
        "employee",
    )

    assert created is False
    assert "8 characters" in message.lower()


def test_employer_requires_company(isolated_db):
    created, message = portal_auth.create_user(
        "Test Employer",
        "employer@example.com",
        "StrongPass123",
        "employer",
        "",
    )

    assert created is False
    assert "company" in message.lower()


def test_password_is_not_stored_as_plaintext(isolated_db):
    portal_auth.create_user(
        "Test Employee",
        "employee@example.com",
        "StrongPass123",
        "employee",
    )

    with sqlite3.connect(isolated_db) as db:
        row = db.execute(
            "SELECT salt, password_hash FROM users "
            "WHERE email = ?",
            ("employee@example.com",),
        ).fetchone()

    assert row is not None
    salt, password_hash = row
    assert salt != b""
    assert password_hash != b"StrongPass123"
    assert password_hash == portal_auth.hash_password(
        "StrongPass123", salt
    )
