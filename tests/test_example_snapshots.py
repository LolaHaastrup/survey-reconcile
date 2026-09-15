import csv
import json
from pathlib import Path

from survey_reconcile.pipeline import run_pipeline


PROJECT = Path(__file__).parents[1]
EXPECTED = PROJECT / "examples/expected"


def _csv_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_documented_example_matches_committed_snapshots(tmp_path):
    run_pipeline(
        PROJECT / "examples/config.yaml",
        PROJECT / "examples/households.csv",
        {"household_members": PROJECT / "examples/household_members.csv"},
        tmp_path,
    )

    csv_outputs = [
        "clean_households.csv",
        "excluded_households.csv",
        "clean_household_members.csv",
        "excluded_household_members.csv",
        "quality_issues.csv",
        "reconciliation_log.csv",
    ]
    for filename in csv_outputs:
        assert _csv_rows(tmp_path / filename) == _csv_rows(EXPECTED / filename)

    actual_summary = json.loads((tmp_path / "run_summary.json").read_text())
    expected_summary = json.loads((EXPECTED / "run_summary.json").read_text())
    assert actual_summary == expected_summary
