from __future__ import annotations

from dataclasses import replace
from datetime import date

from rackshift.models import RackSpec, SiteDesign
from rackshift.remediate import remediations
from rackshift.store import load_design, load_spec, write_design, write_provenance, write_spec
from rackshift.validate import validate

VENDOR_REVISED_POWER_W = 112_000


def apply_vendor_revision(root=None, rack_power_w: int = VENDOR_REVISED_POWER_W) -> RackSpec:
    report = validate(root)
    spec = report.spec
    if spec.rack_power_w == rack_power_w:
        return spec
    updated = replace(
        spec,
        rack_power_w=rack_power_w,
        revision=spec.revision + 1,
        effective_date=date.today().isoformat(),
        source="vendor-revision-notice",
    )
    write_spec(report.repo_root, updated)
    write_provenance(
        report.repo_root,
        {
            "type": "vendor_revision",
            "from_w": spec.rack_power_w,
            "to_w": updated.rack_power_w,
            "revision": updated.revision,
            "effective_date": updated.effective_date,
        },
    )
    return updated


def apply_remediation(option_id: str, root=None) -> SiteDesign:
    report = validate(root)
    match = next((item for item in remediations(report) if item.id == option_id), None)
    if match is None:
        raise ValueError(f"unknown or inapplicable remediation {option_id!r}")
    current = load_design(report.repo_root)
    updated = replace(
        current,
        rack_count=match.rack_count,
        usable_power_budget_w=match.usable_power_budget_w,
    )
    write_design(report.repo_root, updated)
    write_provenance(
        report.repo_root,
        {
            "type": "remediation_applied",
            "option": option_id,
            "rack_count": updated.rack_count,
            "usable_power_budget_w": updated.usable_power_budget_w,
            "spec_revision": load_spec(report.repo_root).revision,
        },
    )
    return updated
