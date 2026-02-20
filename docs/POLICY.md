---

# POLICY.md

## Zweck

Diese Policy definiert den minimalen, deterministischen Vertrag für eine semi-automatisierte Softwareentwicklung mit:

* **Kanban-Karten** als Kommunikations- und Steuerobjekt (Human ↔ Agent),
* **Artefaktdateien** als inhaltliche Single Source of Truth (Requirement/Design/Tests),
* **Status + Tags + Assignee** als einziges Steuerungssignal.

## Geltungsbereich

Gilt für alle Karten und Artefakte innerhalb eines Projekts/Workspaces.

---

## 1. Begriffe und Rollen

### Human (Hannes)

* beantwortet Rückfragen,
* gibt Vorschläge frei (Approval),
* fordert Überarbeitung an (Rework),
* kann jederzeit verwerfen (Discard).

### Agenten

* erzeugen und überarbeiten Artefakte (Requirements/Design/Tests),
* stellen Rückfragen, wenn Informationen fehlen,
* verändern Status/Tags/Assignee nur im Rahmen definierter Workflows.

---

## 2. Datenobjekte

### 2.1 Kanban-Karte (`cards/<id>-<slug>.md`)

**Funktion:** Kommunikation + Steuerung, nicht inhaltliche Spezifikation.

Mindeststruktur (Überschriften sind verbindlich):

* `## Links`
* `## Rückfragen an Hannes`
* `## Human-Feedback`

**Offene Rückfrage:** Eine Zeile `Antwort:` ist leer.

### 2.2 Artefakte

* `requirements/<id>-<slug>.md` (inkl. Abnahmekriterien)
* `design/<id>-<slug>.md`
* `tests/<id>-<slug>.md` (Testplan + später Report; referenziert Requirements)

**Grundsatz:** Inhalte leben in Artefakten, nicht in der Karte.

---

## 3. Statusmodell

### 3.1 Status

* `INBOX`
* `REQUIREMENT`
* `DESIGN`
* `IMPLEMENTING`
* `VERIFYING`
* `DONE`
* `DISCARDED`

### 3.2 Status-Semantik

* `INBOX`: Idee roh, noch keine Spezifikation.
* `REQUIREMENT`: Requirement-Artefakt existiert (Entwurf oder freigegeben).
* `DESIGN`: Design-Artefakt existiert (Entwurf oder freigegeben).
* `IMPLEMENTING`: Umsetzung läuft / wird durchgeführt.
* `VERIFYING`: Tests/Verifikation und Abnahmevorbereitung.
* `DONE`: abgeschlossen und akzeptiert.
* `DISCARDED`: bewusst verworfen, keine weitere Bearbeitung.

---

## 4. Tagmodell

### 4.1 Steuer-Tags (minimal, verbindlich)

* `needs-input`
  Rückfragen sind offen; Human muss antworten.
* `needs-approval`
  Vorschlag liegt vor; Human muss freigeben.
* `needs-rework`
  Human hat abgelehnt; Agent soll anhand Feedback neu ausarbeiten.

### 4.2 Tag-Exklusivität (Invariante)

Es darf **maximal eines** der Tags `{needs-input, needs-approval, needs-rework}` gleichzeitig gesetzt sein.

---

## 5. Assignee-Regeln

### 5.1 Zuweisung an Human

Wenn `needs-input` **oder** `needs-approval` gesetzt ist, dann:

* `assignee = Hannes`

### 5.2 Zuweisung an Agent/Queue

Wenn `needs-rework` gesetzt ist, dann:

* `assignee` ist **leer** (oder eine definierte Agent-Queue), jedoch **nicht** Hannes

---

## 6. Schreibrechte und Sperren (ohne managed blocks)

### 6.1 Artefakte schreiben

Agenten dürfen Artefakte nur schreiben, wenn:

* ein Artefakt erstmalig angelegt wird (typischerweise bei `INBOX → REQUIREMENT`), **oder**
* `needs-rework` gesetzt ist (Überarbeitung explizit angefordert).

### 6.2 Keine Artefaktänderungen bei Human-Gates

Solange `needs-input` **oder** `needs-approval` gesetzt ist:

* Agenten ändern **keine** Artefakte.

### 6.3 Human-Edits in Artefakten

Der Human editiert Artefakte grundsätzlich nicht. Änderungen erfolgen primär über:

* Rückfragen/Antworten in der Karte,
* Human-Feedback in der Karte + `needs-rework`.

Ausnahmen sind möglich, aber dann gilt:

* keine parallele Agentenbearbeitung (kein `needs-rework` aktiv).

---

## 7. Human-Runbook (minimale Bedienung)

### 7.1 Rückfragen beantworten

* Antworten in `## Rückfragen an Hannes` ergänzen
* Tag `needs-input` entfernen
* assignee leeren (optional)

### 7.2 Vorschlag freigeben (Approval)

* Tag `needs-approval` entfernen
* assignee leeren (optional)

### 7.3 Überarbeitung anfordern (Rework)

* Feedback in `## Human-Feedback` ergänzen (konkret, stichpunktartig, testbar)
* Tag `needs-approval` entfernen (falls gesetzt)
* Tag `needs-rework` setzen
* assignee leeren

### 7.4 Verwerfen

* Status `DISCARDED` setzen
* alle `needs-*` Tags entfernen
* assignee leeren

---

## 8. Fehler- und Konfliktbehandlung (ohne integrity-check)

### 8.1 Konflikt: mehrere `needs-*` Tags

Workflows dürfen in diesem Fall **keine** Artefakte ändern und sollen:

* entweder die Karte **überspringen** (skip),
* oder `needs-input` setzen und eine Rückfrage notieren („Tag-Konflikt bereinigen“).

### 8.2 Fehlende Links/Artefakte in nicht-Initialphasen

Wenn in `REQUIREMENT/DESIGN/VERIFYING` der erwartete Link fehlt:

* `needs-input` setzen + konkrete Rückfrage („Bitte Link ergänzen oder Artefaktpfad bestätigen“),
* keine Artefakte schreiben.

### 8.3 Batch-Größe

Pro Workflow-Run sollten maximal **1–3 Karten** bearbeitet werden (Risikobegrenzung).

---

## 9. Qualitätskriterien (konzise)

* Requirements: Abnahmekriterien sind eindeutig, testbar, ohne Implementierungsdetails.
* Design: Entscheidungen sind begründet; Auswirkungen und Risiken sind benannt.
* Tests: klare Zuordnung AC → Testfälle; Report ist nachvollziehbar.

