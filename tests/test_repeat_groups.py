from survey_reconcile.config import RepeatConfig
from survey_reconcile.reconciliation.repeat_groups import reconcile_repeats


REPEAT = RepeatConfig(parent_column="parent_id", record_id_column="member_id")


def _rows():
    return [
        {"member_id": "retained-child", "parent_id": "kept"},
        {"member_id": "superseded-child", "parent_id": "discarded"},
        {"member_id": "true-orphan", "parent_id": "unknown"},
    ]


def test_orphan_setting_does_not_rescue_child_of_known_parent():
    retained, excluded, audit = reconcile_repeats(
        _rows(), "members", REPEAT,
        all_parent_ids={"kept", "discarded"},
        retained_parent_ids={"kept"}, keep_orphans=True,
    )
    assert {row["member_id"] for row in retained} == {"retained-child", "true-orphan"}
    assert {row["member_id"] for row in excluded} == {"superseded-child"}
    reasons = {row["record_id"]: row["reason"] for row in audit}
    assert reasons["superseded-child"] == "parent_known_but_not_authoritative"
    assert reasons["true-orphan"] == "orphan_retained_by_configuration"


def test_true_orphan_is_excluded_when_setting_is_false():
    retained, excluded, _ = reconcile_repeats(
        _rows(), "members", REPEAT,
        all_parent_ids={"kept", "discarded"},
        retained_parent_ids={"kept"}, keep_orphans=False,
    )
    assert {row["member_id"] for row in retained} == {"retained-child"}
    assert {row["member_id"] for row in excluded} == {"superseded-child", "true-orphan"}
