# Deep Codebase Analysis

Goal: produce `analysis/report.json` with verified facts (tech stack, entry
points, module map, data flow, key files, metrics) and 3-8 insight candidates.
Every insight must cite evidence (file path, symbol, or command output).

## 1. Preferred: codebase-memory-mcp

Install once (single static binary, no language runtime or API key):

- macOS/Linux:
  `curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash`
- Windows (PowerShell):
  ```powershell
  Invoke-WebRequest -Uri https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1 -OutFile install.ps1
  Unblock-File .\install.ps1
  .\install.ps1
  ```

The installer auto-configures the MCP entry for detected agents (Codex, Claude
Code, etc.). Restart the agent session after installing, then enable
auto-indexing: `codebase-memory-mcp config set auto_index true`.

When the MCP tools are exposed to this agent, run this query sequence:

1. `get_architecture` - one call returns languages, packages, entry points,
   routes, hotspots, boundaries, layers, and clusters. This covers most of the
   report skeleton.
2. `semantic_query` - ask in natural language, e.g. "how does a request flow
   from the API layer to storage?" and "what are the core abstractions?".
3. `search_code` / `search_graph` - locate concrete symbols, entry points, and
   route registrations.
4. Cypher-style queries for call chains, e.g.
   `MATCH (f:Function)-[:CALLS]->(g) WHERE f.name = 'main' RETURN g.name`.
5. Inspect the 3D graph UI if useful: `codebase-memory-mcp --ui=true --port=9749`.

If indexing a fresh clone: trigger it from the MCP session (the server indexes
the current project on first connection; `auto_index true` makes this
automatic). Large repos (10k+ files) take minutes; query after indexing.

## 2. Fallback: ripgrep + cloc + git (no MCP)

```bash
git -C repo log --oneline -20                 # history & message quality
git -C repo shortlog -sn | head -20           # contributors
cloc repo --json                              # LOC per language (or `tokei repo`)
rg -n "@(app|router)\.(get|post|put|delete)|def .*view|public async" repo/src   # HTTP routes
rg -n "TODO|FIXME" repo                        # debt signals
```

Then:

- Read all manifests: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
  `pom.xml`, `build.gradle`, `requirements.txt`, `Dockerfile`,
  `.github/workflows/*`.
- Find entry points: `main` functions, `bin/`, `cmd/`, `src/main*`,
  `scripts` field in package.json, `__main__.py`.
- Find the highest-signal files: largest files, most-imported modules, most
  recently changed. Read 5-15 of them.
- Trace one end-to-end feature from entry to storage/network boundary.
- List public API surface: exported functions/classes, CLI subcommands, HTTP
  routes, config schema.

## 3. Output shape

```json
{
  "repo": {
    "name": "...", "url": "...", "commit": "...", "branch": "...",
    "language_stats": {"Python": 42000},
    "loc": 42000, "stars": 12300, "license": "MIT"
  },
  "tech_stack": ["FastAPI", "SQLAlchemy", "PostgreSQL"],
  "entry_points": [{"path": "app/main.py", "what": "HTTP server entry"}],
  "modules": [
    {"name": "auth", "purpose": "JWT + OAuth flows", "key_files": ["app/auth.py"], "depends_on": ["db"]}
  ],
  "data_flow": ["HTTP request -> router -> service -> repository -> PostgreSQL"],
  "routes_api": [{"method": "GET", "path": "/api/v1/orders", "handler": "app.orders.list"}],
  "key_files": [{"path": "app/engine.py", "why": "core scheduling loop, 80% of business logic"}],
  "metrics": {"files": 320, "loc": 42000, "commits": 1500, "contributors": 42, "open_issues": 87},
  "insight_candidates": [
    {"fact": "All writes go through a single append-only journal", "evidence": "app/journal.py:12", "why_it_matters": "explains crash-safety story"}
  ]
}
```

## 4. Analysis rules

- Do not copy README claims into the report unless verified in code or by
  command output.
- Spend effort proportional to repo size: <5k LOC, read broadly; large repos,
  lean on graph queries and hotspots.
- Look specifically for: surprising architecture choices, elegant
  abstractions, bottlenecks, dead code, scale/performance numbers, security
  design, migration history, and the "why" behind the project (from README +
  git history + docs).
