# Contributing

Thank you for helping improve Survey Reconcile. Contributions should keep
reconciliation decisions deterministic, auditable, and reproducible offline.

## Development setup

```bash
git clone https://github.com/LolaHaastrup/survey-reconcile.git
cd survey-reconcile
python -m venv .venv
```

Activate the environment, then install the package and development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -q
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. On macOS or
Linux, use `source .venv/bin/activate`.

## Proposing a change

1. Open an issue describing the data condition and expected behaviour.
2. Create a focused branch from `main`.
3. Add a test that would fail without the proposed change.
4. Update documentation when configuration or output behaviour changes.
5. Run the complete test suite before opening a pull request.

Tests should distinguish competing explanations rather than merely repeat an
implementation detail. Never add real respondent data, direct identifiers, or
credentials. Use small fictional fixtures that demonstrate the relevant edge
case.

## Pull-request checklist

- [ ] Behaviour is documented in plain language.
- [ ] New or changed behaviour has focused tests.
- [ ] Audit reasons remain stable or the change is documented.
- [ ] Example data contains no personal or confidential information.
- [ ] `pytest -q` passes locally.
