from __future__ import annotations

from collections import Counter
from typing import Any

from ..config import Config, RepeatConfig


def _issue(config: Config, rule: str, record_type: str, record_id: str,
           message: str, **context: Any) -> dict[str, Any]:
    defaults = {
        "household_size_mismatch": "warning",
        "invalid_member_age": "error",
        "duplicate_member_id": "error",
    }
    configured = config.quality.severity or {}
    return {
        "rule": rule,
        "severity": configured.get(rule, defaults[rule]),
        "record_type": record_type,
        "record_id": record_id,
        "message": message,
        **context,
    }


def check_member_ages(rows: list[dict[str, str]], repeat_name: str,
                       repeat_config: RepeatConfig,
                       config: Config) -> list[dict[str, Any]]:
    age_column = config.quality.member_age_column
    if not age_column:
        return []
    issues = []
    for row in rows:
        value = row.get(age_column, "")
        try:
            age = int(value)
            valid = config.quality.minimum_age <= age <= config.quality.maximum_age
        except (TypeError, ValueError):
            valid = False
        if not valid:
            record_id = row.get(repeat_config.record_id_column, "")
            issues.append(_issue(
                config, "invalid_member_age", repeat_name, record_id,
                f"Age '{value}' is not between {config.quality.minimum_age} and {config.quality.maximum_age}",
                observed_value=value,
            ))
    return issues


def check_duplicate_member_ids(rows: list[dict[str, str]], repeat_name: str,
                               repeat_config: RepeatConfig,
                               config: Config) -> list[dict[str, Any]]:
    id_column = repeat_config.record_id_column
    counts = Counter(row.get(id_column, "") for row in rows)
    return [
        _issue(config, "duplicate_member_id", repeat_name, member_id,
               f"Member identifier occurs {count} times in retained data",
               observed_value=count)
        for member_id, count in sorted(counts.items())
        if member_id and count > 1
    ]


def check_household_sizes(parents: list[dict[str, str]],
                          members: list[dict[str, str]], repeat_name: str,
                          repeat_config: RepeatConfig,
                          config: Config) -> list[dict[str, Any]]:
    size_column = config.quality.household_size_column
    if not size_column:
        return []
    child_counts = Counter(row.get(repeat_config.parent_column, "") for row in members)
    issues = []
    for parent in parents:
        parent_id = parent[config.parent.id_column]
        reported = parent.get(size_column, "")
        try:
            expected = int(reported)
        except (TypeError, ValueError):
            continue
        observed = child_counts[parent_id]
        if expected != observed:
            issues.append(_issue(
                config, "household_size_mismatch", "parent", parent_id,
                f"Reported household size is {expected}, but {observed} retained member rows were found",
                expected_value=expected, observed_value=observed,
                repeat_group=repeat_name,
            ))
    return issues


def run_quality_checks(parents: list[dict[str, str]],
                       retained_repeats: dict[str, list[dict[str, str]]],
                       config: Config) -> list[dict[str, Any]]:
    issues = []
    for name, rows in retained_repeats.items():
        repeat_config = config.repeat_groups[name]
        issues.extend(check_member_ages(rows, name, repeat_config, config))
        issues.extend(check_duplicate_member_ids(rows, name, repeat_config, config))
        issues.extend(check_household_sizes(parents, rows, name, repeat_config, config))
    return issues
