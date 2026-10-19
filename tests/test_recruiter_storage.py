
import pytest

from src import recruiter_storage


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """Use a temporary database for recruiter storage tests."""
    test_db = tmp_path / "test_recruiter.db"
    monkeypatch.setattr(recruiter_storage, "DB_PATH", test_db)
    return test_db


def sample_candidates():
    return [
        {
            "Candidate": "1. candidate_a.pdf",
            "Match score": 82.5,
            "Assessment": "Strong Match",
            "Matched skills": "Python, SQL",
            "Missing skills": "AWS",
            "Keyword coverage (%)": 75.0,
            "Completeness (%)": 90.0,
            "Shortlist": False,
            "Analysis status": "Completed",
        }
    ]


def test_save_and_retrieve_batch(isolated_db):
    batch_id = recruiter_storage.save_recruiter_batch(
        employer_id=101,
        job_description="Python developer with SQL experience",
        candidates=sample_candidates(),
    )

    batch = recruiter_storage.get_recruiter_batch(
        employer_id=101,
        batch_id=batch_id,
    )

    assert batch is not None
    assert batch["batch_id"] == batch_id
    assert "Python developer" in batch["job_description"]
    assert len(batch["candidates"]) == 1
    assert batch["candidates"][0]["Match score"] == 82.5


def test_employer_cannot_retrieve_another_employers_batch(isolated_db):
    batch_id = recruiter_storage.save_recruiter_batch(
        employer_id=101,
        job_description="Data analyst",
        candidates=sample_candidates(),
    )

    batch = recruiter_storage.get_recruiter_batch(
        employer_id=202,
        batch_id=batch_id,
    )

    assert batch is None


def test_history_only_contains_employers_own_batches(isolated_db):
    recruiter_storage.save_recruiter_batch(
        employer_id=101,
        job_description="Role A",
        candidates=sample_candidates(),
    )
    recruiter_storage.save_recruiter_batch(
        employer_id=202,
        job_description="Role B",
        candidates=sample_candidates(),
    )

    history = recruiter_storage.get_recruiter_history(101)

    assert len(history) == 1
    assert history[0]["job_description"] == "Role A"


def test_update_shortlist_status(isolated_db):
    batch_id = recruiter_storage.save_recruiter_batch(
        employer_id=101,
        job_description="Python developer",
        candidates=sample_candidates(),
    )

    updated = recruiter_storage.update_candidate_shortlist(
        employer_id=101,
        batch_id=batch_id,
        candidate_name="1. candidate_a.pdf",
        shortlisted=True,
    )

    assert updated is True

    batch = recruiter_storage.get_recruiter_batch(101, batch_id)
    assert batch["candidates"][0]["Shortlist"] is True


def test_other_employer_cannot_update_shortlist(isolated_db):
    batch_id = recruiter_storage.save_recruiter_batch(
        employer_id=101,
        job_description="Python developer",
        candidates=sample_candidates(),
    )

    updated = recruiter_storage.update_candidate_shortlist(
        employer_id=202,
        batch_id=batch_id,
        candidate_name="1. candidate_a.pdf",
        shortlisted=True,
    )

    assert updated is False

    batch = recruiter_storage.get_recruiter_batch(101, batch_id)
    assert batch["candidates"][0]["Shortlist"] is False


def test_unknown_batch_returns_none(isolated_db):
    assert recruiter_storage.get_recruiter_batch(
        employer_id=101,
        batch_id=999999,
    ) is None
