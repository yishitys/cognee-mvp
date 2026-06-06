from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_DATA_DIR = Path("demo_materials/m_agents_rehearsal/assembled_crisis_pack")
REQUIRED_TABLES = {
    "accounts": "accounts.csv",
    "contacts": "contacts.csv",
    "opportunities": "opportunities.csv",
    "usage_events": "usage_events.csv",
    "support_tickets": "support_tickets.csv",
    "incident_log": "incident_log.csv",
}


def _read_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, keep_default_na=False)
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def load_tables(data_dir: str | Path = DEFAULT_DATA_DIR) -> dict[str, pd.DataFrame]:
    data_path = Path(data_dir)
    missing_files = [file_name for file_name in REQUIRED_TABLES.values() if not (data_path / file_name).exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing required data files in {data_path}: {', '.join(missing_files)}")

    tables = {name: _read_csv(data_path / file_name) for name, file_name in REQUIRED_TABLES.items()}
    return normalize_tables(tables)


def normalize_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    normalized = {name: frame.copy() for name, frame in tables.items()}

    for column in ["arr"]:
        normalized["accounts"][column] = pd.to_numeric(normalized["accounts"][column], errors="coerce").fillna(0)

    for column in ["amount"]:
        normalized["opportunities"][column] = pd.to_numeric(normalized["opportunities"][column], errors="coerce").fillna(0)

    for column in ["active_users", "api_errors", "core_workflows_completed", "daily_usage_mins"]:
        normalized["usage_events"][column] = pd.to_numeric(normalized["usage_events"][column], errors="coerce").fillna(0)

    for column in ["customer_satisfaction"]:
        normalized["support_tickets"][column] = pd.to_numeric(normalized["support_tickets"][column], errors="coerce")

    date_columns = {
        "accounts": ["renewal_date"],
        "opportunities": ["close_date"],
        "usage_events": ["date"],
        "support_tickets": ["created_at"],
        "incident_log": ["start_time", "end_time"],
    }
    for table_name, columns in date_columns.items():
        for column in columns:
            normalized[table_name][column] = pd.to_datetime(normalized[table_name][column], errors="coerce")

    return normalized


def table_preview(tables: dict[str, pd.DataFrame], limit: int = 5) -> dict[str, list[dict[str, Any]]]:
    return {name: frame.head(limit).to_dict(orient="records") for name, frame in tables.items()}
