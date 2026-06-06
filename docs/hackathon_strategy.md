# M-Agents Hackathon Strategy

## Confirmed Context

This project is for the M-Agents hackathon.

Known technical case for Cognee:

> Every team builds a multi-agent pipeline across five sequential tasks: data ingestion, classification, reconciliation, narrative generation, and a live interface demo. Without persistent memory, each agent starts from scratch. The context found in Task 1 is lost by Task 3. The behavioral baseline built in Task 2 has to be re-ingested for Task 4. Cognee fixes that with a small API surface: install Cognee, call `remember()`, call `recall()`. Any team using it can build a more capable pipeline because prior task context remains available to later agents.

Known sponsors:

- Trupeer: AI-powered screen recording and demo creation from product walkthroughs.
- Cognee: persistent memory layer between data and agents.
- PyMC Labs: Bayesian AI consultancy and creators of PyMC.
- Geodo: AI-powered GTM and outbound sales infrastructure.
- Red Bull: beverages.

More challenge details will be announced during the event.

Additional known information:

- Every team receives a real dataset and a real business crisis.
- Teams have one day to go from zero to a working product demo.
- Judges are from industry.
- Problems are real; the team decides how high the stakes feel in the product framing.
- The actual hackathon working window may be as short as 6 hours, so the implementation process must be rehearsed before the event.

## Sponsor Research Notes

Sources checked on June 5, 2026:

- Trupeer official site and docs: turns one screen recording into videos, docs, translations, guides, shared pages, knowledge base material, and agent-queryable workflow knowledge.
- Cognee docs: `remember()` supports permanent graph memory and session memory; permanent memory creates dataset records, chunks, graph nodes/edges, embeddings, summaries, and retrieval artifacts; `recall()` can query the graph-backed memory.
- PyMC Labs official site: focuses on Bayesian modeling, optimization, AI systems, strategy, causal inference, and transparent probabilistic modeling.
- Geodo official site: positions itself as a GTM command center / digital twin for outbound intelligence, pipeline mastery, buyer personalization, sequences, and sales workflow automation. Public developer API documentation was not obvious, so use it as a product/UX/workflow inspiration unless sponsor access is provided.

## Recommended Build

Build a "Memory-Native Multi-Agent Ops Pipeline".

The demo should show the same five tasks the hackathon asks for, but make the memory handoff visible. The core differentiator is not just that the answer is good; it is that each downstream agent can cite what it inherited from earlier agents.

Because the event is time-constrained, the product should be pre-architected as a crisis-response cockpit. On the day of the event, the dataset and business crisis should be treated as pluggable inputs, not as reasons to redesign the system.

### Task 1: Data Ingestion Agent

Responsibilities:

- Load raw files, tables, notes, or API output.
- Normalize schema.
- Detect missing fields and suspicious records.
- Write raw context, dataset summary, schema, anomalies, and source metadata into Cognee.

Memory writes:

- `dataset_profile`
- `schema_map`
- `source_provenance`
- `data_quality_findings`

### Task 2: Classification Agent

Responsibilities:

- Classify records into the required categories.
- Build a behavioral baseline or label ontology.
- Store label definitions, edge cases, uncertainty, and examples.

Memory writes:

- `label_taxonomy`
- `classification_baseline`
- `known_edge_cases`
- `confidence_distribution`

PyMC angle:

- Use Bayesian classification calibration or a simple probabilistic confidence model.
- Show uncertainty instead of only deterministic labels.

### Task 3: Reconciliation Agent

Responsibilities:

- Resolve duplicates, conflicts, entity aliases, and mismatched records.
- Pull ingestion provenance and classification baseline from Cognee instead of reprocessing.
- Write reconciliation decisions with evidence.

Memory writes:

- `entity_resolution_decisions`
- `conflict_log`
- `canonical_entities`
- `reconciliation_confidence`

PyMC angle:

- Use a probabilistic match score for entity resolution.
- Treat fuzzy matches as posterior probabilities rather than brittle yes/no rules.

### Task 4: Narrative Generation Agent

Responsibilities:

- Recall all prior task outputs from Cognee.
- Generate a short executive narrative with citations to pipeline memory.
- Explain what changed between raw input, classification, and reconciliation.

Memory reads:

- Data quality findings from Task 1.
- Classification baseline from Task 2.
- Reconciliation decisions from Task 3.

Memory writes:

- `narrative_summary`
- `action_items`
- `open_questions`

### Task 5: Live Interface Demo

Responsibilities:

- Show the pipeline running step by step.
- Display memory writes and recalls as first-class UI events.
- Let judges ask: "Why did the narrative say this?" and retrieve the supporting memory.

Required visible elements:

- Agent timeline.
- Cognee memory event log.
- Current task output.
- Evidence panel showing recalled facts.
- Confidence / uncertainty panel if PyMC is used.

Trupeer angle:

- Record the live walkthrough with Trupeer.
- Generate a polished product demo and written walkthrough.
- Use the generated documentation as a final submission artifact.

Geodo angle:

- If the challenge data is sales, GTM, lead, customer, pipeline, or outreach-related, make Geodo the domain fit: classify accounts, reconcile contacts, generate personalized outbound narratives, and show pipeline next actions.
- If the challenge is not GTM-related, use Geodo more lightly: frame the interface as an agent command center with natural-language task control and personalized action recommendations.

## Core Architecture

```text
Raw inputs
  -> Ingestion Agent
  -> Cognee remember(dataset_profile, schema, provenance)
  -> Classification Agent
  -> Cognee recall(ingestion context)
  -> Cognee remember(label baseline, edge cases)
  -> Reconciliation Agent
  -> Cognee recall(schema + baseline)
  -> Cognee remember(canonical entities, conflicts)
  -> Narrative Agent
  -> Cognee recall(all prior task memory)
  -> Live Interface
```

## Judging Strategy

Make these points obvious in the demo:

- The agents do not pass a giant prompt around.
- Each task writes structured memory into Cognee.
- Later agents recall the exact context they need.
- The UI shows memory provenance, so outputs are explainable.
- PyMC adds calibrated uncertainty, not just another LLM call.
- Trupeer turns the walkthrough into polished demo collateral.
- The interface feels like a response tool for a real business crisis, not a toy notebook.
- The demo should answer: what happened, what entities are involved, what changed, what is uncertain, what should leadership do next, and what evidence supports the recommendation.

## Implementation Priorities

1. Build the Cognee memory layer first.
2. Make the five-task pipeline work on a tiny sample dataset.
3. Add a Streamlit or FastAPI + React interface that shows each task and memory event.
4. Add PyMC only where uncertainty is meaningful: classification confidence or reconciliation probability.
5. Polish demo flow and record it with Trupeer.

## Six-Hour Runbook

Use this as the day-of-event default unless the prompt forces a different structure.

- 0:00-0:20: Read prompt, define crisis framing, inspect dataset columns, pick the business question.
- 0:20-0:50: Build ingestion adapter and dataset profile; write source/schema/provenance to Cognee.
- 0:50-1:40: Implement classification baseline and label taxonomy; write edge cases and confidence summary to Cognee.
- 1:40-2:30: Implement reconciliation/entity resolution; write canonical entities and conflict log to Cognee.
- 2:30-3:20: Add PyMC or lightweight Bayesian scoring only if it supports a visible uncertainty output.
- 3:20-4:20: Build narrative generator that recalls prior memory and produces evidence-backed recommendations.
- 4:20-5:15: Build/polish UI: timeline, current output, memory evidence, confidence panel, final narrative.
- 5:15-5:45: Rehearse demo; record fallback walkthrough with Trupeer if available.
- 5:45-6:00: Freeze features, fix obvious UI failures, prepare 90-second story.

## Pre-Hackathon Rehearsal

Run at least one full mock crisis before the event.

Suggested rehearsal scenario:

- Dataset: synthetic customer accounts, support tickets, usage metrics, renewal dates, and sales opportunities.
- Crisis: enterprise churn spike caused by a product incident that affected strategic accounts.
- Business goal: identify at-risk accounts, reconcile duplicate customer records, classify incident severity, generate an executive action plan, and demo a live command center.

Why this rehearsal is useful:

- It exercises ingestion, classification, reconciliation, narrative generation, and interface demo.
- It naturally fits Cognee memory because each step depends on prior context.
- It fits PyMC because churn or incident risk can be modeled probabilistically.
- It fits Geodo if the narrative includes outbound/customer-success next actions.
- It fits Trupeer because the final command-center walkthrough can be recorded as a product demo.

## Do Not Overbuild

- Do not create five fully autonomous agents before the memory story works.
- Do not hide Cognee behind a generic RAG label; show `remember` and `recall`.
- Do not force Geodo into the stack if the challenge data has no GTM angle.
- Do not make PyMC a decorative import; use it for a visible posterior/confidence output.
