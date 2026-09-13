import csv
import json
from pathlib import Path

from survey_reconcile.pipeline import run_pipeline


PROJECT = Path(__file__).parents[1]


def _read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_end_to_end_reconciliation(tmp_path):
    summary = run_pipeline(
        PROJECT / "examples/config.yaml",
        PROJECT / "examples/households.csv",
        {"household_members": PROJECT / "examples/household_members.csv"},
        tmp_path,
    )

    assert summary == {
        "input_parents": 3,
        "retained_parents": 2,
        "excluded_parents": 1,
        "retained_repeat_rows": 4,
        "excluded_repeat_rows": 2,
        "quality_issues": 1,
    }
    households = _read_csv(tmp_path / "clean_households.csv")
    assert {row["submission_id"] for row in households} == {"sub-001", "sub-003"}
    members = _read_csv(tmp_path / "clean_household_members.csv")
    assert {row["member_id"] for row in members} == {"m-001", "m-002", "m-003", "m-006"}
    excluded = _read_csv(tmp_path / "excluded_household_members.csv")
    assert {row["member_id"] for row in excluded} == {"m-004", "m-005"}
    issues = _read_csv(tmp_path / "quality_issues.csv")
    assert [(row["rule"], row["record_id"]) for row in issues] == [
        ("household_size_mismatch", "sub-003")
    ]
    assert json.loads((tmp_path / "run_summary.json").read_text()) == summary


def test_orphan_setting_does_not_rescue_child_of_superseded_parent(tmp_path):
    config = (PROJECT / "examples/config.yaml").read_text().replace(
        "keep_orphan_repeats: false", "keep_orphan_repeats: true"
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config)

    run_pipeline(
        config_path,
        PROJECT / "examples/households.csv",
        {"household_members": PROJECT / "examples/household_members.csv"},
        tmp_path / "output",
    )
    retained = _read_csv(tmp_path / "output/clean_household_members.csv")
    retained_ids = {row["member_id"] for row in retained}
    assert "m-005" in retained_ids
    assert "m-004" not in retained_ids
