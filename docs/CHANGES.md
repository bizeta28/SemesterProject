# Changes

One entry per model change or analysis session, newest first:
date · spec implemented (`docs/formulation/<file>.md`, or "no spec") · what changed · what was tested · open issues.

## 2026-11-27 · no spec · run settings in main.py, scenarios
- **Changed:** removed `case.yaml`; objective, solver and LP writing are now set
  in `src/main.py` as in the ehubX docs (LP writing on). Added `src/scenarios.py`
  (named changes applied after `parse()`), `--scenario` option, results folders
  named `<scenario>_<timestamp>`.
- **Tested:** `pytest tests/` (4 passed); `_smoke` base scenario solved end to end
  with GLPK.
- **Open issues:** the docs' `deactivate_*()` methods do not exist in ehubX @ d436c9b.

## 2026-11-26 · no spec · repository skeleton
- **Changed:** case-centric layout, `src/main.py` entry point, smoke case.
- **Tested:** `pytest tests/` (4 passed); `_smoke` solved end to end with GLPK.
- **Open issues:** no project cases migrated yet.
