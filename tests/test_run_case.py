"""Fast checks that need no solver licence.

Run from the repository root:  pytest tests/
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import run_case  # noqa: E402


def test_smoke_case_is_listed():
    assert "_smoke" in run_case.list_cases()


def test_case_settings_fill_defaults():
    settings = run_case.load_case_settings(run_case.CASES_DIR / "_smoke")
    assert settings["objective"] == "cost"
    assert set(settings) == set(run_case.DEFAULT_SETTINGS)


def test_unknown_case_setting_is_rejected(tmp_path):
    (tmp_path / "case.yaml").write_text("objectiv: cost\n")  # typo on purpose
    with pytest.raises(ValueError, match="Unknown keys"):
        run_case.load_case_settings(tmp_path)


def test_smoke_case_parses_and_builds():
    """ehubx is installed and the smoke case is a valid model (no solve)."""
    pytest.importorskip("ehubx")
    assert run_case.run_case("_smoke", inspect_only=True) is None
