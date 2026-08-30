from __future__ import annotations

import json
from pathlib import Path

import yaml

from rackshift.models import RackSpec, SiteDesign
from rackshift.units import watts_from_label

SPEC_PATH = Path("specs/rack-source.json")
DESIGN_PATH = Path("design/site.yaml")
PROVENANCE_PATH = Path("specs/provenance.json")


def repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "design" / "site.yaml").exists() and (candidate / "specs" / "rack-source.json").exists():
            return candidate
    raise FileNotFoundError("not inside a RackShift repository")


def load_spec(root: Path) -> RackSpec:
    payload = json.loads((root / SPEC_PATH).read_text())
    return RackSpec(
        vendor=str(payload["vendor"]),
        sku=str(payload["sku"]),
        rack_power_w=watts_from_label(payload["rack_power_w"]),
        revision=int(payload["revision"]),
        effective_date=str(payload["effective_date"]),
        source=str(payload["source"]),
    )


def load_design(root: Path) -> SiteDesign:
    payload = yaml.safe_load((root / DESIGN_PATH).read_text())
    site = payload["site"]
    return SiteDesign(
        name=str(site["name"]),
        rack_count=int(site["rack_count"]),
        usable_power_budget_w=watts_from_label(site["usable_power_budget_w"]),
    )


def write_spec(root: Path, spec: RackSpec) -> None:
    path = root / SPEC_PATH
    payload = {
        "vendor": spec.vendor,
        "sku": spec.sku,
        "rack_power_w": spec.rack_power_w,
        "unit": "W",
        "revision": spec.revision,
        "effective_date": spec.effective_date,
        "source": spec.source,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n")


def write_design(root: Path, design: SiteDesign) -> None:
    path = root / DESIGN_PATH
    payload = {
        "site": {
            "name": design.name,
            "rack_count": design.rack_count,
            "usable_power_budget_w": design.usable_power_budget_w,
            "unit": "W",
        }
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False))


def write_provenance(root: Path, event: dict) -> None:
    path = root / PROVENANCE_PATH
    history = json.loads(path.read_text()) if path.exists() else {"events": []}
    history.setdefault("events", []).append(event)
    path.write_text(json.dumps(history, indent=2) + "\n")
