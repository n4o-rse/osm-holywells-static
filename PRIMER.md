# PRIMER — osm-holywells-static

Arbeitsplan für `n4o-rse/osm-holywells-static` (Repo-Name: Vorschlag 2026-11-01). Wird zu Beginn jedes Chats hochgeladen (Bundle, siehe A5) und am Ende zurückgeschrieben. Stand: 2026-11-01 (S0: Festlegungen, Befunde; S1: Skeleton; S2: Modell aus `osm-benchmarks-static`).

Sprache: dieses Dokument ist deutsch, alles andere im Repo (Code, Kommentare, README) ist britisches Englisch.

---

## Teil A — Immer gültig

### A1 Ausgangslage

| Repo | Rolle | Stand |
|---|---|---|
| `Research-Squirrel-Engineers/osm2lod` | Prototyp: Overpass-Abfrage je Export-Typ, CSV, TTL und QuickStatements je Lauf; liefert hier die Abfragen | vorhanden, wird nicht umgebaut |
| `n4o-rse/wikibase-static` | Paket (v0.24.1): CSV (vier Tabellen) → Wikibase-JSON → Seiten, RDF, SPARQL; Verb `import-osm`; BeaverBridge-Design mit hell/dunkel | vorhanden; Änderungen für dieses Repo: S3 |
| `n4o-rse/osm-benchmarks-static` | Vorbild: Site-Repo mit den Benchmarks (23 Nodes, live); Modell, Skeleton, Workflow, Abfragen werden von dort übernommen | vorhanden, S0 bis S8 erledigt |
| `n4o-rse/osm-holywells-static` | dieses Repo | neu, S0 bis S2 gebaut |
| `n4o-rse/osm-ogham-static` | Schwester-Site für Ogham-Steine (gleiche Abfrage-Gebiete, gleiches Modell) | neu, wird gleichzeitig angelegt |

Nicht neu zu bauen: das Modell (P100 bis P113), `import-osm`, Seiten, RDF, SPARQL-Seite, `check-crm` (kommen aus `osm-benchmarks-static` und dem Paket).

**Befunde** (geprüft 2026-11-01, soweit nicht anders gesagt):

1. **osm2lod, Ist-Stand `holywells`** (Lauf 2026-03-28, aus `dist/2026-03-28/`): 736 Elemente (709 Nodes, 27 Ways). Die Summe der aktuellen Versionsnummern ist der Umfang der Historie: 2282 Versionen (höchste Version 15). Die Schwester-Menge `ogham` hat kein gemeinsames Element mit dieser (0 gemeinsame Typ/ID-Paare).
2. **Die Abfrage** (aus `metadata_holywells_*.json`, `out meta geom;` und 25 s dort; hier `out meta;` und 180 s wie bei den Benchmarks). Gebiete sind die Areas der Relationen Irland (62273) und Nordirland (156393), anders als bei den Benchmarks ohne Schottland:

   ```
   [out:json][timeout:180];
   ( area(3600062273)->.roi; area(3600156393)->.ni; );
   ( nwr(area.roi)["place_of_worship"="holy_well"]; nwr(area.ni)["place_of_worship"="holy_well"]; );
   out meta;
   ```

   Die Dateien stehen unter `data/seeds/` (`overpass-holywells.overpassql`, `holywells.csv`).
3. **Tags** (aktueller Stand im Lauf 2026-03-28): 645 von 736 mit `name`, 141 mit `wikidata`, 36 mit `wikimedia_commons`. Ohne `name` greifen die Rückfälle der Etiketten (`name:en`, Commons-Titel, Inschrift, `OSM node <id>`): bei 91 Elementen.
4. **Paket v0.24.1, Grenzen** (im Quelltext geprüft, `step_import_osm.py` und `crm.py`): (a) die Beschreibungstexte sind fest eingebaut („Benchmark“/„Höhenmarke“ als Rückfall, Tabelle `THINGS`): Holy Wells würden als „Benchmark (OpenStreetMap node …)“ beschrieben; (b) `crm.py` kennt `crm:E22_Human-Made_Object`, aber nicht `crm:E26_Physical_Feature`: eine Klasse ohne Eintrag in `CLASSES` wird ohne Oberklasse geschrieben (`check-crm` meldet trotzdem keinen Verstoß, Test unten). Der Auswahlname ist `benchmarks`, solange `--selection` fehlt; hier setzt `main.py` `--selection holywells` selbst. Eine Klasse und eine Auswahl je Site, wie bei den Benchmarks, reichen hier; die Mehrfach-Auswahl ist nicht nötig.
5. **Umfang des Harvests.** 736 Elemente, dazu 27 Ways, deren Stützpunkte ebenfalls geholt werden (`data/raw/osm/members/`). Mit 100 History-Anfragen je Lauf und einer Sekunde Pause sind es mindestens 8 Läufe, plus die Stützpunkte der Ways (`--member-limit`). Overpass und die OSM-API sind aus der Sandbox dieses Chats nicht erreichbar (geprüft 2026-11-01, keine Verbindung); der Harvest läuft bei Flo, wie bei den Benchmarks.
6. **Ways.** Die Benchmarks haben nur Nodes; der Echttest der Way-Geometrie (S6 dort, zurückgestellt) ist hier mit 27 Ways möglich.
7. **Skeleton ohne Daten** (geprüft 2026-11-01 mit `wikibase-static` v0.24.1): `python main.py --strict` läuft mit den Modelldateien (4 Klassen: Q1 bis Q3 und Q100; 24 Properties, 60 Statements) zweimal mit Exit-Code 0 durch; nach dem Einchecken von `data/derived/`, `dist/` und `docs/` ist `git status` leer, auch nach einem dritten Lauf. `check-crm` meldet 0 Verstöße, `check_attribution.py` findet „OpenStreetMap contributors“ in 63 Dateien. Anders als bei den Benchmarks in S1 (ohne Modell: „nothing to do“) erzeugt der Lauf also schon Seiten für die Modell-Entitäten. Ohne `queries.yaml` scheitert `--strict` an der Standardabfrage `coordinates` (keine Zeilen, WARN): `requires: [globe-coordinate]` prüft den Datentyp der Property P110, nicht ob es Statements gibt. Deshalb liegt eine vorläufige `queries.yaml` (Standardsatz ohne `coordinates`) im Repo, die mit dem ersten Harvest gelöscht wird.

---

### A2 Zielbild

```
 data/seeds/overpass-holywells.overpassql + data/seeds/holywells.csv     (Abfrage und Tag-Bedingung, aus osm2lod)
         │
         │ import-osm   (Verb mit Netz, nie im Standardlauf)
         ▼
 Overpass  ──►  data/raw/osm/overpass/<name>.json        Elemente und aktuelle Versionen
 OSM API   ──►  data/raw/osm/history/<type>_<id>.json   volle Historie (nur bei Versionsabweichung)
         │         data/raw/osm/members/                 Historien der Stützpunkte von Ways
         │ import-osm --offline  +  data/csv/mapping/osm-properties.csv
         ▼
 data/csv/  entities.csv  statements.csv  qualifiers.csv  references.csv  idmap.csv     data/crm.csv  (Holy well → crm:E26)
         │ from-csv → load → build → search → rdf → sparql
         ▼
 docs/  (GitHub Pages: Seiten, Karte, Suche, SPARQL)      dist/*.ttl  (DCAT 3, GeoSPARQL, CIDOC CRM)
```

Eine QID je OSM-Element, die Versionen als Statements daran; das Beispiel mit den Statements und Qualifiern steht in A2 von `osm-benchmarks-static`.

Die Ergebnisse müssen diese Eigenschaften haben, jede ist prüfbar:

1. Jedes Element hat genau eine QID; es gibt keine Versions-Items.
2. Zahl der OSM-Version-Statements je Element = Zahl der Versionen in der API-History.
3. Jede QID ist über `data/crm.csv` auf eine CRM-Klasse verankert; `check-crm` meldet keinen Verstoß.
4. Das RDF enthält kein `owl:sameAs` auf OpenStreetMap; die Statement- und Wert-IRIs sind reine Bezeichner im eigenen Namensraum.
5. Zweimal laufen lassen ändert nichts (`git status` leer); ein zweiter Harvest ohne Änderung bei OSM stellt nur die Overpass-Anfrage.


### A3 Querschnittsregeln

- Rohdaten liegen unter `data/raw/`, unverändert wie erhalten, nicht von Hand ändern. Was ein Skript daraus macht, geht nach `data/csv/`, `data/derived/`, `dist/` oder `docs/`.
- Wiederverwendung heißt kopieren, nicht referenzieren. Das Modell (P100 bis P113) ist aus `osm-benchmarks-static` kopiert und bleibt dort wie hier gleich; Abweichungen stehen in A4.
- **Keine Uhr im Output.** Kein Generator ruft `datetime.now()` auf. Zeitangaben stammen aus den Quelldaten (Zeitstempel der OSM-Versionen) oder aus `RELEASE_DATE`.
- **Zeilenenden LF** (`.gitattributes`: `* text=auto eol=lf`).
- **Zweimal laufen lassen, `git status` bleibt sauber.**
- **Netzwerk nur im Verb `import-osm`.** Alles andere läuft offline gegen `data/raw/`; das Verb gehört nie zum Standardlauf.
- **Höflicher Harvest.** Ehrlicher User-Agent mit Kontaktadresse (`--contact`), mindestens eine Sekunde Pause zwischen Requests an die OSM API, `Retry-After` beachten, Overpass nur mit einer Abfrage zur Zeit; die OSM-Nutzungsregeln gelten.
- **Die Seiten zeigen, was die Quelle sagt.** Werte werden formatiert, nicht repariert.
- **Lizenz und Namensnennung.** Die Daten sind OpenStreetMap-Daten (ODbL 1.0, „© OpenStreetMap contributors“); der Hinweis steht auf jeder Seite und im RDF.
- Befehle für Windows `cmd`, jeder in **einer** Zeile, zusammengehörige Befehle mit `&&` verkettet.
- Mermaid-Diagramme nutzen das feste Farbschema der Familie (Subject/Object grau, RealObject dunkelgrün, Class dunkelorange, Term dunkelviolett, OWL weiß, PropMeta amber).

### A4 Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Zweck | Statische Wikibase (GitHub Pages) für holy wells (`place_of_worship=holy_well`) in Irland und Nordirland; Weiterentwicklung von osm2lod wie bei den Benchmarks | 2026-11-01 |
| Repo-Zuschnitt | **Ein Repo je Typ**: `holywells`, `ogham` und `sisal` sind drei getrennte Site-Repos (`osm-holywells-static`, `osm-ogham-static`, `osm-sisal-static`); jedes hat eine Klasse und eine Auswahl wie `osm-benchmarks-static` | 2026-11-01 |
| Repo-Name und Ort | `n4o-rse/osm-holywells-static`, lokal `C:\git\osm-holywells-static` | Vorschlag 2026-11-01 |
| Klasse, ID | Q100 „Holy well“ (de „Heilige Quelle“), `subclass of` Q3; Properties P100 bis P113 wie bei den Benchmarks; Rolle `class_benchmark` = Q100 | Vorschlag 2026-11-01 |
| CRM-Anker | Holy well → `crm:E26` Physical Feature, über `data/crm.csv`; so steht es in osm2lod (`entityBaseClass`). Ein Holy Well ist oft eine gefasste Quelle (E25 wäre möglich); nach Prüfung entscheiden. `crm:E26` sollte für die Kette zu `crm:E18` einen Eintrag im Paket bekommen (S3). | Vorschlag 2026-11-01 |
| Auswahl | Name `holywells`; Tag-Bedingung `place_of_worship=holy_well`; Dateien `data/seeds/holywells.csv` und `data/seeds/overpass-holywells.overpassql` | 2026-11-01 |
| Auswahlname | `main.py` hängt bei `import-osm` `--selection holywells` an, wenn es fehlt (das Paket nimmt sonst `benchmarks`); die einzige Abweichung von `main.py` der Benchmarks | 2026-11-01 |
| Logo | Das Logo (`assets/logo.png`) ist die Zeichnung des Quellbrunnens mit Steinkreuz | Vorschlag 2026-11-01 |
| Modell | Wie `osm-benchmarks-static`, **1:1**: eine QID je OSM-Element, Versionen als Statements, Eintrittsmarker, Geometrie-Verlauf als WKT, Tags nur aktuell als `key=value`; Properties P100 bis P113 mit denselben IDs, Namen und Datentypen; Rolle → ID in `data/csv/mapping/osm-properties.csv`. Alle übrigen Beschlüsse der A4 dort (Identität, Versionen, Historie, Quelle, Austritt, Geometrie, Datentypen, Benutzername und uid, Label, URIs, Verb) gelten hier unverändert | 2026-11-01 |
| Seeds | Die Abfrage steht als Datei unter `data/seeds/overpass-<name>.overpassql`, aus osm2lod übernommen; geändert nur `out meta geom;` → `out meta;` (das Paket baut die Geometrie selbst) und das Zeitlimit 25 → 180 s (wie bei den Benchmarks). Die Tag-Bedingung steht als `data/seeds/<name>.csv` | 2026-11-01 |
| Lizenz | ODbL 1.0 mit „© OpenStreetMap contributors“ in `site.yaml` (`license`); der Code unter MIT; das Logo unter CC BY 4.0 (Vorschlag, siehe Teil D) | Vorschlag 2026-11-01 |
| URIs | Eigener Namensraum im github.io-Raum des Repos (`rdf_base`), eigene Präfixfamilie (`rdf_prefix`); kein `owl:sameAs` und kein `skos:exactMatch` auf OSM | Vorschlag 2026-11-01 |
| Skeleton | Wie `osm-benchmarks-static` (S1): dünnes `main.py` (setzt `WBS_ROOT`), `site.yaml`, `requirements.txt` auf `wikibase-static` v0.24.1, `update.cmd`, `check_attribution.py`, Workflow-Aufrufer mit `deploy: false`, bis die ersten Daten da sind | 2026-11-01 |
| Paket | Das Paket in v0.24.1 kann nur **eine** Klasse je Site, **eine** Auswahl je Lauf und fest eingebaute Beschreibungswörter (Befund 4); das Ändern ist Schritt S3 im Paket-Repo, nicht hier | 2026-11-01 |

### A5 Was in welchem Chat hochgeladen wird

Ein Bundle statt Einzeldateien. Mitnehmen: `PRIMER.md`, Quelltexte, kleine Daten (`data/raw/osm/`). Nicht mitnehmen: `.git/`, `.venv/`, `config.local.*`, große erzeugte Dateien.

```cmd
robocopy . ..\osm-holywells-static-bundle /E /XD .git .venv __pycache__ build /XF config.local.ini config.local.json >nul & powershell -NoProfile -Command "Compress-Archive -Path ..\osm-holywells-static-bundle\* -DestinationPath ..\osm-holywells-static-bundle.zip -Force"
```

(robocopy meldet Erfolg mit Exit-Code unter 8, das ist normal.) Das Paket `wikibase-static` und `osm-benchmarks-static` klont Claude selbst von GitHub. Ein Chat im Paket-Repo (S3) bekommt dessen PRIMER und dessen Bundle.

### A6 IRI-Landkarte

Alles `geplant`, bis die erste Veröffentlichung die Basis festlegt. Vorschlag: `rdf_base` = `https://n4o-rse.github.io/osm-holywells-static`, `rdf_prefix` = `ohs`.

| Pfad | Inhalt | Ziel des Redirects | Status |
|---|---|---|---|
| `<base>/entity/<ID>` | Konzept-URI eines Elements (Weiterleitungsseite) | – | geplant |
| `docs/ttl/<ID>.ttl`, `docs/json/<ID>.json` | ein Element als Turtle bzw. JSON | – | geplant |
| `docs/downloads/<host>.ttl` | RDF aller Entitäten, beschrieben mit DCAT 3 | – | geplant |
| `docs/sparql.html`, `docs/query.html` | Query-Seite und Editor | – | geplant |
| w3id-Präfix | offen, wie im Paket vorerst keines | offen | geplant |

---

## Teil B — Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S0 | Festlegungen, Abfrage aus osm2lod, Befunde | osm-holywells-static | – | erledigt 2026-11-01 |
| S1 | Skeleton: Layout, `main.py`, `site.yaml`, `requirements.txt`, Lizenz, Citation, Workflow-Aufrufer, `update.cmd`, Logo | osm-holywells-static | S0 | gebaut 2026-11-01 (Patch-ZIP; Einspielen offen) |
| S2 | Modell: Klasse, Properties P100 bis P113, `data/crm.csv`, Mapping-Datei, Seeds | osm-holywells-static | S1 | gebaut 2026-11-01 (Patch-ZIP; Einspielen offen) |
| S3 | Paket 0.25.0: Beschreibungswörter je Klasse statt der festen Tabelle, `crm:E26` in der Klassentabelle (gemeinsam für alle drei neuen Site-Repos) | wikibase-static | S2 | offen |
| S4 | Erstharvest: 736 Elemente, Overpass, Historien (mehrere Läufe), Import, Seiten, RDF, `check-crm` | osm-holywells-static | S3 | offen |
| S5 | Echttest der Way-Geometrie an den 27 Ways (der zurückgestellte S6-Test der Benchmarks) | osm-holywells-static | S4 | offen |
| S6 | Standardabfragen (`queries.yaml`): Versionen je Element, Eintrittsversion, Wikidata-Verknüpfungen, Bilder | osm-holywells-static | S4 | offen |
| S7 | Pages-Workflow scharf (`deploy` an, `check_attribution.py`), ODbL-Hinweis, CI mit `--strict` zweimal | osm-holywells-static | S4 | offen |

S1 und S2 sind in einem Patch. S3 ist ein Chat im Paket-Repo für alle drei neuen Sites; der Harvest (S4) läuft technisch auch mit 0.24.1, bekäme aber falsche Beschreibungen („Benchmark …“), also nicht committen. S5 hängt nur an den ersten Ways.

---

## Teil C — Die Schritte

### S1 und S2 — Skeleton und Modell

**Ziel:** Ein Site-Repo nach dem Muster von `osm-benchmarks-static`, das mit `python main.py` ohne Daten sauber durchläuft und das Modell enthält.

**Uploads:** keine; Claude klont `osm-benchmarks-static` und osm2lod selbst.

Inhalt: Dateien wie bei den Benchmarks (S1 und S2 dort); neu sind die Klasse Q100 in `data/csv/entities.csv`, eine Zeile in `data/crm.csv`, `data/seeds/holywells.csv` und `data/seeds/overpass-holywells.overpassql`. `main.py` setzt bei `import-osm` die Auswahl `holywells`. Der Workflow-Aufrufer hat `deploy: false` und prüft nur `python main.py --strict`; `check_attribution.py` ist da, läuft aber erst mit S7. Die `queries.yaml` ist vorläufig (Standardabfragen ohne `coordinates`, siehe Befund 7) und wird mit dem ersten Harvest gelöscht.

**Abnahme:** `python main.py --list` nennt die Schritte; `python main.py --strict` läuft ohne Daten durch; zwei Läufe hintereinander, `git status --porcelain` leer; `python main.py --strict check-crm` ohne Verstoß.

### Erledigt 2026-11-01 (S1, S2)

Gebaut: Dateien wie `osm-benchmarks-static` (`main.py`, `requirements.txt` auf v0.24.1, `site.yaml`, `LICENSE`, `CITATION.cff`, `update.cmd`, `check_attribution.py`, `.github/workflows/site.yml`, `README.md`), dazu das Modell (`data/csv/`, `data/crm.csv`, `data/csv/mapping/osm-properties.csv`), die Seeds (`data/seeds/`), das Logo und die vorläufige `queries.yaml` (Befund 7). Abnahme in einer frischen Kopie: `--list` nennt neun Einträge (sechs im Standardlauf, drei Verben), `--strict` zweimal und ein drittes Mal mit Exit-Code 0, `git status` leer, `check-crm` 0 Verstöße, `check_attribution.py` grün; `main.py` reicht `--selection` an `import-osm` weiter (mit einer Attrappe für den Aufruf geprüft, nicht mit Netz). Die Properties P100 bis P113 sind bis auf den Beispieltext in P107 und P109 gleich denen der Benchmarks (verglichen). Nicht geprüft: der Lauf des Workflows auf GitHub, `update.cmd` unter Windows, Overpass und OSM-API (kein Netz), die Seiten im Browser. Der Patch bringt kein `docs/`, `dist/` und `data/derived/` mit; sie entstehen beim ersten Lauf und werden mit eingecheckt.

### S3 — Paket 0.25.0

**Ziel:** Die Beschreibungen der Items sagen, was sie sind, und `crm:E26` hat seine Oberklasse.

**Uploads:** das Bundle von `wikibase-static` (PRIMER dort); dieses PRIMER.

Vorschlag zum Zuschnitt, vor dem Bauen als Formular zu bestätigen: die Beschreibungswörter je Klasse (englisch und deutsch, z. B. „Holy well“/„Heilige Quelle“) kommen aus `entities.csv` oder den Seeds statt aus der festen Tabelle `THINGS`; der Rückfall der Benchmarks bleibt, damit `osm-benchmarks-static` unverändert baut. `crm:E26_Physical_Feature` (Oberklasse `crm:E18_Physical_Thing`) kommt in die Klassentabelle. Der Auftrag gilt gleichzeitig für `osm-holywells-static`, `osm-ogham-static` und `osm-sisal-static`.

**Abnahme:** Tests im Paket; in einer Kopie dieses Repos mit einem Probe-Element trägt das Item die richtige Beschreibung, `check-crm` meldet keinen Verstoß; `osm-benchmarks-static` baut mit der neuen Version byteweise gleich.

### S4 bis S7

Wie die Schritte S5 bis S8 von `osm-benchmarks-static` (dort ausführlich und mit Befunden): Harvest mit Netz (`python main.py import-osm --probe --contact <Adresse>` zuerst, dann ohne `--probe`, bei Flo), Import, Seiten, `check-crm`, danach die Abfragen und die Veröffentlichung. Besonderheiten hier:
- **S4** Abnahme: 736 Elemente (oder die Zahl der heutigen Overpass-Antwort), Zahl der Version-Statements je Element = Zahl der Versionen der API-History (Summe 2282 am 2026-03-28, heute gleich oder höher), jede Historie vollständig, zweiter Lauf stellt nur die Overpass-Anfrage; `queries.yaml` gelöscht.
- **S5** an den Ways: Geometrie-Verlauf als WKT, Karte, GeoSPARQL; Abnahme: ein Way mit mehreren Geometriestand zeigt sie in der Reihenfolge der Versionen; die Zahl der Requests (Stützpunkte) ist notiert.
- **S7** `deploy: false` entfernen und `&& python check_attribution.py` im Aufrufer ergänzen.

---

## Teil D — Offene Punkte

- **Repo-Name und Organisation:** `osm-holywells-static` unter `n4o-rse` ist ein Vorschlag. Alternative: ein gemeinsames Repo für Holy Wells und Ogham-Steine (verworfen 2026-11-01: je Typ ein Repo).
- **Logo:** Autor und Lizenz auch dieser Zeichnung klären (bei den Benchmarks: Florian Thiery, mit ChatGPT erzeugt, CC BY 4.0; das README nennt das hier ebenso, bis es bestätigt ist).
- **CRM-Klasse der Holy Wells:** `crm:E26` (wie osm2lod), `crm:E25` (gefasste Quelle) oder beides je nach Tag (`man_made`, `natural`)? Zu entscheiden mit S3, bevor Daten importiert werden.
- **Eintrittsregel:** Die Bedingung `place_of_worship=holy_well` kann in einer frühen Version fehlen (Element zuerst als `amenity=…` getaggt; `was:…`-Tags in den Daten zeigen, dass es solche Fälle gibt). Der Eintrittsmarker zeigt dann die Version, ab der sie gilt. In S4 an den Daten prüfen.
- **Gebiet:** Irland und Nordirland sind die Areas aus osm2lod; Schottland, Wales und die Insel Man hätten weitere Elemente, sind aber nicht Teil der Abfrage. Entscheiden, ob die Abfrage gleich bleibt (1:1 mit osm2lod) oder erweitert wird.
- **Weitere Typen aus osm2lod** (`ci`, `drillcores`, `romansites`): je ein eigenes Repo nach demselben Muster, nach S3.
- **Netz:** `import-osm` ist hier noch nicht gelaufen; beim ersten Lauf `--contact` setzen und die Pause prüfen.
