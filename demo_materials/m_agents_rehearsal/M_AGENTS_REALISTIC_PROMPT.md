# M-Agents Rehearsal Prompt

## Challenge Title

Enterprise Renewal Crisis Command Center

## Background

You are building a demo for the M-Agents hackathon. A B2B SaaS company is facing an urgent enterprise retention crisis. During the last two weeks, support tickets increased, API and data-sync incidents affected several customers, product usage dropped for important accounts, and the revenue team is worried about active renewal and expansion opportunities.

The company wants a working multi-agent product demo by the end of the day. Leadership does not want a notebook-only analysis. They want a command center that explains what happened, which accounts are at risk, how records were reconciled, and what customer-success or GTM action should happen in the next 48 hours.

## Available Data

Use the assembled dataset in:

`demo_materials/m_agents_rehearsal/assembled_crisis_pack`

Tables:

- `accounts.csv`: 40 customer accounts with ARR, segment, owner, region, renewal date, and account aliases.
- `contacts.csv`: 40 account contacts with titles and emails.
- `opportunities.csv`: 650 CRM opportunities with sales agent, stage, product, amount, and close date.
- `usage_events.csv`: 1,400 daily product-usage rows with active users, API errors, workflow completions, login frequency, and usage minutes.
- `support_tickets.csv`: 900 support tickets with customer name, optional account ID, product area, severity, status, subject, description, and satisfaction.
- `incident_log.csv`: 2 product incidents affecting API Platform and Data Sync.

Source material came from Kaggle CRM, customer-support, and SaaS churn datasets, then was assembled into a dirty cross-table crisis pack for this rehearsal.

## Intentional Data Problems

The dataset is designed to behave like a real hackathon prompt:

- Some support tickets have missing `account_id`.
- Some account names appear as aliases, lower-case variants, or company suffix variants.
- Ticket severity labels are not always aligned with normalized severity.
- Usage drops appear after the incident window for some enterprise and strategic accounts.
- Support, CRM, usage, and incident records must be reconciled before the executive narrative is trustworthy.

## Required Five-Agent Pipeline

### 1. Ingestion Agent

Load all six tables. Produce a dataset profile, table relationship map, row counts, date coverage, missing-field report, and suspicious-record list.

Memory writes to show in the demo:

- `dataset_profile`
- `schema_map`
- `source_provenance`
- `data_quality_findings`

### 2. Classification Agent

Classify accounts and tickets.

Required outputs:

- Account risk label: `low`, `medium`, `high`, or `critical`.
- Ticket severity normalization.
- Incident-related product-area classification.
- Confidence summary and notable edge cases.

Suggested risk signals:

- ARR and segment.
- Renewal date proximity.
- Post-incident active-user or workflow-completion drop.
- API error spike.
- Critical or high support tickets.
- Open opportunities close to renewal.

Memory writes:

- `label_taxonomy`
- `classification_baseline`
- `known_edge_cases`
- `confidence_distribution`

### 3. Reconciliation Agent

Resolve duplicate or ambiguous account references across support tickets, opportunities, contacts, usage events, and incident impact.

Required outputs:

- Canonical account table.
- Matched support-ticket-to-account table.
- Conflict log for uncertain matches.
- Match confidence score or reason.

Memory reads:

- Ingestion findings.
- Schema map.
- Classification baseline.

Memory writes:

- `canonical_entities`
- `entity_resolution_decisions`
- `conflict_log`
- `reconciliation_confidence`

### 4. Narrative Generation Agent

Generate an executive crisis narrative using recalled memory from prior agents.

The narrative must answer:

- What happened?
- Which accounts are at highest renewal or expansion risk?
- Which incidents and product areas are implicated?
- Which facts are certain and which are uncertain?
- What should customer success, support, and sales do in the next 48 hours?

Memory reads:

- Data quality findings.
- Risk labels and confidence.
- Reconciliation decisions.
- Evidence for top accounts.

Memory writes:

- `narrative_summary`
- `action_items`
- `open_questions`

### 5. Live Interface Demo

Build a command-center interface or dashboard that can be shown to judges.

Required panels:

- Agent timeline.
- Cognee memory writes and recalls.
- Current task output.
- Evidence panel for selected account.
- Risk / uncertainty panel.
- Final executive narrative.

## Sponsor Fit

- Cognee: make memory handoff visible through `remember()` and `recall()`.
- PyMC: optional, but useful for account-risk uncertainty or entity-match probability.
- Geodo: convert findings into GTM, renewal, and outbound next actions.
- Trupeer: record the walkthrough and generate demo collateral.

## Success Criteria

- The five-stage pipeline runs end to end on the assembled dataset.
- At least three downstream steps visibly recall memory produced by earlier steps.
- The final narrative cites evidence from ingestion, classification, and reconciliation.
- The UI tells a credible crisis story in under 90 seconds.
- The team can explain what would break if there were no persistent memory layer.

## Suggested Six-Hour Runbook

- 0:00-0:20: Read prompt, inspect tables, define crisis framing.
- 0:20-0:50: Build ingestion profile and write memory events.
- 0:50-1:40: Implement classification rules and account-risk scoring.
- 1:40-2:30: Implement account alias reconciliation.
- 2:30-3:20: Add uncertainty scoring if feasible.
- 3:20-4:20: Generate evidence-backed executive narrative.
- 4:20-5:15: Build command-center UI.
- 5:15-5:45: Rehearse and record fallback walkthrough.
- 5:45-6:00: Freeze scope and polish the 90-second story.
