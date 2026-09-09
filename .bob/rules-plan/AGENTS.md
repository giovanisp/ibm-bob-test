# Project Architecture Rules (Non-Obvious Only)

- **No build pipeline** — Python tool files are uploaded directly to wxO via ADK; no packaging, no pip install required for tool consumers.
- The test runner (`tests/run_tests.py`) is a custom spec-driven runner, **not pytest** — it uses `yaml.safe_load` + dynamic `__import__` and cannot be run with `pytest` or `python -m pytest`.
- Tool contract testing is completely decoupled from wxO: `run_tests.py tool` imports the Python module directly. Agent testing (`run_tests.py agent`) hits the live wxO API via `RunClient`/`ThreadsClient` — it is an integration test, not a unit test.
- `_STUB_HR_DATA` in `get_ferie_residue.py` uses `firstname.lastname` keys in lowercase; the tool normalises with `.strip().lower()` — case-insensitive lookup is intentional and tested.
- KB embeddings model in the existing YAML is `ibm/slate-125m-english-rtrvr-v2` (English retriever). For Italian documents, consider `ibm/granite-embedding-278m-multilingual` (shown in the README Quick Reference but not yet used in the committed YAML).
- Agent multi-turn tests maintain `thread_id` across turns — scenario tests are stateful. Each scenario starts a new thread; a turn failure aborts the rest of the scenario's turns.
- The `fuori_scope` scenario in `askhr_scenarios.yaml` uses `expect_contains: [[]]` (list-of-empty-list) as a sentinel for "no positive assertions" — the runner explicitly handles this by resetting `must_have` to `[]`.
