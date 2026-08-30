from __future__ import annotations

import argparse
import json
import sys

from rackshift.actions import apply_remediation, apply_vendor_revision
from rackshift.remediate import remediations
from rackshift.serialize import report_to_dict
from rackshift.validate import validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rackshift")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="validate the committed design against the current spec")
    sub.add_parser("revise", help="apply the vendor rack-power revision (100 kW → 112 kW)")
    apply_p = sub.add_parser("apply", help="apply a tested remediation to design/site.yaml")
    apply_p.add_argument("option", choices=["reduce-racks", "upgrade-feed"])
    sub.add_parser("serve", help="serve the operator UI")
    serve_p = sub.add_parser("mcp", help="serve the RackShift MCP endpoint for TrueForge")
    serve_p.add_argument("--port", type=int, default=8788)

    args = parser.parse_args(argv)
    if args.cmd == "status":
        report = validate()
        payload = report_to_dict(report, remediations(report))
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if report.valid else 2
    if args.cmd == "revise":
        spec = apply_vendor_revision()
        report = validate()
        payload = report_to_dict(report, remediations(report))
        payload["revised_to_w"] = spec.rack_power_w
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if report.valid else 2
    if args.cmd == "apply":
        apply_remediation(args.option)
        report = validate()
        json.dump(report_to_dict(report, remediations(report)), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if report.valid else 2
    if args.cmd == "serve":
        from rackshift.web import serve

        serve()
        return 0
    if args.cmd == "mcp":
        try:
            from rackshift.mcp_server import serve_mcp
        except ModuleNotFoundError:
            sys.stderr.write("MCP extra missing. Install with: uv sync --extra mcp\n")
            return 1
        serve_mcp(args.port)
        return 0
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
