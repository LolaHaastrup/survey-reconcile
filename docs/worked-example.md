# Worked reconciliation example

This example shows why keeping the newest survey submission is not always the
correct decision and why repeat rows must be reconciled after their parents.
Run it from the repository root with:

```bash
survey-reconcile run \
  --config examples/config.yaml \
  --households examples/households.csv \
  --repeat household_members=examples/household_members.csv \
  --output output
```

## Parent submissions

`sub-001` and `sub-002` appear to have different household identifiers, but
normalisation maps both `OSN-0012` and `osn 0012` to `OSN0012`. They therefore
compete to represent the same household.

| Submission | Status | Submitted | Normalised household | Decision |
|---|---|---|---|---|
| `sub-001` | approved | 10 Jan | `OSN0012` | retained |
| `sub-002` | rejected | 12 Jan | `OSN0012` | superseded by `sub-001` |
| `sub-003` | pending | 11 Jan | `OSN0013` | retained |

Although `sub-002` is newer, configured status priority is evaluated before
timestamp. The older approved submission therefore wins. Timestamp decides
only when two candidates have the same status priority, and submission ID is
the final deterministic tie-breaker.

## Repeat rows

Repeat rows link to immutable submission IDs, not to normalised household IDs.
This distinction produces three outcomes:

| Member rows | Parent | Outcome | Reason |
|---|---|---|---|
| `m-001`–`m-003` | retained `sub-001` | retained | authoritative parent |
| `m-004` | superseded `sub-002` | excluded | known but non-authoritative parent |
| `m-005` | absent parent | excluded | true orphan and orphan retention is off |
| `m-006` | retained `sub-003` | retained | authoritative parent |

Turning on `keep_orphan_repeats` would retain `m-005`, whose parent is absent
from the complete parent input. It would not retain `m-004`, because `sub-002`
is known and was deliberately superseded.

## Quality result

Quality checks run after reconciliation. `sub-003` reports a household size of
two but has only one retained member row, so `quality_issues.csv` records one
`household_size_mismatch` warning. The warning does not remove or silently
alter either record.

## Audit interpretation

`reconciliation_log.csv` separates the outcome from its cause. For example,
`m-004` has decision `excluded` and reason
`parent_known_but_not_authoritative`; no row was deleted merely because it was
old. The files in `examples/expected/` contain the complete expected result.
