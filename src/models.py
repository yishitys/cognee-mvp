from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class MemoryEvent:
    key: str
    stage: str
    summary: str
    payload: dict[str, Any]
    event_type: str = "write"
    source: str = "local"
    query: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class DatasetProfile:
    row_counts: dict[str, int]
    columns: dict[str, list[str]]
    missing: dict[str, dict[str, int]]
    date_ranges: dict[str, dict[str, str]]
    suspicious_records: list[dict[str, Any]]


@dataclass
class RiskScore:
    account_id: str
    account_name: str
    segment: str
    arr: float
    renewal_date: str
    score: float
    probability: float
    confidence: float
    label: str
    reasons: list[str]


@dataclass
class NarrativeSummary:
    title: str
    what_happened: str
    top_accounts: list[dict[str, Any]]
    uncertainty: list[str]
    actions: list[str]
    source: str


@dataclass
class PipelineResult:
    dataset_profile: dict[str, Any]
    classification: dict[str, Any]
    reconciliation: dict[str, Any]
    narrative: dict[str, Any]
    memory_events: list[MemoryEvent]
    evidence_by_account: dict[str, dict[str, Any]]
