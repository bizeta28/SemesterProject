# Edge data centres in buildings: waste heat and IT flexibility

Semester project (ETH Zürich, MSc Energy Science and Technology, hosted at
Empa UESL). An energy hub optimisation model, built with
[ehubX](https://github.com/uesl-empa/ehubx), of buildings with decentralised
(edge) data centres.

**Research question.** How much seasonal heat-demand flexibility can
coordinated data-centre waste-heat recovery unlock across a multi-building
portfolio, and how does it depend on the type of computational workload?

1. How do workload types differ in temporal profile, deferrability, and the
   amount and temperature of recoverable heat?
2. How much heat-demand flexibility does each workload type provide across
   seasons and demand profiles, and which provides the best fit?
3. How does the workload–demand match change the electrical load seen by the
   grid?

## Repository layout

```text
SemesterProject/
  cases/              one complete ehubx model per folder (see cases/README.md)
    <case>/inputs/    ehubx inputs: basic/ network/ renewables/
    <case>/case.yaml  run settings for that case
    <case>/results/   one timestamped folder per run (git-ignored)
  data/raw/           each input profile once, with provenance (data/README.md)
  src/
    run_case.py       the ONLY entry point
    prep.py           data/raw -> ehubx CSVs
    kpis.py           KPIs from a results folder
    plotting.py       figures from results
  tests/              fast checks, no solver licence needed
  notebooks/          exploration only; nothing the results depend on
  docs/
    formulation/      one spec per model change, approved before coding
    CHANGES.md        log of model changes and runs
    private/          local only, git-ignored
  results_examples/   the only tracked results (hand-picked for the report)
  environment.yml
```

## Setup

ehubX is installed from a local clone, not from PyPI, so the exact framework
version is a git commit. Keep the clone **next to** this repository, never
inside it.

```powershell
# 1. Environment
conda env create -f environment.yml      # creates "sp"
conda activate sp

# 2. ehubX framework (official repository, pinned commit)
git clone https://github.com/uesl-empa/ehubx C:\ehubx
cd C:\ehubx
git checkout d436c9b
poetry install                           # installs into the active "sp" env

# 3. Check
python -c "import ehubx; print(ehubx.__file__)"   # must point into C:\ehubx
```

Note: `pip install -e C:\ehubx` does **not** work, because ehubX's build
backend does not support editable installs. Use `poetry install`.

Pinned versions used for the results in this repository:

| Component | Version |
|---|---|
| ehubX | `uesl-empa/ehubx @ d436c9b` |
| Python | 3.12 |
| Gurobi | 11.0.0 (licence type: to confirm) |

Large models need a full Gurobi licence. The size-limited licence that ships
with `pip install gurobipy` is not enough for 8760-hour cases.

## Running

From the repository root:

```powershell
python src/run_case.py --list              # available cases
python src/run_case.py _smoke --inspect    # parse + build only (fast check)
python src/run_case.py _smoke              # full run
pytest tests/                              # fast checks
```

## Outputs

Each run writes to a fresh folder, so nothing is ever overwritten:

```text
cases/<case>/results/<YYYY-MM-DD_HH-MM-SS>/
  opt_vars.csv, import_export*.csv, ...   ehubX result files
  run_metadata.json                       ehubX commit, Python and Gurobi
                                          versions, case settings used
```

**Source of truth for reported numbers:** the ehubX result files of the run
named in the report, together with its `run_metadata.json`. Results used in
the report are copied to `results_examples/`.

## Workflow

1. Write or update the spec in `docs/formulation/` and get it approved.
2. Change inputs in a **new** case folder (reference cases are never edited).
3. Run, check against the reference numbers, log the result in `docs/CHANGES.md`.

## Scope

A semester-project implementation, not a general framework. It focuses on:

- ehubX cases of buildings with edge data centres and waste-heat recovery;
- workload-type IT flexibility and its effect on heat and electricity flows;
- KPIs and figures that answer the three research questions.

It deliberately avoids generating ehubX inputs from templates, a scenario
framework, and modifying the ehubX source.

## Licence

`cases/_smoke/` is an unmodified copy of the ehubX `small_demo` example
(GPL-3.0-or-later, Empa UESL).
