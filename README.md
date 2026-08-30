# RackShift

Keeps an AI-infrastructure design correct when a GPU-rack power spec changes.

Eight racks at 100 kW fit an 850 kW usable feed. When the vendor revises the rack to 112 kW, the committed design is over budget. RackShift proves that with a deterministic validator, proposes two legal repairs, and stops until a human approves a Qodo-reviewed pull request.

A chatbot would answer a question about the design. RackShift keeps the design correct as the world changes.

## Stack

- **TrueForge** runs the agent loop, sandbox, subagents, and approval gate.
- **Qodo** reviews every substantive pull request before merge.
- **GitHub** is the source of truth for the spec, the design, and the review trail.
- OpenAI is only the model behind TrueForge.

There is no Bright Data scraper and no Daytona cloud sandbox. Power math is ordinary Python. The model is not allowed to invent a passing budget.

## Demo

```sh
uv sync --extra dev
uv run pytest -q
uv run rackshift status    # VALID: 8 × 100 kW = 800 kW ≤ 850 kW
uv run rackshift revise    # VIOLATION: 8 × 112 kW = 896 kW
uv run rackshift serve     # operator UI at http://127.0.0.1:8787
```

TrueForge should already be running (`npx @truefoundry/trueforge` → http://localhost:8790). Register the local MCP server after `uv run rackshift mcp --port 8788`, then load `trueforge/agent.json`.

Two remediations, neither chosen by the agent:

| Option | Result |
| --- | --- |
| `reduce-racks` | 7 × 112 kW = 784 kW. Valid. Less compute. |
| `upgrade-feed` | Keep 8 racks, raise usable budget to 946 kW (same 50 kW headroom). Valid. Electrical-plan change. |

## Architecture

```text
specs/rack-source.json     vendor assumption (watts)
design/site.yaml           committed row
        │
        ▼
uv run rackshift status    deterministic PASS/FAIL
        │
        ▼
TrueForge session          tools + sandbox + subagents
        │
        ▼
draft GitHub pull request  Qodo review, then human merge
```

## Qodo Code Review Evidence

Qodo is required on every substantive merge. Direct pushes to `main` do not count.

- Representative PR: _added after the first reviewed merge_
- What Qodo surfaced and what changed: _fill after the review thread exists_
- Follow-up review against the final code: same pull request, second `/agentic_review`

See `CONTRIBUTING.md` for the branch → review → merge rule.

## License

MIT
