# Project Documentation Rules (Non-Obvious Only)

- `lab-data/` contains **original scenario source documents** (canonical reference). `knowledge-bases/files/` contains the `.txt`/`.md` copies actually loaded into wxO KBs — they may diverge from `lab-data/` originals.
- KB YAML in `knowledge-bases/` uses `.txt` files, not `.md`, even though markdown versions also exist in the same folder — the embeddings model preference is `.txt`.
- `tools/get_ferie_residue_spec.yaml` is both a contract spec **and** test input — it defines expected substrings against the stub HR data. If stub data changes, the spec expected values break.
- `tests/askhr_scenarios.yaml` targets an agent named `MioAgente` — tests fail if the agent on wxO has a different name. The `agent:` field at the top of the file must match the deployed agent name exactly.
- `connections/` and `toolkits/` directories are intentionally empty (scaffolding for lab use).
- The README is in Italian — the codebase itself is bilingual (Italian comments/docstrings, English variable names in some places).
