# Cognee MVP: Enterprise Renewal Crisis Command Center

A Streamlit hackathon MVP that demonstrates a memory-native agent workflow for an enterprise renewal crisis. The app ingests fragmented CRM, product usage, support, and incident data; scores at-risk accounts; reconciles messy account identities; and produces an executive action package with a visible memory event trail.

The project is designed to run in two modes:

- **Local-first demo mode:** no external API keys required. The pipeline uses deterministic local memory events and a template narrative.
- **External-service demo mode:** optional Cognee memory writes and optional Anthropic narrative generation can be enabled from the Streamlit sidebar.

Repository: [github.com/yishitys/cognee-mvp](https://github.com/yishitys/cognee-mvp)

## Table of Contents

- [Why This Exists](#why-this-exists)
- [What The Demo Shows](#what-the-demo-shows)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Run The Apps](#run-the-apps)
- [Demo Walkthrough](#demo-walkthrough)
- [Data](#data)
- [Validation](#validation)
- [Git LFS](#git-lfs)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

## Why This Exists

Enterprise teams often have customer risk signals scattered across CRM records, product usage logs, incident history, and support tickets. This MVP turns those disconnected tables into an explainable command center:

1. Load and profile operational data.
2. Classify account renewal risk.
3. Reconcile incomplete or alias-only account references.
4. Generate an executive narrative and 48-hour action plan.
5. Show every memory write and recall event so the agent handoff is inspectable.

The result is not a production churn model. It is a working prototype for showing how memory, entity resolution, evidence trails, and executive workflow can fit together in a live sponsor demo.

## What The Demo Shows

- **Five-agent workflow:** ingestion, classification, reconciliation, narrative, and demo surface.
- **Explainable risk scoring:** renewal timing, ARR exposure, workflow drop, API error spikes, high-severity tickets, incident-related product areas, and open opportunity exposure.
- **Entity reconciliation:** support tickets with missing account IDs are matched to canonical accounts by account ID, exact alias, or fuzzy name matching.
- **Memory-native handoff:** each stage writes structured context and later agents recall prior outputs before acting.
- **Fallback reliability:** the main demo runs without external services, then can optionally prove Cognee and LLM paths.
- **Executive output:** top-risk accounts, evidence drill-downs, action items, open questions, and quality flags.

## Architecture

```text
CSV crisis pack
    |
    v
Ingestion Agent
    - load six operational tables
    - profile schema, row counts, date ranges, missingness
    - write dataset profile and quality findings to memory
    |
    v
Classification Agent
    - recall ingestion context
    - score account renewal risk
    - normalize ticket severity
    - write risk baseline and confidence summary to memory
    |
    v
Reconciliation Agent
    - recall schema and classification baseline
    - resolve support tickets to canonical accounts
    - write canonical entities, match decisions, and conflicts to memory
    |
    v
Narrative Agent
    - recall prior stage outputs
    - generate executive summary, actions, and uncertainty
    - optionally use Anthropic when configured
    |
    v
Streamlit Command Center
    - risk table
    - top account radar
    - evidence drill-down
    - action package
    - raw memory event log
```

### Core Modules

| Module | Purpose |
| --- | --- |
| `app.py` | Main Streamlit command center UI. |
| `src/data_loader.py` | Loads and normalizes the default crisis-pack CSV tables. |
| `src/pipeline.py` | Runs the five-agent pipeline and risk/evidence logic. |
| `src/memory.py` | Provides local memory event logging and optional Cognee writes. |
| `src/models.py` | Dataclasses for memory events, risk scores, profiles, and pipeline output. |
| `tools/validate_pipeline.py` | End-to-end validation for data loading, risk labels, reconciliation, and narrative output. |
| `demos/cognee_mvp/app.py` | Minimal Cognee loop demo focused on remember/recall behavior. |

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- .env.example
|-- .gitattributes
|-- .gitignore
|-- Command Center (standalone).html
|-- demo_materials/
|   |-- m_agents_rehearsal/
|   |   `-- assembled_crisis_pack/
|   |       |-- accounts.csv
|   |       |-- contacts.csv
|   |       |-- opportunities.csv
|   |       |-- usage_events.csv
|   |       |-- support_tickets.csv
|   |       `-- incident_log.csv
|   |-- retail_sales_forecasting/
|   `-- customer_churn/
|-- demos/
|   `-- cognee_mvp/
|-- docs/
|-- scripts/
|-- src/
`-- tools/
```

Ignored local/runtime paths include `.env`, `.venv/`, `.cache/`, `.data_storage/`, `.cognee_system/`, `.cognee_cache/`, and Python cache folders.

## Quick Start

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Python 3.12 is the known-good target for this project. Python 3.11 should likely work, but it has not been the primary local verification target.

## Environment Variables

Copy `.env.example` to `.env` before running local demos.

### Local-Only Mode

No real API keys are required for the default demo path. Keep the sidebar toggles off:

- `Use Cognee memory writes`: off
- `Use Anthropic narrative`: off

The app will still load data, score accounts, reconcile tickets, generate a template narrative, and show memory events.

### Optional Cognee Memory

`.env.example` includes Cognee-related provider and storage settings:

```env
LLM_PROVIDER=openai
LLM_MODEL=openai/gpt-5-mini
LLM_API_KEY=your_api_key_here

EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=openai/text-embedding-3-large
EMBEDDING_API_KEY=your_api_key_here

DATA_ROOT_DIRECTORY=C:/path/to/project/.data_storage
SYSTEM_ROOT_DIRECTORY=C:/path/to/project/.cognee_system
CACHE_ROOT_DIRECTORY=C:/path/to/project/.cognee_cache

GRAPH_DATABASE_PROVIDER=ladybug
VECTOR_DB_PROVIDER=lancedb
DB_PROVIDER=sqlite
```

Important: update the three absolute Cognee directory paths for your local checkout before enabling Cognee.

If Cognee is unavailable or times out, `src/memory.py` records a `local-fallback` event and the demo continues.

### Optional Anthropic Narrative

To enable LLM-generated executive narrative text, add:

```env
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
ANTHROPIC_TIMEOUT_SECONDS=20
```

Then enable `Use Anthropic narrative` in the Streamlit sidebar.

## Run The Apps

### Main Command Center

```powershell
streamlit run app.py
```

With an explicit port:

```powershell
streamlit run app.py --server.port 8506
```

### Minimal Cognee MVP

This smaller demo focuses only on the remember/recall loop:

```powershell
streamlit run demos/cognee_mvp/app.py --server.port 8507
```

### Standalone HTML Artifact

`Command Center (standalone).html` is a static visual artifact of the command center. It is useful for quick review or backup presentation, but the live Streamlit app is the primary demo.

## Demo Walkthrough

Suggested live flow:

1. Start with both external toggles off.
2. Click `Run Five-Agent Pipeline`.
3. Walk through the five-agent handoff map and point out memory writes/recalls.
4. Use the risk table to identify critical and high-risk accounts.
5. Select a critical account in the evidence drill-down.
6. Show the support trail, revenue exposure, and dataset proof tabs.
7. Open the executive action package and read the top actions.
8. Show the memory tab or raw memory events to demonstrate traceability.
9. Optionally rerun with Cognee or Anthropic enabled if API credentials are configured.

The strongest judging point is that the app does not just produce a score. It exposes the evidence chain that led to the score and turns that evidence into action.

## Data

The main app uses:

```text
demo_materials/m_agents_rehearsal/assembled_crisis_pack/
```

Required tables:

| Table | Role |
| --- | --- |
| `accounts.csv` | Canonical account list, ARR, segment, renewal date, owner, and region. |
| `contacts.csv` | Account contacts for GTM context. |
| `opportunities.csv` | Open and historical revenue exposure. |
| `usage_events.csv` | Product usage, workflow completion, active users, and API errors. |
| `support_tickets.csv` | Support volume, severity, status, account references, and product areas. |
| `incident_log.csv` | Incident timeline and affected product areas. |

Additional demo datasets are included for experimentation:

- `demo_materials/retail_sales_forecasting/`
- `demo_materials/customer_churn/`
- `demo_materials/m_agents_rehearsal/` source and assembled variants

The retail forecasting dataset is large and is tracked with Git LFS.

## Validation

Run the deterministic pipeline check:

```powershell
python tools/validate_pipeline.py
```

Expected result:

```text
Pipeline validation passed.
```

Compile check:

```powershell
python -m compileall app.py src tools demos
```

The validation script checks:

- all six default CSV tables load
- expected row counts are present
- account-name normalization works
- the pipeline creates memory write/read events
- multiple risk labels are produced
- top accounts include evidence reasons
- ticket reconciliation match rate is above 90 percent
- narrative output includes top accounts, actions, and uncertainty

## Git LFS

Some files in `demo_materials/retail_sales_forecasting/` are larger than GitHub's regular file limit. They are tracked with Git LFS through `.gitattributes`:

```text
demo_materials/retail_sales_forecasting/raw/*.csv filter=lfs diff=lfs merge=lfs -text
demo_materials/retail_sales_forecasting/*.zip filter=lfs diff=lfs merge=lfs -text
```

If you clone the repo and need the large dataset files:

```powershell
git lfs install
git lfs pull
```

If you only want to run the main command center, the default assembled crisis pack is enough.

## Troubleshooting

### Streamlit cannot find modules

Run commands from the project root and activate the virtual environment first:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

### Missing data files

The main app expects:

```text
demo_materials/m_agents_rehearsal/assembled_crisis_pack/
```

Run:

```powershell
python tools/validate_pipeline.py
```

to confirm all required files are present.

### Cognee path errors

Cognee 1.1.x expects absolute storage paths. Edit `.env` and update:

```env
DATA_ROOT_DIRECTORY=
SYSTEM_ROOT_DIRECTORY=
CACHE_ROOT_DIRECTORY=
```

to match your local project path.

### External service failure during demo

Turn off the external toggles in the Streamlit sidebar:

- `Use Cognee memory writes`
- `Use Anthropic narrative`

The demo is intentionally built to keep running with local fallback behavior.

### Large files did not download after clone

Install and pull Git LFS:

```powershell
git lfs install
git lfs pull
```

## Roadmap

Potential next steps:

- Replace the rules-based risk score with a trained, validated renewal-risk model.
- Add source-level citations to every executive action.
- Expand Cognee recall from write-event visibility into richer semantic retrieval.
- Add role-specific views for Sales, Customer Success, Support, and Leadership.
- Add a production data connector layer for CRM, support, product analytics, and incident systems.
- Package the Streamlit app for hosted deployment.

## Security And Collaboration Notes

- Do not commit `.env`.
- Do not commit local virtual environments, Cognee state, cache folders, or generated runtime artifacts.
- Use `.env.example` and `docs/environment_setup.md` for teammate setup.
- Keep external-service toggles off for first rehearsal, then enable one at a time.
- Review large dataset needs before pushing additional raw files.

