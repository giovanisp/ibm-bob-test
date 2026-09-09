# IT Support Knowledge Base — Acme Corp

## Applicazioni Supportate

| App ID | Nome Applicazione | Owner Team | SLA Risposta | SLA Risoluzione |
|--------|-------------------|------------|--------------|-----------------|
| APP-001 | PortalDipendenti | Team Intranet | 2h | 8h |
| APP-002 | GestPaghe | Team Finance IT | 1h | 4h |
| APP-003 | CRMSales | Team CRM | 2h | 8h |
| APP-004 | TimeTracker | Team HR IT | 4h | 24h |
| APP-005 | ExpenseFlow | Team Finance IT | 2h | 8h |
| APP-006 | DataWarehouse | Team BI | 4h | 48h |
| APP-007 | EmailServer | Team Infra | 30min | 2h |
| APP-008 | VPN Aziendale | Team Networking | 30min | 2h |

---

## Categorie di Ticket

| Codice | Categoria | Priorità Default |
|--------|-----------|-----------------|
| CAT-01 | Accesso / Login | Alta |
| CAT-02 | Performance / Lentezza | Media |
| CAT-03 | Errore Applicativo | Alta |
| CAT-04 | Richiesta Nuova Funzionalità | Bassa |
| CAT-05 | Dati Errati / Discrepanza | Alta |
| CAT-06 | Integrazione tra sistemi | Media |
| CAT-07 | Infrastruttura / Rete | Critica |

---

## Procedure di Escalation

### Livello 1 — IT Help Desk
- Gestisce problemi di accesso, reset password, problemi comuni documentati
- Tempo massimo prima dell'escalation: 2h per ticket Alta, 4h per Media

### Livello 2 — Team Owner Applicazione
- Gestisce bug applicativi, degradi di performance, integrazioni
- Tempo massimo prima dell'escalation: SLA Risoluzione × 0.5

### Livello 3 — IT Management
- Escalation automatica se: P1 non risolto in 2h, o cliente esterno impattato

---

## Guide di Risoluzione Comuni

### Problema: Impossibile accedere a PortalDipendenti
**Sintomi:** Schermata bianca, errore 403, loop di redirect  
**Causa comune:** Cookie corrotti o sessione scaduta  
**Soluzione:**
1. Svuota cache e cookie del browser
2. Prova in modalità navigazione privata
3. Se il problema persiste, segnala a Team Intranet indicando browser e versione OS

### Problema: GestPaghe mostra importi errati
**Sintomi:** Cedolino con importi diversi da aspettative, calcoli IVA errati  
**Causa comune:** Aggiornamento parametri fiscali non propagato  
**Soluzione:**
1. Verifica data di riferimento del cedolino
2. Controlla se è attivo un aggiornamento di sistema (banner giallo in homepage)
3. Escalation immediata a Team Finance IT — NON modificare dati manualmente

### Problema: VPN Aziendale non si connette
**Sintomi:** Timeout di connessione, errore "Authentication failed"  
**Causa comune:** Certificato scaduto o aggiornamento client richiesto  
**Soluzione:**
1. Verifica che il client VPN sia aggiornato all'ultima versione (v3.2+)
2. Rinnova il certificato utente dal portale IT: https://certs.acme.internal
3. Se il problema persiste dopo il rinnovo, contatta Team Networking con urgenza

---

## Ticket di Esempio (Storico)

| Ticket ID | Data | Applicazione | Categoria | Priorità | Stato | Tempo Risoluzione |
|-----------|------|-------------|-----------|----------|-------|-------------------|
| TKT-4821 | 2024-11-10 | APP-007 | CAT-07 | Critica | Chiuso | 1h 45min |
| TKT-4822 | 2024-11-10 | APP-001 | CAT-01 | Alta | Chiuso | 3h 12min |
| TKT-4823 | 2024-11-11 | APP-002 | CAT-05 | Alta | Chiuso | 2h 30min |
| TKT-4824 | 2024-11-12 | APP-003 | CAT-02 | Media | Aperto | — |
| TKT-4825 | 2024-11-12 | APP-004 | CAT-06 | Media | In Lavorazione | — |

---

## Contatti di Riferimento

| Team | Email | Telefono Emergenze |
|------|-------|--------------------|
| IT Help Desk | helpdesk@acme.com | +39 02 1234 5000 |
| Team Intranet | intranet-team@acme.com | — |
| Team Finance IT | finance-it@acme.com | +39 02 1234 5010 |
| Team Networking | networking@acme.com | +39 02 1234 5020 (H24) |
| IT Management | it-manager@acme.com | +39 02 1234 5001 |
