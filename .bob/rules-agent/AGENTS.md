# Project Coding Rules (Non-Obvious Only)

- **Tool file name = function name = spec `tool:` field** — all three must match exactly or the test runner's dynamic import breaks silently.
- `@tool` wraps returns in `ToolResponse`; unwrap with `raw.content if hasattr(raw, "content") else str(raw)` when calling outside wxO.
- Always return a plain `str` from `@tool` functions — no JSON, no dicts; the agent and test runner both do substring matching on the output.
- Guard empty/whitespace inputs explicitly (`if not param or not param.strip()`) — the agent may call the tool before collecting required data.
- KB documents are referenced **relative to the KB YAML file** (`"files/doc.txt"`), not relative to the project root.
- Deploy order: **KB → tool → agent**. Agent YAML references KB and tool by name; they must exist on wxO before importing the agent.
- `tools[].name` in agent YAML must match the Python `@tool` function name, not the file name (they happen to be the same in this project — keep it that way).
- Test runner must be invoked from `my-lab-project/` — `ROOT` is computed as `Path(__file__).parent.parent`.
- `python tests/run_tests.py tool` — no wxO connection required; imports the tool Python file directly.
- `python tests/run_tests.py agent` — requires `orchestrate env activate` first.
