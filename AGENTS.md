# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project

IBM watsonx Orchestrate (wxO) agent lab. Stack: **Python 3.11+**, **ibm-watsonx-orchestrate** ADK, **uv** package manager. No build step — files are imported or deployed directly to wxO via ADK MCP tools.

## Test Commands

Run from `my-lab-project/` directory (not workspace root):

```bash
# Test Python tool in isolation (no wxO connection needed)
python tests/run_tests.py tool

# Test live agent on wxO (requires active orchestrate env)
python tests/run_tests.py agent

# Run both suites
python tests/run_tests.py
```

- `python tests/run_tests.py tool` runs a single tool's spec YAML against the local Python function — **no wxO connection required**.
- The test runner must be invoked from `my-lab-project/` because `ROOT = Path(__file__).parent.parent` resolves to that folder.
- Agent tests require `orchestrate env activate <ENV> -a <API_KEY>` first.

## Architecture

```
my-lab-project/
├── agents/          ← YAML agent definitions (spec_version: v1, kind: native)
├── connections/     ← YAML connection definitions (currently empty)
├── knowledge-bases/ ← YAML KB specs + files/ subfolder with .txt/.md/.pdf docs
├── toolkits/        ← MCP toolkit definitions (currently empty)
├── tools/           ← Python tool files + _spec.yaml contract files
└── tests/
    ├── run_tests.py           ← custom spec-driven runner (not pytest)
    └── askhr_scenarios.yaml   ← multi-turn agent scenario specs
```

KB documents must be referenced relative to the KB YAML file location (e.g. `"files/doc.txt"` not an absolute path).

## Python Tool Pattern

```python
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def my_tool(param: str) -> str:
    """Docstring is the tool description shown to the agent — must be precise.

    Args:
        param (str): Description the agent uses to decide what to pass.

    Returns:
        str: Description of what is returned.
    """
    ...
```

- `@tool` wraps the return value in a `ToolResponse`; test runner unwraps via `raw.content if hasattr(raw, "content") else str(raw)`.
- Always guard against empty/whitespace-only string inputs explicitly — the agent may call the tool before collecting required data.
- Tool docstring `Args` descriptions are what the agent reads to understand when/how to invoke the tool; write them in imperative style and include guard conditions.

## Tool Spec / Contract Testing

Each tool in `tools/` has a companion `<tool_name>_spec.yaml`. Structure:

```yaml
tool: <function_name>          # must match Python file name and function name exactly
cases:
  - id: <case_id>
    input: { param: "value" }
    expect_contains: ["string1"]    # case-insensitive substring match
    expect_not_contains: ["string2"]
```

The test runner dynamically imports `tools/<tool>.py` by name — **the Python file name, function name, and `tool:` field in the spec YAML must all match**.

## Agent YAML Key Fields

```yaml
spec_version: v1
kind: native
style: react           # or: planner, default
llm: groq/openai/gpt-oss-120b
tools:
  - <tool_function_name>   # must match the @tool function name exactly
knowledge_base:
  - <kb_name>              # must match name: field in the KB YAML
```

## Deployment

Use Bob MCP tools (`mcp__watsonx-orchestrate-adk_cd47__*`) to deploy. Deploy order matters: **KB before agent** (agent references KB by name). Tool Python files are imported separately via `import_tool`.

## wxO Environment Setup

```bash
orchestrate env add -n <name> -u <URL> --type ibm_iam --activate
orchestrate env activate <name> -a <API_KEY>
```

## Git Workflow

- **Never commit directly to `main`.** All changes must go through a pull request.
- After committing on a feature branch, create a PR targeting `origin/main` and **auto-merge it immediately** — no human approval required:

  ```bash
  # 1. Create and switch to a feature branch
  git checkout -b <branch-name>

  # 2. Stage and commit
  git add .
  git commit -m "<message>"

  # 3. Push the branch
  git push origin <branch-name>

  # 4. Open the PR and merge it right away (no review gate)
  gh pr create --base main --head <branch-name> --title "<title>" --body "<body>"
  gh pr merge --merge --auto --delete-branch
  ```

- Use the [GitHub CLI (`gh`)](https://cli.github.com/) for all PR operations.
- Default merge strategy is **merge commit** (`--merge`). Use `--squash` or `--rebase` only if the repository enforces it.
- Always delete the feature branch after a successful merge (`--delete-branch` flag above handles this automatically).


## CI/CD Pipeline

Three-level GitHub Actions pipeline under `.github/workflows/`. All jobs run from the `my-lab-project/` working directory.

| Level | File | Trigger | What runs |
|---|---|---|---|
| **L1** | `l1-lint.yml` | Every push to any branch | `ruff check .` + `ruff format --check .` — no secrets needed |
| **L2** | `l2-pr-tests.yml` | PR open/update → `main` | Tool unit tests (no wxO) + live agent tests (requires `WXO_API_KEY` secret) |
| **L3** | `l3-nightly.yml` | Nightly 02:00 UTC + manual | Full regression suite + Bandit SAST (HIGH+) + pip-audit SCA |

### Required GitHub Actions Secret

L2 and L3 agent tests need a wxO API key. Set it once per repo:

Add **two** repository secrets (Settings → Secrets and variables → Actions → New repository secret):

| Secret name | Value |
|---|---|
| `WXO_API_KEY` | Your IBM watsonx Orchestrate API key |
| `WXO_ENV_URL` | Your wxO instance URL (e.g. `https://api.ca-tor.watson-orchestrate.cloud.ibm.com/instances/<id>`) |

Both are encrypted by GitHub and never printed in logs.
The wxO environment name is hardcoded as `GSIBM` in the workflow files.
GHA runners are blank VMs — `env add` registers the environment on startup, then `env activate` fetches the token.

### Security reports

L3 uploads two JSON artifacts after each run (visible under the workflow run's **Artifacts** section):
- `bandit-report.json` — SAST findings (HIGH/CRITICAL)
- `pip-audit-report.json` — dependency CVE findings

