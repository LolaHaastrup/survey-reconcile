from survey_reconcile.config import Config, IdentifierConfig, ParentConfig, QualityConfig, RepeatConfig
from survey_reconcile.quality.rules import check_duplicate_member_ids, check_member_ages


def _config():
    return Config(
        parent=ParentConfig("submission_id", "household_id", "status", "timestamp"),
        status_priority={"approved": 1},
        identifiers=IdentifierConfig(),
        repeat_groups={"members": RepeatConfig("parent_id", "member_id")},
        quality=QualityConfig(member_age_column="age", minimum_age=0, maximum_age=120),
    )


def test_invalid_age_is_flagged_without_removing_record():
    rows = [{"member_id": "m-1", "parent_id": "p-1", "age": "145"}]
    issues = check_member_ages(rows, "members", _config().repeat_groups["members"], _config())
    assert len(issues) == 1
    assert issues[0]["rule"] == "invalid_member_age"
    assert rows[0]["age"] == "145"


def test_duplicate_member_identifier_is_reported_once():
    rows = [
        {"member_id": "m-1", "parent_id": "p-1", "age": "20"},
        {"member_id": "m-1", "parent_id": "p-1", "age": "21"},
    ]
    issues = check_duplicate_member_ids(
        rows, "members", _config().repeat_groups["members"], _config()
    )
    assert len(issues) == 1
    assert issues[0]["observed_value"] == 2
