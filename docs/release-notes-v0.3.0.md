# Survey Reconcile v0.3.0

This first alpha release provides an auditable offline pipeline for reconciling
Kobo/ODK-style parent submissions and repeat-group records.

The pipeline normalises configured entity identifiers, selects one authoritative
parent using status priority before timestamp, reconciles child rows against
the resulting parent set, and produces both decision-level audit records and
non-destructive quality warnings. The included worked example demonstrates why
an older approved submission can outrank a newer rejected correction and why
orphan retention does not rescue children of known superseded parents.

Automated tests cover Python 3.10, 3.11, and 3.12. This alpha release processes
CSV inputs and uses deterministic exact matching after normalisation. It is not
a probabilistic record-linkage system and its outputs should be reviewed before
operational use.
