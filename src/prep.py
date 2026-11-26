"""Turn files in data/raw/ into ehubx-format CSVs for the case folders.

Empty on purpose: functions are added here as each raw dataset is migrated
(README, workflow step 4). Rules for every function in this module:

- read only from data/raw/, write only into cases/<case>/inputs/...;
- write the ehubx CSV layout (header rows, optional unit row, then values),
  see ehubx docs, "Input structure" > "csv files";
- temperatures in K (ehubx does not accept degC), units in the unit row.
"""
