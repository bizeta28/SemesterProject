"""Fast checks that need no solver licence.

Run from the repository root:  pytest tests/
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import main  # noqa: E402
from scenarios import SCENARIOS  # noqa: E402


def test_smoke_case_is_listed():
    assert "_smoke" in main.list_cases()


def test_every_scenario_has_label_and_apply():
    assert "base" in SCENARIOS
    for name, scenario in SCENARIOS.items():
        assert scenario["label"], f"scenario {name} has no label"
        assert callable(scenario["apply"]), f"scenario {name} has no apply()"


def test_unknown_scenario_is_rejected():
    with pytest.raises(ValueError, match="Unknown scenario"):
        main.run_case("_smoke", scenario="does_not_exist", inspect_only=True)


def test_smoke_case_parses_and_builds():
    """ehubx is installed and the smoke case is a valid model (no solve)."""
    assert main.run_case("_smoke", inspect_only=True) is None
