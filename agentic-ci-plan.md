# Agentic CI/CD Loop — Plan

## Overview

Add a three-level GitHub Actions CI/CD pipeline to `my-lab-project/`. No build step exists — Python tools are deployed directly to wxO via ADK. All workflows live under `.github/workflows/` inside the repo root (`my-lab-project/`).

Trigger model:
- **Level 1** — every push to any branch (pre-merge gate)
- **Level 2** — PR open or update targeting `main`
- **Level 3** — nightly scheduled run

---

## Sub-Task 1 — Scaffolding and tooling baseline

**Status**: `[ ] pending`

**Intent**: Establish the minimum packaging and tooling config that all three levels depend on. The project currently has no `pyproject.toml`, `requirements.txt`, or linter config. This sub-task adds those so subsequent workflow files can install and invoke tools consistently.

**Expected Outcomes**:
- `pyproject.toml` exists at the repo root with Ruff, Bandit, and pip-audit listed as dev dependencies (or as optional extras), plus a `[tool.ruff]` section targeting `tools/` and `tests/`.
- Running `ruff check .` and `ruff format --check .` from `my-lab-project/` exits 0 on the current codebase.
- A `requirements-dev.txt` (or equivalent) documents all CI tool pins so GHA steps can do a single `pip install -r` call.

**Todo List**:
1. Create `my-lab-project/pyproject.toml` with a `[tool.ruff]` section: `line-length = 100`, `target-version = "py311"`, `select = ["E", "F", "W", "I"]`, `src = ["tools", "tests"]`.
2. Create `my-lab-project/requirements-dev.txt` pinning: `ruff`, `bandit[toml]`, `pip-audit`.
3. Run `ruff check .` locally to confirm zero violations on the existing source files; fix any that exist.

**Relevant Context**:
- Source files: `tools/get_ferie_residue.py`, `tests/run_tests.py`
- No existing linter config anywhere in the repo
- Python version: 3.11+

---

## Sub-Task 2 — Level 1: Lint & Format gate

**Status**: `[ ] pending`

**Intent**: Block any push that introduces syntax errors or formatting violations. Fast, stateless, no secrets required.

**Expected Outcomes**:
- `.github/workflows/l1-lint.yml` exists and is valid GitHub Actions YAML.
- The workflow triggers on `push` to all branches.
- It installs Ruff, runs `ruff check .` and `ruff format --check .`, and fails the job on any violation.
- No wxO credentials, no external network calls beyond package install.

**Todo List**:
1. Create `.github/workflows/l1-lint.yml` with:
   - `on: push` (all branches)
   - Job `lint` on `ubuntu-latest`, Python 3.11
   - Steps: checkout → setup-python → `pip install ruff` → `ruff check .` → `ruff format --check .`
   - Working directory set to `my-lab-project/`

**Relevant Context**:
- Ruff config will come from `pyproject.toml` added in Sub-Task 1
- The `tools/__pycache__/` directory is tracked in git (`.pyc` file committed) — add a `.gitignore` excluding `__pycache__/` and `*.pyc` to avoid Ruff scanning compiled files

---

## Sub-Task 3 — Level 2: PR test suite (tool + agent)

**Status**: `[ ] pending`

**Intent**: Validate that every PR targeting `main` passes both the tool unit tests (no wxO connection) and the live agent tests (requires wxO credentials). This is the main quality gate before merge.

**Expected Outcomes**:
- `.github/workflows/l2-pr-tests.yml` exists and is valid GitHub Actions YAML.
- Workflow triggers on `pull_request` targeting `main` (types: `opened`, `synchronize`, `reopened`).
- Job runs `python tests/run_tests.py tool` — passes with zero failures.
- Job runs `python tests/run_tests.py agent` using the `WXO_API_KEY` GitHub Actions secret to activate the orchestrate environment first.
- A failed test causes the PR check to fail, blocking merge.

**Todo List**:
1. Create `.github/workflows/l2-pr-tests.yml`:
   - `on: pull_request` targeting `main`
   - Job `test` on `ubuntu-latest`, Python 3.11
   - Steps: checkout → setup-python → `pip install ibm-watsonx-orchestrate` (ADK) → activate env → `python tests/run_tests.py tool` → `python tests/run_tests.py agent`
   - Inject `WXO_API_KEY` from GitHub Actions secrets via `env:` block
   - wxO env name is hardcoded as `GSIBM`
   - `working-directory: my-lab-project/`
2. Document in `AGENTS.md` how to set the `WXO_API_KEY` secret (see note below on GitHub secret setup).

**GitHub Actions Secret Setup** (one-time, manual):
- Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
- Name: `WXO_API_KEY`
- Value: your IBM watsonx Orchestrate API key
- This value is encrypted by GitHub, never exposed in logs, and available in workflow runs as `${{ secrets.WXO_API_KEY }}`

**Relevant Context**:
- `tests/run_tests.py` agent mode calls `RunClient`/`ThreadsClient` from `ibm_watsonx_orchestrate`
- wxO env activation command: `orchestrate env activate GSIBM -a <API_KEY>` — env name is hardcoded as `GSIBM`
- Agent under test: `MioAgente` — must be deployed before L2 runs (L2 tests the deployed agent, it does not deploy it)
- `askhr_scenarios.yaml` covers 7 multi-turn scenarios — all must pass

---

## Sub-Task 4 — Level 3: Nightly regression + security/SCA

**Status**: `[ ] pending`

**Intent**: Full regression run plus static security analysis (Bandit) and dependency vulnerability scan (pip-audit). Runs nightly so it does not block developer flow but catches regressions and CVEs quickly.

**Expected Outcomes**:
- `.github/workflows/l3-nightly.yml` exists and is valid GitHub Actions YAML.
- Workflow triggers on `schedule: cron` (e.g. `0 2 * * *` — 02:00 UTC nightly) and on manual `workflow_dispatch`.
- Job 1 (`regression`): runs the full `python tests/run_tests.py` suite (tool + agent) against `main`.
- Job 2 (`security`): runs `bandit -r tools/ tests/` and `pip-audit` on the installed dependencies; fails on HIGH or CRITICAL findings.
- Results uploaded as GitHub Actions artifacts (Bandit JSON report, pip-audit output).

**Todo List**:
1. Create `.github/workflows/l3-nightly.yml`:
   - `on: schedule` + `on: workflow_dispatch`
   - Job `regression`: same steps as L2 but runs against `main` HEAD
   - Job `security`:
     - `pip install bandit[toml] pip-audit`
     - `bandit -r tools/ tests/ -f json -o bandit-report.json --severity-level high`
     - `pip-audit --output pip-audit-report.json --format json`
     - Upload both JSON files as artifacts with `actions/upload-artifact`
2. Add `continue-on-error: false` on security steps so any HIGH/CRITICAL finding fails the nightly build.

**Relevant Context**:
- `bandit` config can reference `pyproject.toml` `[tool.bandit]` section (add `skips = []`, `targets = ["tools", "tests"]`)
- `pip-audit` scans the currently installed environment — L3 job must install the same deps as production
- No `requirements.txt` exists today; Sub-Task 1 creates `requirements-dev.txt` — L3 also needs a `requirements.txt` for runtime deps (currently just `ibm-watsonx-orchestrate`)

---

## Sub-Task 5 — Gitignore and AGENTS.md updates

**Status**: `[ ] pending`

**Intent**: Clean up tracked artifacts and document the new CI/CD pipeline for future agents and developers.

**Expected Outcomes**:
- `.gitignore` added at repo root excluding `__pycache__/`, `*.pyc`, `*.pyo`, `.env`, `bandit-report.json`, `pip-audit-report.json`.
- `AGENTS.md` updated with a **CI/CD Pipeline** section describing all three levels, their triggers, required secrets, and how to interpret failures.

**Todo List**:
1. Create `my-lab-project/.gitignore` with standard Python ignores + CI artifact ignores.
2. Untrack `tools/__pycache__/get_ferie_residue.cpython-313.pyc` from git (`git rm --cached`).
3. Append a **CI/CD Pipeline** section to `AGENTS.md` summarising the three levels and secret setup instructions.

**Relevant Context**:
- `tools/__pycache__/get_ferie_residue.cpython-313.pyc` is currently tracked in git (confirmed by `git ls-files`)
- `AGENTS.md` already has a Git Workflow section — CI/CD section goes after it
