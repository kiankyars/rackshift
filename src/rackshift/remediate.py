from __future__ import annotations

from rackshift.models import Remediation, ValidationReport
from rackshift.units import WATTS_PER_KILOWATT, format_kw


def remediations(report: ValidationReport) -> list[Remediation]:
    if report.valid:
        return []
    spec = report.spec
    design = report.design
    reduced = design.usable_power_budget_w // spec.rack_power_w
    if reduced < 1:
        raise ValueError("budget cannot host a single rack at the new spec")
    # Keep the original 50 kW headroom shape: 8×100 kW sat in 850 kW.
    upgraded_budget_w = spec.rack_power_w * design.rack_count + 50 * WATTS_PER_KILOWATT
    return [
        Remediation(
            id="reduce-racks",
            title="Reduce deployment",
            summary=(
                f"Cut the row from {design.rack_count} to {reduced} racks "
                f"({reduced} × {format_kw(spec.rack_power_w)} = {format_kw(reduced * spec.rack_power_w)}). "
                "Valid against the current feed. Compute capacity drops."
            ),
            rack_count=reduced,
            usable_power_budget_w=design.usable_power_budget_w,
            compute_capacity_racks=reduced,
            requires_electrical_change=False,
        ),
        Remediation(
            id="upgrade-feed",
            title="Upgrade usable feed",
            summary=(
                f"Keep {design.rack_count} racks and raise the usable budget to "
                f"{format_kw(upgraded_budget_w)}. Valid, but it is an electrical-plan change."
            ),
            rack_count=design.rack_count,
            usable_power_budget_w=upgraded_budget_w,
            compute_capacity_racks=design.rack_count,
            requires_electrical_change=True,
        ),
    ]
