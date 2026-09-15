# Survey Reconcile

[![Tests](https://github.com/LolaHaastrup/survey-reconcile/actions/workflows/tests.yml/badge.svg)](https://github.com/LolaHaastrup/survey-reconcile/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Survey Reconcile is an offline Python tool for turning Kobo/ODK parent and
repeat-group exports into analysis-ready datasets. It resolves corrected or
duplicate submissions using explicit review priorities, reconnects child rows
to the retained parent, and writes an audit record for every decision.

## Why it exists

Survey data is rarely a simple flat file. Enumerators resubmit interviews,
reviewers reject later corrections, identifiers are typed inconsistently, and
repeat-group rows may point to submissions that are no longer authoritative.
Silently keeping the newest row can therefore discard the best available data.

## Quick start

```bash
python -m pip install -e ".[dev]"
survey-reconcile run \
  --config examples/config.yaml \
  --households examples/households.csv \
  --repeat household_members=examples/household_members.csv \
  --output output
pytest
```

The command writes retained and excluded parent/child CSVs, a reconciliation
log, a non-destructive quality-issues report, and a JSON run summary. The
example intentionally includes an approved older submission, a rejected newer
correction, orphaned repeat rows, and a household-size inconsistency.

## Reconciliation contract

1. Normalise the configured entity key for grouping only; original values are
   preserved.
2. Rank duplicate parents by configured status priority, then timestamp, then
   stable submission ID.
3. Retain one authoritative parent per normalised entity key.
4. Retain repeat rows only when they point directly to a retained submission.
5. `keep_orphan_repeats` applies only to children whose parent submission is
   absent from the complete parent input. It does not rescue children of a
   known but superseded or rejected parent.

This ordering is deliberate and is covered by integration tests.

## Data-quality checks

The initial rules flag invalid ages, duplicate retained member identifiers, and
differences between reported household size and retained member rows. Rules run
after reconciliation, so warnings describe the dataset that will actually be
analysed. See `docs/configuration.md` for configuration details.

## Worked example

The complete example inputs, decision sequence, expected outputs, and audit-log
interpretation are documented in [`docs/worked-example.md`](docs/worked-example.md).
The committed snapshots under `examples/expected/` are regenerated during the
test suite to keep the documentation aligned with the executable behaviour.

## Project status

Version 0.3.0 is an alpha release intended for reproducible local processing
of CSV exports. Review the audit and quality outputs before using reconciled
records for operational decisions. Contributions and reproducible bug reports
are welcome; see [`CONTRIBUTING.md`](CONTRIBUTING.md).
