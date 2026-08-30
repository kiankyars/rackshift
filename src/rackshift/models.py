from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RackSpec:
    vendor: str
    sku: str
    rack_power_w: int
    revision: int
    effective_date: str
    source: str


@dataclass(frozen=True)
class SiteDesign:
    name: str
    rack_count: int
    usable_power_budget_w: int


@dataclass(frozen=True)
class Constraint:
    name: str
    left_label: str
    right_label: str
    demand_w: int
    budget_w: int

    @property
    def valid(self) -> bool:
        return self.demand_w <= self.budget_w

    @property
    def delta_w(self) -> int:
        return self.demand_w - self.budget_w


@dataclass(frozen=True)
class ValidationReport:
    spec: RackSpec
    design: SiteDesign
    constraints: tuple[Constraint, ...]
    repo_root: Path

    @property
    def valid(self) -> bool:
        return all(item.valid for item in self.constraints)


@dataclass(frozen=True)
class Remediation:
    id: str
    title: str
    summary: str
    rack_count: int
    usable_power_budget_w: int
    compute_capacity_racks: int
    requires_electrical_change: bool
