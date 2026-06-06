from __future__ import annotations

import math
import os
import re
from dataclasses import asdict
from datetime import date
from typing import Any

import pandas as pd
from dotenv import load_dotenv

from src.data_loader import DEFAULT_DATA_DIR, load_tables
from src.memory import MemoryStore
from src.models import DatasetProfile, NarrativeSummary, PipelineResult, RiskScore

try:
    from rapidfuzz import fuzz, process
except Exception:  # pragma: no cover - dependency fallback
    fuzz = None
    process = None


INCIDENT_START = pd.Timestamp("2026-05-18")
TODAY = date(2026, 6, 5)
load_dotenv()


def normalize_account_name(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()
    cleaned = re.sub(r"\b(inc|ltd|llc|corp|corporation|company|co)\b", "", cleaned)
    return re.sub(r"\s+", "", cleaned).strip()


def label_from_score(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 70:
        return "high"
    if score >= 58:
        return "medium"
    return "low"


def probability_from_score(score: float) -> float:
    return round(1 / (1 + math.exp(-(score - 55) / 13)), 3)


def run_pipeline(
    data_dir: str = str(DEFAULT_DATA_DIR),
    use_cognee: bool = True,
    use_llm: bool = True,
    memory: MemoryStore | None = None,
) -> PipelineResult:
    memory = memory or MemoryStore(use_cognee=use_cognee)
    memory.reset()
    tables = load_tables(data_dir)

    profile = run_ingestion_agent(tables, memory)
    classification = run_classification_agent(tables, memory)
    reconciliation = run_reconciliation_agent(tables, classification, memory)
    evidence = build_evidence_by_account(tables, classification, reconciliation)
    narrative = run_narrative_agent(profile, classification, reconciliation, evidence, memory, use_llm=use_llm)

    return PipelineResult(
        dataset_profile=profile,
        classification=classification,
        reconciliation=reconciliation,
        narrative=narrative,
        memory_events=memory.list_events(),
        evidence_by_account=evidence,
    )


def run_ingestion_agent(tables: dict[str, pd.DataFrame], memory: MemoryStore) -> dict[str, Any]:
    row_counts = {name: len(frame) for name, frame in tables.items()}
    columns = {name: list(frame.columns) for name, frame in tables.items()}
    missing = {name: frame.replace("", pd.NA).isna().sum().astype(int).to_dict() for name, frame in tables.items()}
    date_ranges: dict[str, dict[str, str]] = {}
    suspicious_records = []

    for name, frame in tables.items():
        ranges = {}
        for column in frame.columns:
            if pd.api.types.is_datetime64_any_dtype(frame[column]):
                ranges[column] = {
                    "min": _date_string(frame[column].min()),
                    "max": _date_string(frame[column].max()),
                }
        if ranges:
            date_ranges[name] = ranges

    support = tables["support_tickets"]
    missing_account_id = int((support["account_id"].astype(str).str.strip() == "").sum())
    if missing_account_id:
        suspicious_records.append(
            {
                "table": "support_tickets",
                "issue": "missing_account_id",
                "count": missing_account_id,
                "why_it_matters": "Reconciliation must attach these tickets to canonical accounts before narrative generation.",
            }
        )

    profile = DatasetProfile(row_counts, columns, missing, date_ranges, suspicious_records)
    payload = asdict(profile)
    memory.remember("dataset_profile", payload, "Ingestion", "Loaded all crisis-pack tables and profiled row counts.")
    memory.remember(
        "schema_map",
        {"tables": columns, "likely_joins": _likely_joins()},
        "Ingestion",
        "Mapped table columns and default join candidates.",
    )
    memory.remember(
        "source_provenance",
        {"sources": "Kaggle CRM, customer support, and SaaS churn datasets assembled into rehearsal crisis pack."},
        "Ingestion",
        "Recorded Kaggle-derived source provenance.",
    )
    memory.remember(
        "data_quality_findings",
        {"missing": missing, "suspicious_records": suspicious_records},
        "Ingestion",
        "Detected missing account ids and other field-level quality issues.",
    )
    return payload


def run_classification_agent(tables: dict[str, pd.DataFrame], memory: MemoryStore) -> dict[str, Any]:
    memory.recall("Load ingestion context before classification.", ["dataset_profile", "data_quality_findings"])
    accounts = tables["accounts"].copy()
    usage = tables["usage_events"].copy()
    tickets = tables["support_tickets"].copy()
    opportunities = tables["opportunities"].copy()

    ticket_rollup = _ticket_rollup(tickets)
    usage_rollup = _usage_rollup(usage)
    opportunity_rollup = _opportunity_rollup(opportunities)

    risks: list[RiskScore] = []
    for _, account in accounts.iterrows():
        account_id = account["account_id"]
        reasons = []
        score = 8.0

        arr = float(account["arr"])
        if arr >= 500_000:
            score += 24
            reasons.append("Strategic ARR exposure")
        elif arr >= 180_000:
            score += 15
            reasons.append("Enterprise ARR exposure")

        days_to_renewal = (account["renewal_date"].date() - TODAY).days if not pd.isna(account["renewal_date"]) else 365
        if days_to_renewal <= 45:
            score += 18
            reasons.append("Renewal inside 45 days")
        elif days_to_renewal <= 90:
            score += 9
            reasons.append("Renewal inside 90 days")

        usage_stats = usage_rollup.get(account_id, {})
        usage_drop = usage_stats.get("workflow_drop_pct", 0)
        if usage_drop >= 0.35:
            score += 24
            reasons.append(f"Workflow completion dropped {usage_drop:.0%} after incident")
        elif usage_drop >= 0.18:
            score += 12
            reasons.append(f"Workflow completion softened {usage_drop:.0%} after incident")

        api_error_spike = usage_stats.get("api_error_spike", 0)
        if api_error_spike >= 25:
            score += 15
            reasons.append("Post-incident API errors spiked")

        ticket_stats = ticket_rollup.get(account_id, {})
        total_tickets = ticket_stats.get("total", 0)
        if total_tickets >= 20:
            score += 10
            reasons.append(f"{total_tickets} total support tickets")
        high_tickets = ticket_stats.get("high_or_critical", 0)
        if high_tickets >= 10:
            score += 30
            reasons.append(f"{high_tickets} high/critical support tickets")
        elif high_tickets >= 7:
            score += 22
            reasons.append(f"{high_tickets} high/critical support tickets")
        elif high_tickets >= 4:
            score += 16
            reasons.append(f"{high_tickets} high/critical support tickets")
        elif high_tickets:
            score += 8
            reasons.append(f"{high_tickets} high/critical support tickets")

        incident_tickets = ticket_stats.get("incident_related", 0)
        if incident_tickets >= 8:
            score += 18
            reasons.append(f"{incident_tickets} tickets tied to incident product areas")
        elif incident_tickets >= 4:
            score += 10
            reasons.append(f"{incident_tickets} tickets tied to incident product areas")

        open_pipeline = opportunity_rollup.get(account_id, {}).get("open_amount", 0)
        if open_pipeline >= 100_000:
            score += 8
            reasons.append("Material open sales opportunity at risk")

        score = round(min(score, 100), 1)
        confidence = round(min(0.95, 0.45 + 0.1 * min(len(reasons), 5)), 2)
        risks.append(
            RiskScore(
                account_id=account_id,
                account_name=account["account_name"],
                segment=account["segment"],
                arr=arr,
                renewal_date=_date_string(account["renewal_date"]),
                score=score,
                probability=probability_from_score(score),
                confidence=confidence,
                label=label_from_score(score),
                reasons=reasons or ["No acute crisis signal detected"],
            )
        )

    risk_rows = [asdict(score) for score in sorted(risks, key=lambda item: item.score, reverse=True)]
    label_counts = pd.Series([row["label"] for row in risk_rows]).value_counts().to_dict()
    severity_output = normalize_ticket_severity(tickets)
    incident_products = sorted(set(tables["incident_log"]["product_area"].dropna().astype(str)))

    payload = {
        "risk_scores": risk_rows,
        "label_counts": label_counts,
        "ticket_severity_summary": severity_output,
        "incident_related_product_areas": incident_products,
        "confidence_summary": {
            "average_account_confidence": round(sum(row["confidence"] for row in risk_rows) / max(len(risk_rows), 1), 2),
            "method": "Lightweight rules-based probability score calibrated for demo explainability.",
        },
    }
    memory.remember("label_taxonomy", _label_taxonomy(), "Classification", "Defined account-risk and ticket-severity labels.")
    memory.remember("classification_baseline", payload, "Classification", "Classified account risk and incident-related tickets.")
    memory.remember(
        "known_edge_cases",
        {"edge_cases": ["Missing account_id tickets", "Alias-only account names", "Severity label conflicts"]},
        "Classification",
        "Captured classification edge cases for reconciliation and narrative.",
    )
    memory.remember(
        "confidence_distribution",
        payload["confidence_summary"],
        "Classification",
        "Stored confidence summary for uncertainty panel.",
    )
    return payload


def run_reconciliation_agent(
    tables: dict[str, pd.DataFrame],
    classification: dict[str, Any],
    memory: MemoryStore,
) -> dict[str, Any]:
    memory.recall("Load schema and classification context before reconciliation.", ["schema_map", "classification_baseline"])
    accounts = tables["accounts"].copy()
    tickets = tables["support_tickets"].copy()

    alias_to_account: dict[str, dict[str, Any]] = {}
    for _, account in accounts.iterrows():
        for value in {account["account_name"], account["account_alias"]}:
            alias_to_account[normalize_account_name(value)] = account.to_dict()

    normalized_aliases = list(alias_to_account.keys())
    matched_rows = []
    conflict_log = []
    for _, ticket in tickets.iterrows():
        provided_id = str(ticket["account_id"]).strip()
        if provided_id:
            match = accounts.loc[accounts["account_id"] == provided_id]
            if not match.empty:
                account = match.iloc[0].to_dict()
                matched_rows.append(_ticket_match_row(ticket, account, "account_id", 1.0))
                continue

        normalized = normalize_account_name(ticket["account_name"])
        if normalized in alias_to_account:
            matched_rows.append(_ticket_match_row(ticket, alias_to_account[normalized], "alias_exact", 0.96))
            continue

        best_name, score = _best_fuzzy_match(normalized, normalized_aliases)
        if best_name and score >= 86:
            matched_rows.append(_ticket_match_row(ticket, alias_to_account[best_name], "fuzzy_name", round(score / 100, 2)))
        else:
            conflict_log.append(
                {
                    "ticket_id": ticket["ticket_id"],
                    "raw_account_name": ticket["account_name"],
                    "reason": "No confident account match",
                    "best_score": round(score / 100, 2) if score else 0,
                }
            )

    canonical = accounts[["account_id", "account_name", "account_alias", "segment", "arr", "renewal_date", "owner", "region"]].copy()
    risk_by_account = {row["account_id"]: row for row in classification["risk_scores"]}
    canonical["risk_label"] = canonical["account_id"].map(lambda account_id: risk_by_account.get(account_id, {}).get("label", "unknown"))
    canonical["risk_score"] = canonical["account_id"].map(lambda account_id: risk_by_account.get(account_id, {}).get("score", 0))

    matched_count = len(matched_rows)
    payload = {
        "canonical_accounts": _records(canonical),
        "ticket_account_matches": matched_rows,
        "conflict_log": conflict_log,
        "summary": {
            "tickets_seen": len(tickets),
            "tickets_matched": matched_count,
            "match_rate": round(matched_count / max(len(tickets), 1), 3),
            "conflicts": len(conflict_log),
        },
    }
    memory.remember("canonical_entities", {"canonical_accounts": payload["canonical_accounts"]}, "Reconciliation", "Built canonical account table.")
    memory.remember(
        "entity_resolution_decisions",
        {"ticket_account_matches": matched_rows[:200], "summary": payload["summary"]},
        "Reconciliation",
        "Resolved support tickets to canonical accounts.",
    )
    memory.remember("conflict_log", {"conflicts": conflict_log}, "Reconciliation", "Stored low-confidence entity matches.")
    memory.remember(
        "reconciliation_confidence",
        payload["summary"],
        "Reconciliation",
        "Stored ticket-to-account reconciliation confidence summary.",
    )
    return payload


def run_narrative_agent(
    profile: dict[str, Any],
    classification: dict[str, Any],
    reconciliation: dict[str, Any],
    evidence: dict[str, dict[str, Any]],
    memory: MemoryStore,
    use_llm: bool = True,
) -> dict[str, Any]:
    recalled = memory.recall(
        "Generate executive narrative with evidence from prior agents.",
        ["data_quality_findings", "classification_baseline", "canonical_entities", "reconciliation_confidence"],
    )
    top_accounts = classification["risk_scores"][:5]
    evidence_packet = {
        "dataset_profile": {
            "row_counts": profile["row_counts"],
            "suspicious_records": profile["suspicious_records"],
        },
        "top_accounts": top_accounts,
        "reconciliation_summary": reconciliation["summary"],
        "recalled_memory_keys": [event.key for event in recalled],
        "selected_evidence": {row["account_id"]: evidence.get(row["account_id"], {}) for row in top_accounts[:3]},
    }

    llm_text = None
    if use_llm:
        llm_text = _try_anthropic_narrative(evidence_packet)

    narrative = _template_narrative(evidence_packet, source="anthropic" if llm_text else "template")
    if llm_text:
        narrative["what_happened"] = llm_text

    memory.remember("narrative_summary", narrative, "Narrative", "Generated executive crisis narrative.")
    memory.remember("action_items", {"actions": narrative["actions"]}, "Narrative", "Stored 48-hour action plan.")
    memory.remember("open_questions", {"open_questions": narrative["uncertainty"]}, "Narrative", "Stored unresolved risks and uncertainties.")
    return narrative


def build_evidence_by_account(
    tables: dict[str, pd.DataFrame],
    classification: dict[str, Any],
    reconciliation: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    risk_by_account = {row["account_id"]: row for row in classification["risk_scores"]}
    matches = pd.DataFrame(reconciliation["ticket_account_matches"])
    evidence = {}
    for account_id, risk in risk_by_account.items():
        usage = tables["usage_events"].loc[tables["usage_events"]["account_id"] == account_id].copy()
        tickets = matches.loc[matches["matched_account_id"] == account_id].copy() if not matches.empty else pd.DataFrame()
        opportunities = tables["opportunities"].loc[tables["opportunities"]["account_id"] == account_id].copy()
        evidence[account_id] = {
            "risk": risk,
            "usage_summary": _account_usage_summary(usage),
            "tickets": _records(tickets.head(10)) if not tickets.empty else [],
            "opportunities": _records(opportunities.sort_values("amount", ascending=False).head(10)),
        }
    return evidence


def normalize_ticket_severity(tickets: pd.DataFrame) -> dict[str, Any]:
    counts = tickets["normalized_severity"].str.lower().value_counts().to_dict()
    conflicts = tickets.loc[
        tickets["reported_severity"].str.lower().str.strip() != tickets["normalized_severity"].str.lower().str.strip()
    ]
    return {"severity_counts": counts, "conflict_count": len(conflicts), "examples": _records(conflicts.head(5))}


def _ticket_rollup(tickets: pd.DataFrame) -> dict[str, dict[str, Any]]:
    known = tickets.loc[tickets["account_id"].astype(str).str.strip() != ""].copy()
    known["is_high"] = known["normalized_severity"].str.lower().isin(["high", "critical"])
    known["is_incident_related"] = known["product_area"].isin(["API Platform", "Data Sync"])
    grouped = known.groupby("account_id").agg(
        total=("ticket_id", "count"),
        high_or_critical=("is_high", "sum"),
        incident_related=("is_incident_related", "sum"),
    )
    return grouped.to_dict(orient="index")


def _usage_rollup(usage: pd.DataFrame) -> dict[str, dict[str, Any]]:
    output = {}
    for account_id, frame in usage.groupby("account_id"):
        pre = frame.loc[frame["date"] < INCIDENT_START]
        post = frame.loc[frame["date"] >= INCIDENT_START]
        pre_workflows = float(pre["core_workflows_completed"].mean() or 0)
        post_workflows = float(post["core_workflows_completed"].mean() or 0)
        drop = max(0.0, (pre_workflows - post_workflows) / pre_workflows) if pre_workflows else 0.0
        output[account_id] = {
            "workflow_drop_pct": drop,
            "api_error_spike": float(post["api_errors"].mean() - pre["api_errors"].mean()) if not pre.empty and not post.empty else 0,
        }
    return output


def _opportunity_rollup(opportunities: pd.DataFrame) -> dict[str, dict[str, Any]]:
    open_stages = opportunities.loc[~opportunities["stage"].str.lower().isin(["won", "lost"])]
    grouped = open_stages.groupby("account_id").agg(open_amount=("amount", "sum"), open_count=("opportunity_id", "count"))
    return grouped.to_dict(orient="index")


def _account_usage_summary(usage: pd.DataFrame) -> dict[str, Any]:
    if usage.empty:
        return {}
    pre = usage.loc[usage["date"] < INCIDENT_START]
    post = usage.loc[usage["date"] >= INCIDENT_START]
    return {
        "pre_workflow_avg": round(float(pre["core_workflows_completed"].mean() or 0), 1),
        "post_workflow_avg": round(float(post["core_workflows_completed"].mean() or 0), 1),
        "post_api_error_avg": round(float(post["api_errors"].mean() or 0), 1),
        "latest_active_users": int(usage.sort_values("date").iloc[-1]["active_users"]),
    }


def _template_narrative(evidence_packet: dict[str, Any], source: str) -> dict[str, Any]:
    top_accounts = evidence_packet["top_accounts"]
    top_names = ", ".join(row["account_name"] for row in top_accounts[:3])
    suspicious = evidence_packet["dataset_profile"]["suspicious_records"]
    reconciliation = evidence_packet["reconciliation_summary"]
    uncertainty = [
        "Some support tickets required alias-based account matching.",
        "Risk scores are lightweight probabilities, not a fully trained churn model.",
    ]
    if suspicious:
        uncertainty.append(f"Data quality finding: {suspicious[0]['count']} support tickets have missing account_id.")
    return asdict(
        NarrativeSummary(
            title="Enterprise renewal crisis: incident-linked usage drop and support escalation",
            what_happened=(
                "API Platform and Data Sync incidents created a measurable customer-success risk. "
                f"The highest-priority accounts are {top_names}. Reconciliation matched "
                f"{reconciliation['tickets_matched']} of {reconciliation['tickets_seen']} support tickets, "
                "giving leadership an evidence-backed account view instead of disconnected CRM, usage, and support data."
            ),
            top_accounts=top_accounts,
            uncertainty=uncertainty,
            actions=[
                "Customer Success should contact critical-risk accounts today with incident-specific remediation notes.",
                "Support should prioritize high/critical tickets tied to API Platform and Data Sync.",
                "Sales managers should review open opportunities for top-risk accounts before renewal conversations.",
                "Leadership should monitor workflow completion recovery and API error reduction for the next 48 hours.",
            ],
            source=source,
        )
    )


def _try_anthropic_narrative(evidence_packet: dict[str, Any]) -> str | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        from anthropic import Anthropic

        timeout = float(os.getenv("ANTHROPIC_TIMEOUT_SECONDS", "20"))
        client = Anthropic(api_key=api_key, timeout=timeout, max_retries=0)
        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            max_tokens=650,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Write a concise executive crisis narrative for a B2B SaaS leadership team. "
                        "Use the evidence packet, cite concrete signals, and include uncertainty.\n\n"
                        f"{evidence_packet}"
                    ),
                }
            ],
        )
        return "\n".join(block.text for block in response.content if getattr(block, "text", None))
    except Exception:
        return None


def _ticket_match_row(ticket: pd.Series, account: dict[str, Any], method: str, confidence: float) -> dict[str, Any]:
    return {
        "ticket_id": ticket["ticket_id"],
        "raw_account_name": ticket["account_name"],
        "matched_account_id": account["account_id"],
        "matched_account_name": account["account_name"],
        "method": method,
        "match_confidence": confidence,
        "product_area": ticket["product_area"],
        "severity": ticket["normalized_severity"],
        "status": ticket["status"],
        "subject": ticket["subject"],
    }


def _best_fuzzy_match(value: str, candidates: list[str]) -> tuple[str | None, float]:
    if not value or not candidates:
        return None, 0
    if process and fuzz:
        match = process.extractOne(value, candidates, scorer=fuzz.token_sort_ratio)
        if match:
            return str(match[0]), float(match[1])
    best_name = None
    best_score = 0.0
    for candidate in candidates:
        score = 100.0 if value == candidate else 0.0
        if score > best_score:
            best_name = candidate
            best_score = score
    return best_name, best_score


def _label_taxonomy() -> dict[str, Any]:
    return {
        "account_risk": {
            "critical": "Immediate executive attention; renewal or expansion materially exposed.",
            "high": "Customer-success action needed this week.",
            "medium": "Monitor and assign owner follow-up.",
            "low": "No acute crisis signal.",
        },
        "ticket_severity": ["low", "medium", "high", "critical"],
    }


def _likely_joins() -> list[dict[str, str]]:
    return [
        {"left": "accounts.account_id", "right": "usage_events.account_id"},
        {"left": "accounts.account_id", "right": "contacts.account_id"},
        {"left": "accounts.account_id", "right": "opportunities.account_id"},
        {"left": "accounts.account_id/account_alias", "right": "support_tickets.account_id/account_name"},
        {"left": "incident_log.product_area", "right": "support_tickets.product_area"},
    ]


def _date_string(value: Any) -> str:
    if pd.isna(value):
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return frame.astype(object).where(pd.notna(frame), "").to_dict(orient="records")
