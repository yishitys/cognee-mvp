# M-Agents Hackathon Implementation Plan

This project implements the Enterprise Renewal Crisis Command Center rehearsal demo as a Streamlit single-page app backed by a five-stage multi-agent pipeline.

## Implementation Phases

1. Baseline setup: install `streamlit`, `pandas`, `rapidfuzz`, and `plotly`; keep `anthropic` and `cognee`.
2. Data and ingestion: load the six-table crisis pack, profile schema, detect missing fields, and write ingestion memory events.
3. Classification: score account risk, normalize ticket severity, tag incident-related product areas, and expose confidence summaries.
4. Reconciliation: match support tickets to canonical accounts using account ID, aliases, and fuzzy names; record conflicts.
5. Narrative: generate an executive crisis summary with Anthropic when available and deterministic fallback otherwise.
6. Command center: show timeline, memory writes/recalls, top-risk accounts, selected-account evidence, uncertainty, and 48-hour actions.
7. Rehearsal hardening: verify fallback modes, demo reset, and 90-second walkthrough readiness.

## Verification

Run:

```powershell
python tools/validate_pipeline.py
streamlit run app.py
```

Acceptance criteria:

- All six tables load with expected row counts.
- Every pipeline stage writes memory events.
- At least three downstream steps perform memory recalls.
- High-risk accounts have concrete evidence reasons.
- Missing-ID support tickets are reconciled to accounts or logged as conflicts.
- Narrative contains what happened, top accounts, uncertainty, and 48-hour actions.
