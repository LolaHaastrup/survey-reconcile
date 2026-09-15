from __future__ import annotations

from pathlib import Path

from .config import load_config
from .io import read_csv, write_csv, write_json
from .quality.rules import run_quality_checks
from .reconciliation.duplicates import reconcile_parents
from .reconciliation.repeat_groups import reconcile_repeats


def run_pipeline(
    config_path: str | Path,
    household_path: str | Path,
    repeat_paths: dict[str, str | Path],
    output_dir: str | Path,
) -> dict[str, int]:
    config = load_config(config_path)
    parents = read_csv(household_path)
    clean_parents, excluded_parents, audit = reconcile_parents(parents, config)
    all_parent_ids = {row[config.parent.id_column] for row in parents}
    retained_parent_ids = {row[config.parent.id_column] for row in clean_parents}
    output = Path(output_dir)

    write_csv(output / "clean_households.csv", clean_parents)
    write_csv(output / "excluded_households.csv", excluded_parents)

    clean_repeat_count = 0
    excluded_repeat_count = 0
    retained_repeats: dict[str, list[dict[str, str]]] = {}
    for name, path in repeat_paths.items():
        if name not in config.repeat_groups:
            raise ValueError(f"Repeat group '{name}' is not configured")
        rows = read_csv(path)
        clean, excluded, repeat_audit = reconcile_repeats(
            rows,
            name,
            config.repeat_groups[name],
            all_parent_ids,
            retained_parent_ids,
            config.keep_orphan_repeats,
        )
        write_csv(output / f"clean_{name}.csv", clean)
        write_csv(output / f"excluded_{name}.csv", excluded)
        retained_repeats[name] = clean
        audit.extend(repeat_audit)
        clean_repeat_count += len(clean)
        excluded_repeat_count += len(excluded)

    quality_issues = run_quality_checks(clean_parents, retained_repeats, config)
    summary = {
        "input_parents": len(parents),
        "retained_parents": len(clean_parents),
        "excluded_parents": len(excluded_parents),
        "retained_repeat_rows": clean_repeat_count,
        "excluded_repeat_rows": excluded_repeat_count,
        "quality_issues": len(quality_issues),
    }
    write_csv(output / "reconciliation_log.csv", audit)
    write_csv(output / "quality_issues.csv", quality_issues)
    write_json(output / "run_summary.json", summary)
    return summary
