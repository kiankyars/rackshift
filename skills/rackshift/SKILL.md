---
name: rackshift
description: Validate and repair an AI-rack site design when the vendor power spec changes. Truth lives in the RackShift CLI, not in model arithmetic.
---

# RackShift

You keep `design/site.yaml` valid against `specs/rack-source.json`.

## Rules

- Never compute the power budget yourself. Call `uv run rackshift status` in the sandbox, or the `get_design_status` MCP tool.
- Watts are canonical. Do not mix kW and W in new fields.
- If the design is valid, say so and stop.
- If it is invalid, present the two remediations from the tool output. Do not pick one.
- `apply_remediation` and merging a pull request are irreversible. Pause for human approval first.
- After a human chooses, write the design, open a GitHub pull request, and wait for Qodo. Do not merge.

## Demo sequence

1. `uv run rackshift status` — expect VALID, 8×100 kW = 800 kW inside 850 kW.
2. `uv run rackshift revise` — vendor spec becomes 112 kW. Expect VIOLATION, 896 kW vs 850 kW.
3. Show both remediations. Stop.
4. On approval, `uv run rackshift apply reduce-racks` or `upgrade-feed`.
5. Open a PR from the changed files. Ask the human to wait for Qodo before merge.
