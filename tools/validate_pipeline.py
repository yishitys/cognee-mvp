from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import DEFAULT_DATA_DIR, load_tables
from src.pipeline import normalize_account_name, run_pipeline


EXPECTED_COUNTS = {
    "accounts": 40,
    "contacts": 40,
    "opportunities": 650,
    "usage_events": 1400,
    "support_tickets": 900,
    "incident_log": 2,
}


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    tables = load_tables(DEFAULT_DATA_DIR)
    counts = {name: len(frame) for name, frame in tables.items()}
    assert_true(counts == EXPECTED_COUNTS, f"Unexpected row counts: {counts}")

    assert_true(normalize_account_name("Acme Inc") == normalize_account_name("acme"), "Alias suffix normalization failed")
    assert_true(normalize_account_name("Blue Sky Ltd") == normalize_account_name("BlueSky"), "Whitespace normalization failed")

    result = run_pipeline(str(DEFAULT_DATA_DIR), use_cognee=False, use_llm=False)
    assert_true(len(result.memory_events) >= 12, "Expected memory write/read events")
    assert_true(any(event.event_type == "read" for event in result.memory_events), "Expected recall events")

    labels = Counter(row["label"] for row in result.classification["risk_scores"])
    assert_true(len(labels) >= 3, f"Expected multiple risk labels, got {labels}")

    top = result.classification["risk_scores"][0]
    assert_true(len(top["reasons"]) >= 3, f"Top account lacks evidence reasons: {top}")

    reconciliation = result.reconciliation["summary"]
    assert_true(reconciliation["tickets_matched"] > 0, "No support tickets were matched")
    assert_true(reconciliation["match_rate"] > 0.9, f"Low reconciliation match rate: {reconciliation}")

    narrative = result.narrative
    assert_true(narrative["top_accounts"], "Narrative missing top accounts")
    assert_true(narrative["actions"], "Narrative missing actions")
    assert_true(narrative["uncertainty"], "Narrative missing uncertainty")

    print("Pipeline validation passed.")
    print(f"Row counts: {counts}")
    print(f"Risk labels: {dict(labels)}")
    print(f"Reconciliation: {reconciliation}")


if __name__ == "__main__":
    main()
