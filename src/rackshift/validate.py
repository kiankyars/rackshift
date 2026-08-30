from __future__ import annotations

from pathlib import Path

from rackshift.models import Constraint, RackSpec, SiteDesign, ValidationReport
from rackshift.store import load_design, load_spec, repo_root
from rackshift.units import format_kw


def validate(root: Path | None = None) -> ValidationReport:
    base = repo_root(root)
    spec = load_spec(base)
    design = load_design(base)
    return ValidationReport(
        spec=spec,
        design=design,
        constraints=(power_budget(spec, design),),
        repo_root=base,
    )


def power_budget(spec: RackSpec, design: SiteDesign) -> Constraint:
    demand_w = design.rack_count * spec.rack_power_w
    return Constraint(
        name="usable_power_budget",
        left_label=f"{design.rack_count} racks × {format_kw(spec.rack_power_w)}",
        right_label=f"usable feed {format_kw(design.usable_power_budget_w)}",
        demand_w=demand_w,
        budget_w=design.usable_power_budget_w,
    )
