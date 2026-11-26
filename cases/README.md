# Cases

One folder per ehubx model. Each case is complete on its own and can be run
with `python src/main.py <case_name>`.

```text
cases/<case_name>/
  case.yaml        run settings (objective, solver, solver options); optional
  inputs/          ehubx model, layout fixed by ehubx
    basic/         stages, ecs, hubs, techs, imports, exports, demands (.yaml)
    network/       network_links.yaml, network_techs.yaml
    renewables/    solar_areas.csv, solar_irradiation.csv
  results/         one timestamped folder per run (git-ignored)
```

Rules:

- **Reference cases are never edited in place.** A model change gets a new
  case folder (or a switch in `case.yaml`) and a spec in `docs/formulation/`.
- **Profiles are not copied between cases.** ehubx resolves CSV paths relative
  to the YAML file, so a case can point to a shared file in `data/`.
- Case names say what is in the model, e.g. `1_WH`, `4_full`.

| Case | What it is | Status |
|---|---|---|
| `_smoke` | Unmodified ehubx `small_demo`; checks the installation | works |
