"""Scenarios: named changes applied to a case after parse(), before build().

A scenario holds ONLY what differs from the case's YAML inputs. Everything
else (costs, efficiencies, profiles) stays in the YAML, the one place ehubx
reads it. Run one with

    python src/main.py <case_name> --scenario <name>

Each entry has
    label   one line saying what the scenario changes (saved in run_metadata.json)
    apply   function taking the parsed EhubX object and changing its data

How to change data: ehubx docs, "The main file" > "Modifying model data
through code". Every input parameter x has getters/setters get_x / set_x on
hub.energy_system, e.g.

    from ehubx.data import stage_data, hub_data, ec_data, time_data, value

    def _cap_import(hub):
        hub.energy_system.imports.set_max(
            stage_data.StageId("S1"), hub_data.HubId("H1"),
            ec_data.EcId("E1"), time_data.TimeId(2),
            value.Value.from_str("500kW"),
        )

Note: the docs also describe hub.energy_system.deactivate_*() methods. They
do not exist in the ehubx version pinned in the README (d436c9b), so do not
rely on them without checking the source first.
"""

from __future__ import annotations

from typing import Callable, TypedDict

from ehubx import EhubX


class Scenario(TypedDict):
    label: str
    apply: Callable[[EhubX], None]


def _no_change(hub: EhubX) -> None:
    """Base scenario: run the inputs exactly as written."""


SCENARIOS: dict[str, Scenario] = {
    "base": {
        "label": "Inputs exactly as written in the case folder",
        "apply": _no_change,
    },
}
