from __future__ import annotations

import json
import threading
from pathlib import Path

import yaml

from rackshift.models import RackSpec, SiteDesign
from rackshift.units import watts_from_label

SPEC_PATH = Path("specs/rack-source.json")
DESIGN_PATH = Path("design/site.yaml")
PROVENANCE_PATH = Path("specs/provenance.json")
_WRITE_LOCK = threading.Lock()


def repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "design" / "site.yaml").exists() and (candidate / "specs" / "rack-source.json").exists():
            return candidate
    raise FileNotFoundError("not inside a RackShift repository")


def _require_watts_unit(payload: dict, field: str) -> None:
    unit = payload.get("unit")
    if unit != "W":
        raise ValueError(f"{field} unit must be 'W', got {unit!r}")


def _positive_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be a positive integer, got {value!r}")
    if value < 1:
        raise ValueError(f"{field} must be >= 1, got {value}")
    return value


def load_spec(root: Path) -> RackSpec:
    payload = json.loads((root / SPEC_PATH).read_text())
    _require_watts_unit(payload, "rack_power_w")
    return RackSpec(
        vendor=str(payload["vendor"]),
        sku=str(payload["sku"]),
        rack_power_w=watts_from_label(payload["rack_power_w"]),
        revision=_positive_int(payload["revision"], "revision"),
        effective_date=str(payload["effective_date"]),
        source=str(payload["source"]),
    )


def load_design(root: Path) -> SiteDesign:
    payload = yaml.safe_load((root / DESIGN_PATH).read_text())
    site = payload["site"]
    _require_watts_unit(site, "usable_power_budget_w")
    return SiteDesign(
        name=str(site["name"]),
        rack_count=_positive_int(site["rack_count"], "rack_count"),
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
    with _WRITE_LOCK:
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
    with _WRITE_LOCK:
        path.write_text(yaml.safe_dump(payload, sort_keys=False))


def write_provenance(root: Path, event: dict) -> None:
    path = root / PROVENANCE_PATH
    with _WRITE_LOCK:
        history = json.loads(path.read_text()) if path.exists() else {"events": []}
        history.setdefault("events", []).append(event)
        path.write_text(json.dumps(history, indent=2) + "\n")
