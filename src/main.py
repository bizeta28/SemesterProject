"""Run one ehubx case: the only command-line entry point of this project.

Usage (from the repository root):

    python src/main.py <case_name>            # e.g. python src/main.py 1_WH
    python src/main.py <case_name> --inspect  # parse + build only, no solve
    python src/main.py --list                 # list available cases

A case is a folder ``cases/<case_name>/`` that contains

    inputs/basic|network|renewables   the ehubx model (layout fixed by ehubx)
    case.yaml                         run settings for this case (see below)

Every run writes to a fresh, timestamped folder

    cases/<case_name>/results/<YYYY-MM-DD_HH-MM-SS>/

so ehubx never asks whether to overwrite an existing results folder.
Next to the ehubx outputs it saves ``run_metadata.json`` (ehubx commit,
Python and Gurobi versions, the case settings used), so every number can be
traced back to the exact code that produced it.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "cases"

# Defaults used when case.yaml does not set a value.
DEFAULT_SETTINGS: dict = {
    "description": "",
    "objective": "cost",  # cost | co2 (ehubx ObjectiveType)
    "file_granularity": "default",  # min | default | max (ehubx FileGranularity)
    "solver": "gurobi",  # gurobi | glpk (GLPK is free but far slower)
    "write_lp": False,  # writing the LP file is slow for 8760 h models
    "solver_options": {},  # passed 1:1 to the solver, e.g. {MIPGap: 0.001}
}


def list_cases() -> list[str]:
    """Return the names of all folders in cases/ that contain an inputs/ folder."""
    if not CASES_DIR.is_dir():
        return []
    return sorted(p.name for p in CASES_DIR.iterdir() if (p / "inputs").is_dir())


def load_case_settings(case_dir: Path) -> dict:
    """Read case.yaml (optional) and fill in defaults for missing keys."""
    settings = dict(DEFAULT_SETTINGS)
    case_file = case_dir / "case.yaml"
    if case_file.is_file():
        with case_file.open(encoding="utf-8") as f:
            user_settings = yaml.safe_load(f) or {}
        unknown = set(user_settings) - set(DEFAULT_SETTINGS)
        if unknown:
            raise ValueError(f"Unknown keys in {case_file}: {sorted(unknown)}")
        settings.update(user_settings)
    return settings


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


def write_metadata(results_dir: Path, case_name: str, settings: dict) -> None:
    metadata = {
        "case": case_name,
        "finished": datetime.now().isoformat(timespec="seconds"),
        "ehubx_commit": ehubx_commit(),
        "python": platform.python_version(),
        "gurobi": gurobi_version(),
        "settings": settings,
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    with (results_dir / "run_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def run_case(case_name: str, inspect_only: bool = False) -> Path | None:
    """Parse, build and (unless inspect_only) solve one case.

    Returns the results folder, or None for an inspect-only run.
    """
    from ehubx import EhubX, FileGranularity, Glpk, Gurobi, ObjectiveType

    case_dir = CASES_DIR / case_name
    if not (case_dir / "inputs").is_dir():
        raise FileNotFoundError(
            f"No case '{case_name}' (expected {case_dir / 'inputs'}). "
            f"Available: {list_cases() or 'none'}"
        )
    settings = load_case_settings(case_dir)

    # Steps follow the ehubx docs, "The main file".
    hub = EhubX()
    hub.model_dir_path = str(case_dir)
    hub.parse()
    hub.build()
    if inspect_only:
        print(f"[{case_name}] parsed and built successfully (no solve).")
        return None

    solvers = {"gurobi": Gurobi, "glpk": Glpk}
    solver = solvers[settings["solver"].lower()]()
    for key, value in settings["solver_options"].items():
        solver.set_option_by_key(key, value)
    hub.set_solver(solver)

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_rel = Path("results") / stamp  # relative to the case folder
    results_dir = case_dir / results_rel

    # ehubx creates results_dir itself (it must not exist yet), so the
    # metadata is written after solving.
    hub.solve_single_obj(
        obj_type=ObjectiveType[settings["objective"].upper()],
        file_granularity=FileGranularity[settings["file_granularity"].upper()],
        write_model=settings["write_lp"],
        results_dir_path=str(results_rel),
    )
    write_metadata(results_dir, case_name, settings)
    print(f"[{case_name}] results written to {results_dir}")
    return results_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("case", nargs="?", help="case folder name under cases/")
    parser.add_argument("--inspect", action="store_true", help="parse and build only")
    parser.add_argument("--list", action="store_true", help="list available cases")
    args = parser.parse_args(argv)

    if args.list or not args.case:
        cases = list_cases()
        print("Available cases:", ", ".join(cases) if cases else "none yet")
        return 0
    run_case(args.case, inspect_only=args.inspect)
    return 0


if __name__ == "__main__":
    sys.exit(main())
