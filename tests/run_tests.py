"""
tests/run_tests.py
==================
Spec-Driven test runner per il progetto AskHR.

Modalità disponibili:
  python tests/run_tests.py tool     — testa get_ferie_residue in isolamento
                                       leggendo tools/get_ferie_residue_spec.yaml
  python tests/run_tests.py agent    — testa MioAgente live su wxO
                                       leggendo tests/askhr_scenarios.yaml
  python tests/run_tests.py          — esegue entrambe le suite

Prerequisiti per la modalità agent:
  - orchestrate env activate <ENV> -a <API_KEY>
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# Forza stdout UTF-8 su Windows (evita UnicodeEncodeError con emoji e accenti)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent  # my-lab-project/
TOOL_SPEC = ROOT / "tools" / "get_ferie_residue_spec.yaml"
AGENT_SPEC = Path(__file__).parent / "askhr_scenarios.yaml"

# ---------------------------------------------------------------------------
# ANSI colours
# ---------------------------------------------------------------------------
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _pass(msg: str) -> str:
    return f"{GREEN}PASS{RESET} {msg}"


def _fail(msg: str) -> str:
    return f"{RED}FAIL{RESET} {msg}"


def _skip(msg: str) -> str:
    return f"{YELLOW}SKIP{RESET} {msg}"


# ---------------------------------------------------------------------------
# Tool suite — importa il modulo e chiama la funzione direttamente
# ---------------------------------------------------------------------------


def run_tool_suite(spec_path: Path) -> tuple[int, int]:
    """Esegue tutti i casi della spec del tool. Ritorna (passed, total)."""
    print(f"\n{BOLD}=== Tool Suite: {spec_path.name} ==={RESET}\n")

    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    tool_name: str = spec["tool"]
    cases: list[dict] = spec.get("cases", [])

    # Import dinamico del tool Python
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        module = __import__(tool_name)
        fn = getattr(module, tool_name)
    except Exception as exc:
        print(f"{RED}ERRORE import tool '{tool_name}': {exc}{RESET}")
        return 0, len(cases)

    passed = 0
    for case in cases:
        cid: str = case["id"]
        inputs: dict = case.get("input", {})
        must_have: list[str] = case.get("expect_contains", [])
        must_not: list[str] = case.get("expect_not_contains", [])

        try:
            raw = fn(**inputs)
            # Il decorator @tool dell'ADK wrappa il ritorno in ToolResponse
            result: str = raw.content if hasattr(raw, "content") else str(raw)
        except Exception as exc:
            print(_fail(f"[{cid}] eccezione: {exc}"))
            continue

        result_lower = result.lower()
        failures: list[str] = []

        for token in must_have:
            if token.lower() not in result_lower:
                failures.append(f"manca '{token}'")
        for token in must_not:
            if token.lower() in result_lower:
                failures.append(f"presente inatteso '{token}'")

        if failures:
            print(_fail(f"[{cid}] {', '.join(failures)}"))
            print(f"       output: {result!r}")
        else:
            print(_pass(f"[{cid}]"))
            passed += 1

    return passed, len(cases)


# ---------------------------------------------------------------------------
# Agent suite — chiama `orchestrate chat ask` per ogni turn
# ---------------------------------------------------------------------------


def _chat(agent: str, message: str, thread_id: str | None = None) -> tuple[str, str]:
    """
    Chiama l'agente wxO via SDK Python e ritorna (risposta, thread_id).
    Usa la stessa logica di chat_controller._execute_agent_interaction_websocket.
    """
    try:
        from ibm_watsonx_orchestrate.cli.commands.agents.agents_helper import get_agent_id_by_name
        from ibm_watsonx_orchestrate.client.chat.run_client import RunClient
        from ibm_watsonx_orchestrate.client.threads.threads_client import ThreadsClient
        from ibm_watsonx_orchestrate.client.utils import instantiate_client
    except ImportError as exc:
        return f"[ImportError: {exc}]", ""

    try:
        # Risolvi agent_id dal nome
        agent_id = get_agent_id_by_name(agent)
        if not agent_id:
            return f"[agente '{agent}' non trovato]", ""

        run_client: RunClient = instantiate_client(RunClient)
        threads_client: ThreadsClient = instantiate_client(ThreadsClient)

        # Invia messaggio — create_run ritorna un dict {"thread_id": ..., "run_id": ...}
        run_response = run_client.create_run(
            message=message,
            agent_id=agent_id,
            thread_id=thread_id,
        )
        thread_id = run_response["thread_id"]
        run_id = run_response["run_id"]

        # Attendi completamento run
        run_client.wait_for_run_completion(run_id)

        # Leggi messaggi del thread e prendi l'ultimo messaggio assistant
        thread_messages = threads_client.get_thread_messages(thread_id)
        if isinstance(thread_messages, dict) and "data" in thread_messages:
            messages = thread_messages["data"]
        elif isinstance(thread_messages, list):
            messages = thread_messages
        else:
            messages = []

        response_text = ""
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, list):
                    parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("response_type") == "text":
                                parts.append(item.get("text", ""))
                            elif "text" in item:
                                parts.append(item["text"])
                    response_text = "\n".join(parts)
                else:
                    response_text = str(content)
                break

        return response_text, thread_id

    except Exception as exc:
        return f"[ERRORE: {exc}]", thread_id or ""


def run_agent_suite(spec_path: Path) -> tuple[int, int]:
    """Esegue tutti gli scenari conversazionali. Ritorna (passed, total)."""
    print(f"\n{BOLD}=== Agent Suite: {spec_path.name} ==={RESET}\n")

    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    agent: str = spec["agent"]
    scenarios: list[dict] = spec.get("scenarios", [])

    passed = 0
    for scenario in scenarios:
        sid: str = scenario["id"]
        turns: list[dict] = scenario.get("turns", [])
        thread_id: str | None = None
        scenario_ok = True

        for i, turn in enumerate(turns):
            user_msg: str = turn["user"]
            must_have: list = turn.get("expect_contains", [])
            must_not: list[str] = turn.get("expect_not_contains", [])

            # Salta se expect_contains è lista vuota (nessun vincolo positivo)
            if must_have == [[]]:
                must_have = []

            response, new_tid = _chat(agent, user_msg, thread_id)
            if new_tid:
                thread_id = new_tid

            response_lower = response.lower()
            failures: list[str] = []

            for token in must_have:
                if isinstance(token, str) and token.lower() not in response_lower:
                    failures.append(f"manca '{token}'")
            for token in must_not:
                if isinstance(token, str) and token.lower() in response_lower:
                    failures.append(f"presente inatteso '{token}'")

            if failures:
                print(_fail(f"[{sid}] turno {i + 1}: {', '.join(failures)}"))
                print(f"       user:     {user_msg!r}")
                safe_resp = response[:300].encode("utf-8", errors="replace").decode("utf-8")
                print(f"       response: {safe_resp!r}")
                scenario_ok = False
                break

        if scenario_ok:
            print(_pass(f"[{sid}]"))
            passed += 1

    return passed, len(scenarios)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _summary(label: str, passed: int, total: int) -> None:
    colour = GREEN if passed == total else RED
    print(f"\n{colour}{BOLD}{label}: {passed}/{total} passed{RESET}\n")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    tool_passed = tool_total = 0
    agent_passed = agent_total = 0

    if mode in ("tool", "all"):
        tool_passed, tool_total = run_tool_suite(TOOL_SPEC)
        _summary("Tool suite", tool_passed, tool_total)

    if mode in ("agent", "all"):
        agent_passed, agent_total = run_agent_suite(AGENT_SPEC)
        _summary("Agent suite", agent_passed, agent_total)

    if mode == "all":
        total_p = tool_passed + agent_passed
        total_t = tool_total + agent_total
        _summary("TOTALE", total_p, total_t)

    # Exit code non-zero se almeno un test fallisce
    total_passed = tool_passed + agent_passed
    total_all = tool_total + agent_total
    sys.exit(0 if total_passed == total_all else 1)


if __name__ == "__main__":
    main()
