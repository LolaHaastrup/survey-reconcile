# Changelog

All notable changes to Survey Reconcile are recorded here. The project follows
[Semantic Versioning](https://semver.org/).

## [0.3.0] - 2026-09-15

### Added

- Configurable status-first reconciliation of duplicate parent submissions.
- Identifier normalisation with preservation of original values.
- Repeat-group reconciliation for retained, superseded, and missing parents.
- Non-destructive age, duplicate-member, and household-size quality checks.
- CSV audit outputs and a JSON run summary.
- A complete worked example with committed expected-output snapshots.
- Automated tests across Python 3.10, 3.11, and 3.12.
- Explicit validation for duplicate submission IDs, missing columns, blank
  identifiers, unknown statuses, and malformed timestamps.

### Known limitations

- Inputs and outputs are currently CSV only.
- Timestamp values must use ISO 8601 syntax.
- Reconciliation uses deterministic exact matching after configured identifier
  normalisation; it does not perform probabilistic record linkage.
- One parent file and explicitly named repeat-group files are processed per run.

[0.3.0]: https://github.com/LolaHaastrup/survey-reconcile/releases/tag/v0.3.0
