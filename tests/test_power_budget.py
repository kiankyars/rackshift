from pathlib import Path

import pytest

from rackshift.actions import apply_remediation, apply_vendor_revision
from rackshift.remediate import remediations
from rackshift.store import write_design, write_spec
from rackshift.units import watts_from_label
from rackshift.validate import validate
from rackshift.models import RackSpec, SiteDesign


def _seed(tmp_path: Path, rack_power_w: int = 100_000, racks: int = 8, budget_w: int = 850_000) -> Path:
    (tmp_path / "specs").mkdir()
    (tmp_path / "design").mkdir()
    write_spec(
        tmp_path,
        RackSpec(
            vendor="NVIDIA",
            sku="GB200 NVL72",
            rack_power_w=rack_power_w,
            revision=1,
            effective_date="2026-06-01",
            source="test",
        ),
    )
    write_design(tmp_path, SiteDesign(name="sf-row-a", rack_count=racks, usable_power_budget_w=budget_w))
    return tmp_path


def test_valid_eight_rack_row(tmp_path: Path) -> None:
    report = validate(_seed(tmp_path))
    assert report.valid
    assert report.constraints[0].demand_w == 800_000


def test_vendor_revision_breaks_budget(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    apply_vendor_revision(root)
    report = validate(root)
    assert not report.valid
    assert report.spec.rack_power_w == 112_000
    assert report.constraints[0].demand_w == 896_000
    assert report.constraints[0].delta_w == 46_000


def test_reduce_racks_restores_validity(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    apply_vendor_revision(root)
    apply_remediation("reduce-racks", root)
    report = validate(root)
    assert report.valid
    assert report.design.rack_count == 7
    assert report.constraints[0].demand_w == 784_000


def test_upgrade_feed_restores_validity(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    apply_vendor_revision(root)
    apply_remediation("upgrade-feed", root)
    report = validate(root)
    assert report.valid
    assert report.design.rack_count == 8
    assert report.design.usable_power_budget_w == 946_000


def test_remediations_only_when_invalid(tmp_path: Path) -> None:
    assert remediations(validate(_seed(tmp_path))) == []


@pytest.mark.parametrize(
    "raw, watts",
    [
        (100000, 100_000),
        ("100 kW", 100_000),
        ("112 kilowatts", 112_000),
        ("850000 W", 850_000),
        ("112kW", 112_000),
    ],
)
def test_unit_parsing(raw: object, watts: int) -> None:
    assert watts_from_label(raw) == watts


def test_rejects_mixed_fractional_kilowatts() -> None:
    with pytest.raises(ValueError):
        watts_from_label("1.5 kW")


def test_rejects_fractional_and_negative_rack_counts(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    (root / "design" / "site.yaml").write_text("site:\n  name: sf-row-a\n  rack_count: 7.9\n  usable_power_budget_w: 850000\n  unit: W\n")
    with pytest.raises(ValueError, match="rack_count"):
        validate(root)
    (root / "design" / "site.yaml").write_text("site:\n  name: sf-row-a\n  rack_count: -1\n  usable_power_budget_w: 850000\n  unit: W\n")
    with pytest.raises(ValueError, match="rack_count"):
        validate(root)


def test_rejects_contradictory_unit_metadata(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    (root / "specs" / "rack-source.json").write_text(
        '{"vendor":"NVIDIA","sku":"GB200 NVL72","rack_power_w":112,"unit":"kW","revision":1,"effective_date":"2026-06-01","source":"test"}\n'
    )
    with pytest.raises(ValueError, match="unit must be 'W'"):
        validate(root)


def test_revision_refuses_to_overwrite_newer_spec(tmp_path: Path) -> None:
    root = _seed(tmp_path, rack_power_w=120_000)
    with pytest.raises(ValueError, match="refusing to overwrite"):
        apply_vendor_revision(root)
