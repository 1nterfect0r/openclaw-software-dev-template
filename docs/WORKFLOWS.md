---

# WORKFLOWS.md

## Allgemeines

Jeder Workflow folgt dem Schema:

1. **Select** (Status/Tags/Assignee Filter)
2. **Guard** (Konflikte/Unklarheiten → skip oder needs-input)
3. **Act** (Artefakte erzeugen/ändern)
4. **Set** (Tags/Assignee/Status aktualisieren)

### Gate-Interpretation je Status

* `REQUIREMENT` + `needs-approval`: Freigabe Requirement
* `DESIGN` + `needs-approval`: Freigabe Design
* `VERIFYING` + `needs-approval`: Abnahme nach Testreport
* `needs-input`: Rückfragen (statusabhängig)

---

## Workflow 1: triage_inbox

### Given

* Karte mit `status = INBOX`
* keine Tags aus `{needs-input, needs-approval, needs-rework}` gesetzt

### When

* Workflow wird ausgeführt

### Then

1. Karte lesen (Titel, Kurzbeschreibung, Rückfragen/Feedback).
2. **Guard:** Wenn grundlegende Informationen fehlen, dann:

   * Fragen in `## Rückfragen an Hannes` ergänzen (Frage + leere Antwort)
   * Tag `needs-input` setzen, assignee=Hannes
   * **Stop** (keine Artefakte schreiben)
3. Requirement-Artefakt erzeugen:

   * `requirements/<id>-<slug>.md` nach Template schreiben (inkl. Abnahmekriterien)
   * Link in `## Links` der Karte sicherstellen
4. Status auf `REQUIREMENT` setzen
5. Tag `needs-approval` setzen, assignee=Hannes

**Skip-Kriterien:**

* mehrere `needs-*` Tags vorhanden → skip (oder needs-input mit Hinweis)
* Karte leer/ohne Titel → needs-input (Rückfrage)

---

## Workflow 2: rework_requirement

### Given

* `status = REQUIREMENT`
* Tag `needs-rework` gesetzt
* Tag `needs-approval` und `needs-input` nicht gesetzt

### When

* Workflow wird ausgeführt

### Then

1. Karte lesen; Feedback aus `## Human-Feedback` extrahieren.
2. **Guard:** Wenn kein Feedback vorhanden oder unverständlich, dann:

   * `needs-input` setzen, assignee=Hannes, konkrete Rückfrage („Bitte Feedback präzisieren…“)
   * `needs-rework` entfernen (optional; oder belassen und skip – konsistenter ist: needs-input dominiert)
   * **Stop**
3. Requirement-Artefakt überschreiben:

   * `requirements/<id>-<slug>.md` vollständig neu schreiben unter Berücksichtigung Feedback + vorhandener Antworten
4. `needs-rework` entfernen
5. `needs-approval` setzen, assignee=Hannes

---

## Workflow 3: advance_requirement_to_design

### Given

* `status = REQUIREMENT`
* keine Tags aus `{needs-input, needs-approval, needs-rework}` gesetzt

### When

* Workflow wird ausgeführt

### Then

1. Requirement lesen.
2. **Guard:** Wenn Requirement-Datei fehlt oder Link fehlt, dann:

   * `needs-input` setzen, assignee=Hannes, Rückfrage („Requirement-Link fehlt…“)
   * **Stop**
3. Design-Artefakt erzeugen:

   * `design/<id>-<slug>.md` schreiben (aus Requirement + ggf. Q/A Kontext)
   * Link in Karte sicherstellen
4. Status → `DESIGN`
5. Wenn Rückfragen entstehen:

   * `needs-input`, assignee=Hannes
     sonst:
   * `needs-approval`, assignee=Hannes

---

## Workflow 4: rework_design

### Given

* `status = DESIGN`
* Tag `needs-rework` gesetzt

### When

* Workflow wird ausgeführt

### Then

Analog zu `rework_requirement`, aber:

* Zielartefakt: `design/<id>-<slug>.md`
* Ergebnis: `needs-approval` + assignee=Hannes

---

## Workflow 5: implement

### Given

* `status = DESIGN`
* keine `needs-*` Tags gesetzt

### When

* Workflow wird ausgeführt

### Then

1. Requirement + Design lesen.
2. Status → `IMPLEMENTING`
3. Implementierung durchführen (repo-spezifisch; hier nur konzeptionell):

   * Codeänderungen
   * ggf. tests/<id>.md initialisieren/aktualisieren (Testfälle/Mapping auf AC)
4. Status → `VERIFYING`
5. **Kein Human-Gate hier erzwingen** (empfohlen), sondern unmittelbar `verify` laufen lassen oder nachgelagert triggern.

**Guard/Stop:**

* Wenn Links/Artefakte fehlen → `needs-input` + assignee=Hannes, Status bleibt `DESIGN`.

---

## Workflow 6: verify

### Given

* `status = VERIFYING`
* keine `needs-*` Tags gesetzt

### When

* Workflow wird ausgeführt

### Then

1. Requirement + Code-Kontext + (optional) Testplan lesen.
2. Tests ausführen / Verifikation durchführen (stackabhängig).
3. `tests/<id>-<slug>.md` schreiben/überschreiben:

   * Testreport (pass/fail, Nachweise, Abweichungen)
4. Tag `needs-approval` setzen, assignee=Hannes (Abnahme)

**Wenn Verifikation fehlschlägt:**

* trotzdem `needs-approval` setzen (damit du den Report siehst) **oder**
* direkt `needs-rework` setzen und assignee leer (wenn du „auto rework“ willst).
  Empfehlung: **Report zuerst zur Kenntnis** → `needs-approval`, und du entscheidest dann rework.

---

## Workflow 7: rework_after_verification

### Given

* `status = VERIFYING`
* Tag `needs-rework` gesetzt

### When

* Workflow wird ausgeführt

### Then

1. Feedback lesen.
2. Status → `IMPLEMENTING` (Änderungen am Code erforderlich)
3. `needs-rework` entfernen
4. (Optional) Implementierung direkt anstoßen oder Karte „bereit“ lassen (keine Tags), sodass `implement` beim nächsten Run greift.

---

## Workflow 8: finalize_done

### Given

* `status = VERIFYING`
* keine `needs-*` Tags gesetzt
* Testreport liegt vor und ist akzeptiert (implizit dadurch, dass du `needs-approval` entfernt hast)

### When

* Workflow wird ausgeführt

### Then

* Status → `DONE`

---

## Workflow 9: discard (human-driven)

Dieser „Workflow“ ist eine menschliche Aktion.

### Given

* beliebiger Status außer `DONE`

### When

* Human setzt Status → `DISCARDED`, entfernt `needs-*`, assignee leer

### Then

* Agenten ignorieren diese Karte in allen Selektoren

---

## Selektor-Übersicht (kompakt)

* `triage_inbox`: `status=INBOX AND no needs-*`
* `rework_requirement`: `status=REQUIREMENT AND needs-rework`
* `advance_requirement_to_design`: `status=REQUIREMENT AND no needs-*`
* `rework_design`: `status=DESIGN AND needs-rework`
* `implement`: `status=DESIGN AND no needs-*`
* `verify`: `status=VERIFYING AND no needs-*`
* `rework_after_verification`: `status=VERIFYING AND needs-rework`
* `finalize_done`: `status=VERIFYING AND no needs-*` (nach human approval)

---

