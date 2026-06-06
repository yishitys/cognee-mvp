# Mock Rehearsal Brief

## Scenario

You are the response team for a B2B SaaS company. In the last 14 days, enterprise renewals dropped, support escalations spiked, and several strategic accounts reduced product usage after a reliability incident.

Build a working product demo that helps leadership answer:

- Which accounts are at highest renewal risk?
- Which support incidents are linked to which accounts and product areas?
- Which records are duplicates or aliases that must be reconciled?
- What narrative should the executive team use in the next operating review?
- What actions should customer success, support, and GTM teams take first?

## Available Synthetic Dataset

Create or simulate these CSV files:

- `accounts.csv`: account_id, account_name, segment, arr, renewal_date, owner, region
- `contacts.csv`: contact_id, account_id, name, title, email, linkedin_url
- `usage_events.csv`: account_id, date, active_users, api_errors, core_workflows_completed
- `support_tickets.csv`: ticket_id, account_name, contact_email, product_area, severity, status, created_at, summary
- `opportunities.csv`: opportunity_id, account_name, stage, amount, close_date, next_step
- `incident_log.csv`: incident_id, start_time, end_time, product_area, customer_impact, root_cause

Intentionally include:

- Duplicate account names.
- Slightly different company aliases.
- Missing account IDs in some support tickets.
- Conflicting severity labels.
- A few high-ARR accounts with usage drops.

## Required Pipeline

### 1. Ingestion

Load CSVs, profile schema, detect missing fields, and write source metadata to Cognee.

Output:

- Dataset profile.
- Data quality findings.
- Source provenance summary.

### 2. Classification

Classify accounts and tickets.

Output:

- Account risk labels: low, medium, high, critical.
- Ticket severity normalized labels.
- Product-area incident categories.
- Confidence summary.

### 3. Reconciliation

Resolve account aliases and connect tickets, opportunities, contacts, and usage events to canonical accounts.

Output:

- Canonical account table.
- Conflict log.
- Match confidence.

### 4. Narrative

Recall prior memory from Cognee and generate an executive crisis narrative.

Output:

- What happened.
- Why it matters.
- Which accounts need attention.
- What actions should happen in the next 48 hours.
- Evidence used.

### 5. Live Demo

Show a command-center interface.

Required UI panels:

- Agent timeline.
- Current task output.
- Cognee memory writes/recalls.
- Evidence panel.
- Risk or uncertainty panel.
- Final executive narrative.

## Sponsor Fit

- Cognee: persistent memory across all five stages.
- PyMC: probabilistic risk score or entity-match probability.
- Geodo: GTM/customer-success next actions and account outreach framing.
- Trupeer: record the final walkthrough and generate demo collateral.

## Six-Hour Rehearsal Target

- 0:00-0:30: Generate/load mock data and inspect schema.
- 0:30-1:15: Ingestion agent and Cognee memory writes.
- 1:15-2:00: Classification rules and baseline risk scoring.
- 2:00-2:45: Reconciliation logic.
- 2:45-3:30: PyMC or simple Bayesian uncertainty model.
- 3:30-4:30: Narrative generation with Cognee recall.
- 4:30-5:30: UI integration.
- 5:30-6:00: Demo rehearsal and cut scope.

## Success Criteria

- The demo runs end to end on a fresh mock dataset.
- At least three downstream steps visibly recall Cognee memory from prior steps.
- The final narrative cites evidence from ingestion, classification, and reconciliation.
- The UI is understandable to an industry judge in under 90 seconds.
- The project has a credible fallback if PyMC or a sponsor tool takes too long.

