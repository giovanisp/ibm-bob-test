from __future__ import annotations

from datetime import date

from ibm_watsonx_orchestrate.agent_builder.tools import tool


# ---------------------------------------------------------------------------
# STUB DATA — sostituire con chiamata reale all'API HR (es. SAP, Workday...)
# ---------------------------------------------------------------------------
_STUB_HR_DATA: dict[str, dict] = {
    "mario.rossi": {
        "nome": "Mario Rossi",
        "ferie_totali": 26,
        "ferie_godute": 10,
        "ferie_riportate_anno_prec": 3,
        "rol_totali_ore": 40,
        "rol_godute_ore": 16,
        "anno": date.today().year,
    },
    "anna.bianchi": {
        "nome": "Anna Bianchi",
        "ferie_totali": 26,
        "ferie_godute": 18,
        "ferie_riportate_anno_prec": 0,
        "rol_totali_ore": 40,
        "rol_godute_ore": 32,
        "anno": date.today().year,
    },
}
# ---------------------------------------------------------------------------


@tool
def get_ferie_residue(employee_id: str) -> str:
    """Restituisce il saldo aggiornato di ferie e ROL residui per un dipendente.

    Recupera dal sistema HR il numero di giorni di ferie ancora disponibili,
    le ore di ROL residue e le ferie riportate dall'anno precedente per
    l'anno corrente. I dati sono riferiti all'anno solare in corso.

    IMPORTANTE: prima di chiamare questo tool devi conoscere l'employee_id
    del dipendente. Se l'utente non lo ha fornito, chiediglielo esplicitamente
    con: "Qual è il tuo ID dipendente (es. mario.rossi)?"

    Args:
        employee_id (str): L'identificativo del dipendente (es. "mario.rossi"),
            tipicamente nella forma nome.cognome oppure la matricola aziendale.
            Non chiamare questo tool se employee_id è vuoto o sconosciuto.

    Returns:
        str: Un testo con il saldo ferie e ROL del dipendente, oppure un
            messaggio di errore se il dipendente non è stato trovato.
    """
    # --- TODO: sostituire il blocco seguente con la chiamata HTTP reale ---
    # import requests
    # from ibm_watsonx_orchestrate.run import connections
    # conn = connections.api_key_auth("hr_system_credentials")
    # response = requests.get(
    #     f"{conn.url}/api/v1/employees/{employee_id}/leave-balance",
    #     headers={"x-api-key": conn.api_key},
    # )
    # response.raise_for_status()
    # data = response.json()
    # ----------------------------------------------------------------------

    # Gestione input mancante o non valido
    if not employee_id or not employee_id.strip():
        return (
            "employee_id non fornito. Chiedi all'utente il suo ID dipendente "
            "(es. 'mario.rossi') prima di chiamare questo tool."
        )

    data = _STUB_HR_DATA.get(employee_id.strip().lower())

    if data is None:
        return (
            f"Dipendente '{employee_id}' non trovato nel sistema HR. "
            "Verificare l'ID e riprovare oppure contattare hr@acme.com."
        )

    ferie_residue = data["ferie_totali"] - data["ferie_godute"] + data["ferie_riportate_anno_prec"]
    rol_residue = data["rol_totali_ore"] - data["rol_godute_ore"]

    return (
        f"Dipendente: {data['nome']} ({employee_id})\n"
        f"Anno: {data['anno']}\n"
        f"Ferie residue: {ferie_residue} giorni "
        f"(godute: {data['ferie_godute']}, "
        f"riportate anno prec.: {data['ferie_riportate_anno_prec']})\n"
        f"ROL residui: {rol_residue} ore (godute: {data['rol_godute_ore']})"
    )
