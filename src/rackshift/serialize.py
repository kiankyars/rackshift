from __future__ import annotations

from rackshift.models import Remediation, ValidationReport
from rackshift.units import format_kw


def report_to_dict(report: ValidationReport, options: list[Remediation] | None = None) -> dict:
    return {
        "valid": report.valid,
        "repo_root": str(report.repo_root),
        "spec": {
            "vendor": report.spec.vendor,
            "sku": report.spec.sku,
            "rack_power_w": report.spec.rack_power_w,
            "rack_power": format_kw(report.spec.rack_power_w),
            "revision": report.spec.revision,
            "effective_date": report.spec.effective_date,
            "source": report.spec.source,
        },
        "design": {
            "name": report.design.name,
            "rack_count": report.design.rack_count,
            "usable_power_budget_w": report.design.usable_power_budget_w,
            "usable_power_budget": format_kw(report.design.usable_power_budget_w),
        },
        "constraints": [
            {
                "name": item.name,
                "expression": f"{item.left_label} = {format_kw(item.demand_w)}",
                "budget": item.right_label,
                "demand_w": item.demand_w,
                "budget_w": item.budget_w,
                "delta_w": item.delta_w,
                "delta": format_kw(abs(item.delta_w)),
                "status": "VALID" if item.valid else "VIOLATION",
            }
            for item in report.constraints
        ],
        "remediations": [remediation_to_dict(item) for item in (options or [])],
    }


def remediation_to_dict(item: Remediation) -> dict:
    return {
        "id": item.id,
        "title": item.title,
        "summary": item.summary,
        "rack_count": item.rack_count,
        "usable_power_budget_w": item.usable_power_budget_w,
        "compute_capacity_racks": item.compute_capacity_racks,
        "requires_electrical_change": item.requires_electrical_change,
    }
