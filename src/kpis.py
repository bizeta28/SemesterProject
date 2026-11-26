"""KPIs computed from a results folder cases/<case>/results/<timestamp>/.

Empty on purpose: the energy reuse factor (ERF) and the other KPIs are added
here, one function per KPI, each citing the definition in
docs/formulation/kpis.md. Functions take a results folder path and return
numbers or DataFrames. They never re-run or modify the model.
"""
