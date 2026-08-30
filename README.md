# RackShift

`design/site.yaml` is an 8-rack row with an 850 kW usable feed. `specs/rack-source.json` is the vendor rack power. The validator multiplies racks × watts and reports PASS or FAIL.

A vendor revision from 100 kW to 112 kW makes demand 896 kW. The two legal repairs are 7 racks, or keep 8 racks and raise the feed to 946 kW. The agent does not pick one. A human does, on a Qodo-reviewed PR.

## Run

```sh
uv sync --extra dev --extra mcp
uv run pytest -q
uv run rackshift status                 # 8 × 100 kW = 800 kW ≤ 850 kW
uv run rackshift revise                 # 8 × 112 kW = 896 kW, FAIL
uv run rackshift serve                  # http://127.0.0.1:8787
uv run rackshift mcp --port 8788
```

TrueForge: `npx @truefoundry/trueforge` → http://localhost:8790. Point it at the MCP port above. Agent spec is `trueforge/agent.json`.

Power is computed in Python. Watts are canonical. The model is not allowed to do the arithmetic.

## Layout

```text
specs/rack-source.json   vendor rack power (W)
design/site.yaml         committed row
uv run rackshift status  PASS / FAIL
TrueForge                tools, sandbox, approval
GitHub PR                Qodo review, then merge
```

## Qodo Code Review Evidence

Substantive changes go through a PR. Direct pushes to `main` do not count.

- Representative PR: https://github.com/kiankyars/rackshift/pull/2
- What Qodo surfaced: Highs on XSS in the operator UI, silent `int()` on rack count, ignored `unit` metadata, and `revise` overwriting a newer spec. All four were fixed on the same PR; Mediums (write locking, MCP extra) were fixed too.
- Follow-up review: `/agentic_review` after commit `21232a8`

See `CONTRIBUTING.md`.

## License

MIT
