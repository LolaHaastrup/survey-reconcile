import pytest

from survey_reconcile.config import Config, IdentifierConfig, ParentConfig
from survey_reconcile.exceptions import SchemaError
from survey_reconcile.reconciliation.duplicates import reconcile_parents


def _config():
    return Config(
        parent=ParentConfig("submission_id", "household_id", "review_status", "submitted_at"),
        status_priority={"approved": 3, "pending": 2, "rejected": 1},
        identifiers=IdentifierConfig(remove_characters=("-", "/")),
        repeat_groups={},
    )


def _row(submission_id, household_id, status, timestamp):
    return {
        "submission_id": submission_id,
        "household_id": household_id,
        "review_status": status,
        "submitted_at": timestamp,
    }


def test_status_priority_outranks_recency():
    rows = [
        _row("old-approved", "OSN-001", "approved", "2026-01-01T09:00:00"),
        _row("new-rejected", "osn 001", "rejected", "2026-02-01T09:00:00"),
    ]
    retained, excluded, _ = reconcile_parents(rows, _config())
    assert retained[0]["submission_id"] == "old-approved"
    assert excluded[0]["submission_id"] == "new-rejected"


def test_recency_breaks_tie_within_same_status():
    rows = [
        _row("older", "HH-1", "approved", "2026-01-01T09:00:00"),
        _row("newer", "HH-1", "approved", "2026-01-02T09:00:00"),
    ]
    retained, _, _ = reconcile_parents(rows, _config())
    assert retained[0]["submission_id"] == "newer"


def test_submission_id_breaks_exact_ranking_tie_deterministically():
    timestamp = "2026-01-01T09:00:00"
    rows = [
        _row("sub-a", "HH-1", "approved", timestamp),
        _row("sub-b", "HH-1", "approved", timestamp),
    ]
    retained, _, _ = reconcile_parents(rows, _config())
    assert retained[0]["submission_id"] == "sub-b"


def test_duplicate_submission_identifier_is_rejected():
    rows = [
        _row("same-id", "HH-1", "approved", "2026-01-01T09:00:00"),
        _row("same-id", "HH-2", "pending", "2026-01-02T09:00:00"),
    ]
    with pytest.raises(SchemaError, match="Duplicate parent submission identifier"):
        reconcile_parents(rows, _config())


@pytest.mark.parametrize(
    "row, message",
    [
        (_row("sub-1", "HH-1", "unreviewed", "2026-01-01T09:00:00"), "unknown status"),
        (_row("sub-1", "HH-1", "approved", "not-a-date"), "invalid ISO timestamp"),
        (_row("", "HH-1", "approved", "2026-01-01T09:00:00"), "cannot be empty"),
        (_row("sub-1", "", "approved", "2026-01-01T09:00:00"), "cannot be empty"),
    ],
)
def test_invalid_parent_values_are_rejected(row, message):
    with pytest.raises(SchemaError, match=message):
        reconcile_parents([row], _config())


def test_missing_parent_column_is_reported():
    row = _row("sub-1", "HH-1", "approved", "2026-01-01T09:00:00")
    del row["review_status"]
    with pytest.raises(SchemaError, match="missing columns"):
        reconcile_parents([row], _config())
