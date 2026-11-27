"""Run one ehubx case: the only command-line entry point of this project.

Usage (from the repository root):

    python src/main.py <case_name>                      # base scenario
    python src/main.py <case_name> --scenario <name>    # see src/scenarios.py
    python src/main.py <case_name> --inspect            # parse + build only
    python src/main.py --list                           # cases and scenarios

A case is a folder ``cases/<case_name>/inputs/basic|network|renewables``
(layout fixed by ehubx). The run follows the ehubx docs, "The main file":
create EhubX -> set model path -> parse -> [apply scenario] -> build ->
set solver -> solve.

Every run writes to a fresh folder

    cases/<case_name>/results/<scenario>_<YYYY-MM-DD_HH-MM-SS>/

so ehubx never asks whether to overwrite an existing results folder.
Next to the ehubx outputs it saves ``run_metadata.json`` (ehubx commit,
Python and Gurobi versions, scenario and run settings), so every number can
be traced back to the exact code that produced it.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from ehubx import EhubX, FileGranularity, Gurobi, ObjectiveType

from scenarios import SCENARIOS

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "cases"

# --------------------------------------------------------------------------- #
# Run settings. As in the ehubx docs, they live here in the main file, in      #
# Python, and apply to every case. Model parameters (costs, efficiencies,     #
# capacities) do NOT belong here: they live in the case's YAML inputs.        #
# --------------------------------------------------------------------------- #
OBJECTIVE = ObjectiveType.COST  # docs: "Solving a single-objective model"
FILE_GRANULARITY = FileGranularity.DEFAULT  # MIN | DEFAULT | MAX
WRITE_LP = True  # LP file written to cases/<case>/ (git-ignored)


def make_solver() -> Gurobi:
    """Solver and its options (docs: "Specifying the solver").

    Add options with the solver's setters, e.g. solver.set_mip_gap(0.001),
    solver.set_time_limit(3600), or solver.set_option_by_key("Method", 0).
    """
    solver = Gurobi()
    return solver


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def list_cases() -> list[str]:
    """Return the names of all folders in cases/ that contain an inputs/ folder."""
    if not CASES_DIR.is_dir():
        return []
    return sorted(p.name for p in CASES_DIR.iterdir() if (p / "inputs").is_dir())


def ehubx_commit() -> str:
    """Git commit of the installed ehubx clone, or 'unknown' if not a git checkout."""
    import ehubx

    pkg_dir = Path(ehubx.__file__).resolve().parent
    try:
        out = subprocess.run(
            ["git", "-C", str(pkg_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        dirty = subprocess.run(
            ["git", "-C", str(pkg_dir), "status", "--porcelain", "--", "."],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return out.stdout.strip() + ("-dirty" if dirty else "")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def gurobi_version() -> str:
    try:
        import gurobipy

        return ".".join(str(v) for v in gurobipy.gurobi.version())
    except Exception:  # gurobipy missing or no licence
        return "unknown"


def write_metadata(results_dir: Path, case_name: str, scenario: str) -> None:
    metadata = {
        "case": case_name,
        "scenario": scenario,
        "scenario_label": SCENARIOS[scenario]["label"],
        "finished": datetime.now().isoformat(timespec="seconds"),
        "ehubx_commit": ehubx_commit(),
        "python": platform.python_version(),
        "gurobi": gurobi_version(),
        "objective": OBJECTIVE.name,
        "file_granularity": FILE_GRANULARITY.name,
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    with (results_dir / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


# --------------------------------------------------------------------------- #
# The run                                                                     #
# --------------------------------------------------------------------------- #
def run_case(
    case_name: str, scenario: str = "base", inspect_only: bool = False
) -> Path | None:
    """Parse, apply the scenario, build and (unless inspect_only) solve one case.

    Returns the results folder, or None for an inspect-only run.
    """
    case_dir = CASES_DIR / case_name
    if not (case_dir / "inputs").is_dir():
        raise FileNotFoundError(
            f"No case '{case_name}' (expected {case_dir / 'inputs'}). "
            f"Available: {list_cases() or 'none'}"
        )
    if scenario not in SCENARIOS:
        raise ValueError(
            f"Unknown scenario '{scenario}'. Choose one of {sorted(SCENARIOS)}"
        )

    # Step 0-1: create EhubX object, set model path, parse the input files
    hub = EhubX()
    hub.model_dir_path = str(case_dir)
    hub.parse()
    # Scenario: change parsed data before building (docs: "Modifying model
    # data through code")
    SCENARIOS[scenario]["apply"](hub)
    # Step 2: build the optimisation model
    hub.build()
    if inspect_only:
        print(f"[{case_name} / {scenario}] parsed and built successfully (no solve).")
        return None

    # Step 3: solver
    hub.set_solver(make_solver())

    # Step 4: solve into a fresh results folder (relative to the case folder)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_rel = Path("results") / f"{scenario}_{stamp}"
    results_dir = case_dir / results_rel
    # ehubx creates results_dir itself (it must not exist yet), so the
    # metadata is written after solving.
    hub.solve_single_obj(
        obj_type=OBJECTIVE,
        file_granularity=FILE_GRANULARITY,
        write_model=WRITE_LP,
        results_dir_path=str(results_rel),
    )
    write_metadata(results_dir, case_name, scenario)
    print(f"[{case_name} / {scenario}] results written to {results_dir}")
    return results_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("case", nargs="?", help="case folder name under cases/")
    parser.add_argument(
        "--scenario", default="base", help="scenario name from src/scenarios.py"
    )
    parser.add_argument("--inspect", action="store_true", help="parse and build only")
    parser.add_argument("--list", action="store_true", help="list cases and scenarios")
    args = parser.parse_args(argv)

    if args.list or not args.case:
        cases = list_cases()
        print("Cases:    ", ", ".join(cases) if cases else "none yet")
        print("Scenarios:", ", ".join(sorted(SCENARIOS)))
        return 0
    run_case(args.case, scenario=args.scenario, inspect_only=args.inspect)
    return 0


if __name__ == "__main__":
    sys.exit(main())
