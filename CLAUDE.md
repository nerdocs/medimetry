# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`medimetry` is a pure-Python library of reference implementations of published clinical formulas and scores (renal, cardiovascular, anthropometric, metabolic, neuro, pulmonary, cardiac, electrolytes). Single runtime dependency: `labunits`. CDC 2000 growth tables are bundled under `src/medimetry/data/cdc/`.

**Not a medical device** — see `DISCLAIMER.md`. Functions return only what the cited publication defines (value, category); never add interpretive or recommendation text to outputs.

Python ≥ 3.11. `src/`-layout package. MIT licensed.

## Commands

Tests and checks are orchestrated by `tox` against py311/py312/py313/pypy311:

```bash
tox                             # full matrix (lint + all python versions + coverage)
tox -e py313                    # single env
tox -e check                    # pre-commit + check-manifest only
tox -e py313 -- pytest -k foo   # forward args to pytest (e.g. filter tests)
tox -p auto                     # run envs in parallel
PYTEST_ADDOPTS=--cov-append tox # combine coverage across envs
```

Direct pytest (requires editable install or `PYTHONPATH=src`):

```bash
pytest tests/test_renal.py::test_name   # single test
pytest --no-cov                         # disable coverage for speed
```

Lint/format via `ruff` (configured in `pyproject.toml`, line-length 140, double quotes, `force-single-line=true` imports). Pre-commit runs ruff + taplo + whitespace fixers:

```bash
pre-commit install --install-hooks
pre-commit run --all-files
```

Version bumps go through `tbump` (updates `pyproject.toml` and `src/medimetry/__init__.py`, checks `CHANGELOG.md` contains the new version, tags as `v{X.Y.Z}`).

WHO anthropometric reference tables are refreshed via `python scripts/update_tables.py` (downloads XLSX from `cdn.who.int`, converts to CSV into `src/medimetry/data/anthropometric/`). Needs `pandas` + `openpyxl` + `requests`.

## Test configuration — non-obvious

`pytest.ini` enables three things that surprise people:

1. `--doctest-modules` — every docstring in `src/medimetry/` is executed as a doctest. Examples in docstrings must be runnable.
2. `--doctest-glob=*.md` — `README.md`, `CHANGELOG.md`, etc. are parsed for doctests. Code blocks in Markdown that look like a `>>>` session will be run.
3. `filterwarnings = error` — any warning (Deprecation included) fails the suite. When adding a deprecation, use explicit `warnings.warn(..., DeprecationWarning, stacklevel=2)` guarded by the caller, not module-level.

## Architecture

Flat domain-module layout — there is no class hierarchy, no plugin system, no registry. Each module under `src/medimetry/` exposes free functions for one clinical domain:

- `renal.py` — ACR (mg/g), Cockcroft-Gault, MDRD, CKD-EPI (2021, with/without cystatin C), KDIGO staging (`ckd_stage` returns `(GFR category, albuminuria category, KDIGO risk category 1-4)` using `kdigo_risk_matrix`)
- `cardiovasc.py` — MAP, CHA₂DS₂-VASc, Framingham General CVD 2008
- `anthropometric.py` — BMI, BSA (multiple formulas via `BSAFormula` enum)
- `growth.py` — pediatric growth charts: LMS z-score/percentile, `GrowthReference.CDC | WHO`, `GrowthIndicator`, `download_who_tables()`; see `docs/growth.md`
- `cardiac.py` — QTc (Bazett/Fridericia/Framingham/Hodges via `QtcCorrectionType`)
- `neuro.py` — GCS (raises if a component is NOT_TESTABLE)
- `pulmonary.py` — Simplified and Revised Geneva, PERC
- `metabolic.py` — Child-Pugh
- `lytes.py` — calcium correction
- `converters.py` — date-of-birth → age helpers (`dob2age`, `dob2age_tuple`)
- `constants.py` — shared enums (`Gender`, `EthnicalRace`, `QtcCorrectionType`). Re-exported from package root (`from medimetry import Gender`).

Cross-cutting conventions:

- All public functions are fully type-annotated and validate inputs with `assert` for programmer errors and `raise ValueError` for runtime/domain errors. The distinction is intentional — don't replace `assert` with `raise` or vice versa without reason.
- `Gender` (enum) is always passed as the enum, never as a string. Functions check `isinstance(x, Gender)`.
- User-visible strings are wrapped with `gettext` (`_(...)`) for i18n, even though no translations are shipped yet. Enum values are plain identifiers; translated titles live in `*_titles` dicts next to the enum.
- Every public function docstring has a `References:` block citing the primary publication.
- Growth-table data policy: CDC 2000 tables are bundled (`data/cdc/`, regenerate with `scripts/update_cdc_tables.py`). **WHO tables are never committed** (CC BY-NC-SA license); users download them with `download_who_tables()`. Both use the canonical `key;L;M;S` CSV layout.
- Units are documented per-arg in docstrings (e.g. creatinine always mg/dl, GFR always ml/min/1.73m²).

## Project-specific rules

- **English only** in code, docstrings, comments, and any i18n source strings. (Translations can then target any language.)
- Pure-Python project; `labunits` is the only runtime dependency. Do not add further `dependencies` in `pyproject.toml` without strong justification — dev/test tools go under `[dependency-groups]`.
- Results from this library carry a disclaimer (see `README.md`): they are not a basis for clinical decision-making. Keep that tone in new docstrings.
- CI tests on py311/py312/py313/pypy311 — avoid syntax or stdlib features newer than 3.11.
