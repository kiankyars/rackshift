from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from rackshift.actions import apply_remediation, apply_vendor_revision
from rackshift.remediate import remediations
from rackshift.serialize import report_to_dict
from rackshift.validate import validate

mcp = FastMCP(
    "rackshift",
    instructions=(
        "Deterministic power-budget tools for an AI-rack site design. "
        "Read tools never change files. apply_vendor_revision and apply_remediation write the repo. "
        "Do not merge. Stop after proposing remediations and wait for a human to pick one."
    ),
)


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False})
def get_design_status() -> dict:
    """Validate the committed site design against the current vendor rack spec."""
    report = validate()
    return report_to_dict(report, remediations(report))


@mcp.tool(
    name="apply_vendor_revision",
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
)
def apply_vendor_revision_tool() -> dict:
    """Write the vendor rack-power revision into specs/rack-source.json (100 kW → 112 kW)."""
    apply_vendor_revision()
    report = validate()
    return report_to_dict(report, remediations(report))


@mcp.tool(
    name="apply_remediation",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def apply_remediation_tool(option_id: str) -> dict:
    """Write a chosen remediation into design/site.yaml. option_id: reduce-racks or upgrade-feed."""
    apply_remediation(option_id)
    report = validate()
    return report_to_dict(report, remediations(report))


def serve_mcp(port: int = 8788) -> None:
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = port
    mcp.run(transport="streamable-http")
