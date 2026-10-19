from src.learning_roadmap import find_skill_evidence, build_learning_roadmap


def test_evidence_only_returns_literal_mentions():
    text = "Built a Python API. Used pandas for analysis."
    evidence = find_skill_evidence(text, {"Python", "Pandas", "Docker"})
    assert "Python" in evidence
    assert "Pandas" in evidence
    assert "Docker" not in evidence


def test_roadmap_only_contains_missing_skills_and_priorities():
    missing = {"Machine Learning", "Python"}
    priorities = {"High": ["Machine Learning"], "Medium": [], "Low": ["Python"]}
    roadmap = build_learning_roadmap(missing, set(), "Python Machine Learning Machine Learning", priorities)
    assert {row["skill"] for row in roadmap} == missing
    assert next(row for row in roadmap if row["skill"] == "Machine Learning")["priority"] == "High"
    assert all("reason" in row for row in roadmap)
