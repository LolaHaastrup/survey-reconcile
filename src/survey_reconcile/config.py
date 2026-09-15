from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigurationError


@dataclass(frozen=True)
class ParentConfig:
    id_column: str
    entity_key: str
    status_column: str
    timestamp_column: str


@dataclass(frozen=True)
class IdentifierConfig:
    uppercase: bool = True
    remove_spaces: bool = True
    remove_characters: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepeatConfig:
    parent_column: str
    record_id_column: str


@dataclass(frozen=True)
class QualityConfig:
    household_size_column: str | None = None
    member_age_column: str | None = None
    minimum_age: int = 0
    maximum_age: int = 120
    severity: dict[str, str] | None = None


@dataclass(frozen=True)
class Config:
    parent: ParentConfig
    status_priority: dict[str, int]
    identifiers: IdentifierConfig
    repeat_groups: dict[str, RepeatConfig]
    keep_orphan_repeats: bool = False
    quality: QualityConfig = QualityConfig()


def _required(mapping: dict[str, Any], key: str, section: str) -> Any:
    if key not in mapping or mapping[key] in (None, ""):
        raise ConfigurationError(f"Missing '{key}' in '{section}' configuration")
    return mapping[key]


def load_config(path: str | Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    parent_raw = _required(raw, "parent", "root")
    priorities = _required(raw, "status_priority", "root")
    repeats_raw = _required(raw, "repeat_groups", "root")
    if not isinstance(priorities, dict) or not priorities:
        raise ConfigurationError("'status_priority' must be a non-empty mapping")

    parent = ParentConfig(
        id_column=_required(parent_raw, "id_column", "parent"),
        entity_key=_required(parent_raw, "entity_key", "parent"),
        status_column=_required(parent_raw, "status_column", "parent"),
        timestamp_column=_required(parent_raw, "timestamp_column", "parent"),
    )
    identifier_raw = raw.get("identifiers", {})
    identifiers = IdentifierConfig(
        uppercase=bool(identifier_raw.get("uppercase", True)),
        remove_spaces=bool(identifier_raw.get("remove_spaces", True)),
        remove_characters=tuple(identifier_raw.get("remove_characters", [])),
    )
    repeats = {
        name: RepeatConfig(
            parent_column=_required(value, "parent_column", f"repeat_groups.{name}"),
            record_id_column=_required(value, "record_id_column", f"repeat_groups.{name}"),
        )
        for name, value in repeats_raw.items()
    }
    quality_raw = raw.get("quality", {})
    quality = QualityConfig(
        household_size_column=quality_raw.get("household_size_column"),
        member_age_column=quality_raw.get("member_age_column"),
        minimum_age=int(quality_raw.get("minimum_age", 0)),
        maximum_age=int(quality_raw.get("maximum_age", 120)),
        severity={str(k): str(v) for k, v in quality_raw.get("severity", {}).items()},
    )
    if quality.minimum_age > quality.maximum_age:
        raise ConfigurationError("quality.minimum_age cannot exceed maximum_age")
    return Config(
        parent=parent,
        status_priority={str(k).lower(): int(v) for k, v in priorities.items()},
        identifiers=identifiers,
        repeat_groups=repeats,
        keep_orphan_repeats=bool(
            raw.get("reconciliation", {}).get("keep_orphan_repeats", False)
        ),
        quality=quality,
    )
