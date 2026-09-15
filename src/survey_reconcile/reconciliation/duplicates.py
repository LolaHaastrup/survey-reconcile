from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from ..config import Config
from ..exceptions import SchemaError
from .identifiers import normalise_identifier


def _parse_timestamp(value: str, submission_id: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise SchemaError(
            f"Submission '{submission_id}' has invalid ISO timestamp '{value}'"
        ) from exc


def reconcile_parents(
    rows: list[dict[str, str]], config: Config
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, Any]]]:
    required = {
        config.parent.id_column,
        config.parent.entity_key,
        config.parent.status_column,
        config.parent.timestamp_column,
    }
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        missing = required - row.keys()
        if missing:
            raise SchemaError(f"Parent input is missing columns: {sorted(missing)}")
        submission_id = row[config.parent.id_column]
        entity = normalise_identifier(row[config.parent.entity_key], config.identifiers)
        if not submission_id or not entity:
            raise SchemaError("Parent submission and entity identifiers cannot be empty")
        enriched = dict(row)
        enriched["_normalised_entity_key"] = entity
        groups[entity].append(enriched)

    retained: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []
    audit: list[dict[str, Any]] = []
    for entity, candidates in groups.items():
        def rank(row: dict[str, str]) -> tuple[int, datetime, str]:
            status = row[config.parent.status_column].lower()
            if status not in config.status_priority:
                raise SchemaError(
                    f"Submission '{row[config.parent.id_column]}' has unknown status '{status}'"
                )
            return (
                config.status_priority[status],
                _parse_timestamp(row[config.parent.timestamp_column], row[config.parent.id_column]),
                row[config.parent.id_column],
            )

        ordered = sorted(candidates, key=rank, reverse=True)
        winner = ordered[0]
        retained.append(winner)
        audit.append({
            "record_type": "parent",
            "record_id": winner[config.parent.id_column],
            "decision": "retained",
            "reason": "highest_status_then_latest_timestamp_then_submission_id",
            "entity_key": entity,
        })
        for loser in ordered[1:]:
            excluded.append(loser)
            audit.append({
                "record_type": "parent",
                "record_id": loser[config.parent.id_column],
                "decision": "excluded",
                "reason": f"superseded_by:{winner[config.parent.id_column]}",
                "entity_key": entity,
            })
    return retained, excluded, audit

