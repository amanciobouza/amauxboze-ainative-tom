# Amaux Bozé Company OS

## Start on Windows

Requires Python 3.11+, Node.js 24+, and optionally LM Studio for live execution.

```powershell
.\run-local.ps1
```

Or double-click `run-local.cmd`. The launcher sets up missing dependencies,
starts the loopback FastAPI backend on port 8000 and the Vite frontend on port
3000, then opens the browser. Ctrl+C stops both services. Add `-NoBrowser` to
keep the browser closed. Add `-Production` to build the UI and serve the entire
application from `http://127.0.0.1:8000` with one process.

Developer services can also start independently with
`scripts/run_backend.ps1` and `scripts/run_frontend.ps1`.

## Features

- Company dashboard with source/formula/window metadata and mode-separated KPIs.
- Original isometric office with eight desks, coffee area, founder launch,
  keyboard-accessible agent list, zoom/pan and reduced-motion support.
- Flat founder reporting, seven departments and shared process catalog.
- Agent profiles, Elena's direct operating style, permissions, live activity
  and paginated durable execution history.
- Versioned skill registry with input/output contracts and model requirements.
- All five existing business processes with validated inputs and provenance.
- Persisted run detail, per-attempt artifacts/model usage, timeline and recovery.
- Human approval inbox with revision checks and allowed workflow decisions.
- Controlled Obsidian Markdown browse/search/read and reviewed learning export.
- LM Studio connectivity/models, optional OpenAI/Anthropic transport and settings.
- Bounded retrospective rooms, attributed evidence, founder review, manual
  sandbox experiments and retained inconclusive evaluations.

## First workflow

Open Processes, prepare "Neue Uhr entwickeln", choose Live or Simulation and
fill the brief. Simulation uses clearly labeled demonstration artifacts; it
never publishes externally or writes the Obsidian vault. Its metrics are
separate from live metrics.

Watch Development asks for concept approval, then separate production approval.
Product Launch requires the ID of a completed production-approved Watch
Development run in the same mode. A client-provided approval flag cannot
substitute for this evidence. Holds require an explicit resume that reopens the
review gate. Failed stages offer only the active workflow's recovery commands.

## Live models and knowledge

Start LM Studio's local server on port 1234. Choose a loaded model in Settings;
an empty model selects the first returned local model. Models vary in schema
support, latency and output quality. Local transport uses LM Studio's native
JSON-schema output mode. Provider failures and incomplete/invalid JSON remain
visible; use Recovery after correcting the provider/model configuration.

OpenAI and Anthropic require explicit provider, model and standard-privacy
selection plus their environment variable in `.env`. Keys are never exposed
through the API. A local-only skill still forbids cloud execution; there is no
automatic cloud fallback. The current retrospective skills are local-only.

Configure the existing Obsidian vault in Settings (default is the repository's
documented Amaux Bozé vault). Context selection is bounded by task-specific
skill scopes and agent read permissions. Missing vault/notes are explicit;
simulation does not replace them with invented business knowledge. Exporting a
closed, reviewed live retrospective is an explicit user command through the
policy/tool gateway, with audited Markdown under `Learnings/Retrospectives/`.

## Connections and limits

Social, Shopify and community publishing adapters and commerce metric sources
are not configured by this application. Live planning and reviews work; live
publication pauses visibly at its unavailable adapter boundary. Revenue and
orders are unavailable, not fabricated zero values. Simulation action results
explicitly indicate that no external action happened.

Experiments are manually conducted in a sandbox and their evidence is recorded
by the user. Approval never edits production code, skills, policies or prices.
Software proposals need separately authorized OpenSpec implementation. Automatic
retrospective triggers, multi-user authentication and SaaS hosting remain future
scope, as in the original control-plane proposals.

## Persistence and recovery

`.runtime/runtime.sqlite` stores operational metadata/events/commands and
`.runtime/checkpoints.sqlite` stores LangGraph checkpoints. Stop the app before
backing up these files together. Neither database is organizational knowledge.
Repository and engine boundaries support future PostgreSQL adapters.

The current worker runs one workflow at a time and does not execute live
external side effects. Interrupted model stages can be recovered from the
durable graph. Commands carry persistent identities; approvals use revision
compare-and-set. Persisted SSE event IDs support replay on reconnect. The UI
also polls authoritative snapshots and marks disconnected Office activity unknown.

## Verify

```powershell
.venv\Scripts\python.exe scripts/validate_openspec.py
.venv\Scripts\python.exe -m pytest -q
cd web
npm test
npm run build
```

With the app running:

```powershell
.venv\Scripts\python.exe scripts/smoke_app.py --channel msedge
```

The browser smoke test creates only simulation work, verifies all main routes,
launches and approves a two-gate Watch Development run, closes a retrospective
experiment and checks mobile layout. Screenshots are saved in `.runtime/screenshots`.
CI runs the Python suite, UI tests/build and Chromium browser acceptance, and
uploads screenshots. Remote CI results require a pushed branch; local execution
does not imply that GitHub CI has run.

## Agentensprache

Unter **Einstellungen ? Sprache der Agenten** kann Deutsch oder English gew?hlt werden. Deutsch ist der Standard, auch f?r bestehende Installationen. Die gespeicherte Sprache gilt f?r neue Live-Ausf?hrungsabschnitte aller Agenten und Retrospektiven bei jedem Modellanbieter. Bereits erzeugte Ergebnisse und Simulationsbeispiele werden nicht nachtr?glich ?bersetzt. JSON-Schl?ssel, Enum-Werte und Quellen bleiben unver?ndert.
