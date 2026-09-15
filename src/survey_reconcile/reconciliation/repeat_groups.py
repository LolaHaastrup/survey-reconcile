from __future__ import annotations

from typing import Any

from ..config import RepeatConfig
from ..exceptions import SchemaError


def reconcile_repeats(
    rows: list[dict[str, str]],
    repeat_name: str,
    repeat_config: RepeatConfig,
    all_parent_ids: set[str],
    retained_parent_ids: set[str],
    keep_orphans: bool,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, Any]]]:
    retained: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []
    audit: list[dict[str, Any]] = []
    required = {repeat_config.parent_column, repeat_config.record_id_column}
    for row in rows:
        missing = required - row.keys()
        if missing:
            raise SchemaError(f"Repeat '{repeat_name}' is missing columns: {sorted(missing)}")
        record_id = row[repeat_config.record_id_column]
        parent_id = row[repeat_config.parent_column]
        if parent_id in retained_parent_ids:
            decision, reason = "retained", "parent_retained"
            retained.append(row)
        elif parent_id in all_parent_ids:
            decision, reason = "excluded", "parent_known_but_not_authoritative"
            excluded.append(row)
        elif keep_orphans:
            decision, reason = "retained", "orphan_retained_by_configuration"
            retained.append(row)
        else:
            decision, reason = "excluded", "parent_missing"
            excluded.append(row)
        audit.append({
            "record_type": repeat_name,
            "record_id": record_id,
            "decision": decision,
            "reason": reason,
            "parent_id": parent_id,
        })
    return retained, excluded, audit

