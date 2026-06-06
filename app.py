from __future__ import annotations

from dataclasses import asdict
from html import escape
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.data_loader import DEFAULT_DATA_DIR, load_tables
from src.pipeline import run_pipeline


load_dotenv()

st.set_page_config(
    page_title="Enterprise Renewal Crisis Command Center",
    layout="wide",
    initial_sidebar_state="expanded",
)


STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Source+Serif+4:wght@600;700&display=swap');

:root {
  --paper: #f2ecdd;
  --panel: #fffaf0;
  --ink: #181510;
  --muted: #615948;
  --line: #d6c9ad;
  --line-strong: #1d1913;
  --red: #b72e26;
  --red-soft: #f3d4cd;
  --gold: #b5791f;
  --gold-soft: #f2dfb8;
  --green: #17624e;
  --green-soft: #dbeadb;
  --blue: #1e6675;
  --blue-soft: #d7e7ea;
  --dark: #17130d;
}

html, body, [class*="css"] {
  font-family: 'Archivo', 'Segoe UI', sans-serif;
}

.stApp {
  background:
    linear-gradient(90deg, rgba(24,21,16,.055) 1px, transparent 1px),
    linear-gradient(0deg, rgba(24,21,16,.045) 1px, transparent 1px),
    radial-gradient(circle at 8% 0%, rgba(183,46,38,.12), transparent 34%),
    radial-gradient(circle at 90% 2%, rgba(30,102,117,.11), transparent 28%),
    var(--paper);
  background-size: 32px 32px, 32px 32px, auto, auto, auto;
  color: var(--ink);
}

.block-container {
  max-width: 1500px;
  padding: 18px 24px 36px;
}

header[data-testid="stHeader"], div[data-testid="stToolbar"] {
  visibility: hidden;
}

section[data-testid="stSidebar"] {
  background: var(--dark);
  border-right: 1px solid #3a3125;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
  color: #fff4df;
}

section[data-testid="stSidebar"] .stButton > button {
  border-radius: 4px;
  border: 1px solid #fff4df;
  background: #fff4df;
  color: var(--dark);
  font-weight: 800;
}

section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {
  color: var(--dark) !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
  border-color: var(--red);
  background: var(--red);
  color: #fffaf0;
}

section[data-testid="stSidebar"] .stButton > button:hover p,
section[data-testid="stSidebar"] .stButton > button:hover span {
  color: #fffaf0 !important;
}

.topline {
  border: 1px solid var(--line-strong);
  background: rgba(255,250,240,.96);
  box-shadow: 6px 6px 0 rgba(23,19,13,.92);
  padding: 18px 20px 16px;
  margin-bottom: 14px;
}

.topline h1 {
  margin: 5px 0 8px;
  font-size: clamp(34px, 4.2vw, 60px);
  line-height: .92;
  letter-spacing: 0;
  color: var(--ink);
}

.topline p {
  max-width: 1040px;
  margin: 0;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.48;
}

.kicker,
.section-title,
.mono {
  font-family: 'IBM Plex Mono', monospace;
}

.kicker {
  font-size: 11px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--red);
  font-weight: 600;
}

.section-title {
  font-size: 11px;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--red);
  font-weight: 700;
  margin: 8px 0 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line-strong);
  background: #f6ecd9;
  color: var(--ink);
  padding: 4px 8px;
  margin: 0 6px 6px 0;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  text-transform: uppercase;
  white-space: nowrap;
}

.chip-red { background: var(--red-soft); color: #7f1e19; }
.chip-gold { background: var(--gold-soft); color: #7a4c0d; }
.chip-green { background: var(--green-soft); color: var(--green); }
.chip-blue { background: var(--blue-soft); color: var(--blue); }

.panel {
  border: 1px solid var(--line);
  background: rgba(255,250,240,.96);
  padding: 12px 13px;
  margin-bottom: 10px;
}

.panel-tight {
  padding: 10px 11px;
  margin-bottom: 8px;
}

.panel-dark {
  border: 1px solid #40372c;
  background: #181510;
  color: #fff2dc;
}

.panel-dark strong {
  color: #f1c36d;
}

.panel strong {
  display: block;
  margin-bottom: 4px;
}

.stage-card {
  min-height: 112px;
  border: 1px solid var(--line-strong);
  background: rgba(255,250,240,.96);
  padding: 10px 11px;
  position: relative;
}

.stage-card .num {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

.stage-card strong {
  display: block;
  margin: 3px 0 4px;
  font-size: 15px;
}

.stage-card p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.35;
}

.stage-foot {
  margin-top: 8px;
  font-family: 'IBM Plex Mono', monospace;
  color: var(--blue);
  font-size: 11px;
}

.risk-critical { background: var(--red-soft); color: #7f1e19; }
.risk-high { background: var(--gold-soft); color: #7a4c0d; }
.risk-medium { background: #f4e9ca; color: #795a10; }
.risk-low { background: var(--green-soft); color: var(--green); }

.evidence-head {
  border: 1px solid var(--line-strong);
  background: rgba(255,250,240,.98);
  padding: 13px 14px;
  margin: 10px 0;
}

.evidence-head h2 {
  margin: 3px 0 7px;
  font-size: clamp(22px, 2.2vw, 34px);
  line-height: 1;
}

.small-note {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.42;
  margin: 0;
}

.narrative {
  border: 1px solid var(--line-strong);
  background: #fffaf0;
  padding: 16px 18px;
  margin: 12px 0 10px;
}

.narrative h2 {
  font-family: 'Source Serif 4', Georgia, serif;
  margin: 4px 0 9px;
  font-size: clamp(27px, 3vw, 42px);
  line-height: 1.02;
}

.narrative p {
  margin: 0;
  color: #2c2924;
  font-size: 15px;
  line-height: 1.58;
}

div[data-testid="stMetric"] {
  background: rgba(255,250,240,.96);
  border: 1px solid var(--line);
  padding: 9px 11px;
}

div[data-testid="stMetric"] label {
  font-family: 'IBM Plex Mono', monospace;
  color: var(--muted);
}

div[data-testid="stMetricValue"] {
  color: var(--ink);
  font-weight: 800;
}

.stDataFrame {
  border: 1px solid var(--line);
}

div[data-testid="stTabs"] button {
  font-family: 'IBM Plex Mono', monospace;
  text-transform: uppercase;
  font-size: 11px;
}

@media (max-width: 900px) {
  .block-container { padding-left: 14px; padding-right: 14px; }
  .topline h1 { font-size: 38px; }
  .stage-card { min-height: auto; }
}
</style>
"""


STAGES = [
    ("01", "Ingestion", "Load six tables, profile schema, dates, nulls, and quality flags."),
    ("02", "Classification", "Score renewal risk from ARR, usage drop, incidents, tickets, and close dates."),
    ("03", "Reconciliation", "Resolve account identities and repair missing ticket account links."),
    ("04", "Narrative", "Summarize crisis evidence into executive actions and open questions."),
    ("05", "Demo Surface", "Expose the trace: source data, memory events, risk, evidence, and actions."),
]


st.markdown(STYLE, unsafe_allow_html=True)


def run_cached_pipeline(use_cognee: bool, use_llm: bool):
    return run_pipeline(str(DEFAULT_DATA_DIR), use_cognee=use_cognee, use_llm=use_llm)


def html(text: Any) -> str:
    return escape(str(text))


def chip(label: Any, kind: str = "") -> str:
    class_name = "chip" if not kind else f"chip {kind}"
    return f"<span class='{class_name}'>{html(label)}</span>"


def risk_chip(label: Any) -> str:
    safe_label = str(label).lower()
    return chip(str(label).upper(), f"risk-{safe_label}")


def section_title(text: str) -> None:
    st.markdown(f"<div class='section-title'>{html(text)}</div>", unsafe_allow_html=True)


def panel(title: str, body: str, meta: str | None = None, dark: bool = False) -> None:
    class_name = "panel panel-tight panel-dark" if dark else "panel panel-tight"
    meta_html = f"<p class='small-note mono'>{html(meta)}</p>" if meta else ""
    st.markdown(
        f"<div class='{class_name}'><strong>{html(title)}</strong><div>{html(body)}</div>{meta_html}</div>",
        unsafe_allow_html=True,
    )


def render_header(status: str, use_cognee: bool, use_llm: bool) -> None:
    status_kind = "chip-red" if status == "LIVE" else "chip-green"
    st.markdown(
        f"""
        <div class="topline">
          <div class="kicker">M-Agents rehearsal / memory-native renewal rescue</div>
          <h1>Enterprise Renewal Crisis Command Center</h1>
          <p>
            A five-agent command flow that reconstructs a renewal crisis from fragmented CRM,
            product usage, incident, and support data. The page is ordered as the demo story:
            crisis state, agent handoff, account risk, evidence chain, then executive actions.
          </p>
          <div style="margin-top:12px">
            {chip(status, status_kind)}
            {chip('COGNEE ' + ('ON' if use_cognee else 'LOCAL'), 'chip-blue')}
            {chip('NARRATIVE ' + ('LLM' if use_llm else 'TEMPLATE'), 'chip-gold')}
            {chip('FALLBACK READY', 'chip-green')}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_frame(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    for column in output.columns:
        if pd.api.types.is_datetime64_any_dtype(output[column]):
            output[column] = output[column].dt.strftime("%Y-%m-%d")
        elif output[column].dtype == "object":
            output[column] = output[column].apply(
                lambda value: "; ".join(map(str, value))
                if isinstance(value, list)
                else ("" if pd.isna(value) else str(value))
            )
    return output


def evidence_table(rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return display_frame(pd.DataFrame(rows))


def memory_counts(events: list[Any]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for event in events:
        stage_counts = counts.setdefault(event.stage, {"read": 0, "write": 0})
        stage_counts[event.event_type] = stage_counts.get(event.event_type, 0) + 1
    return counts


def render_stage_flow(events: list[Any] | None = None) -> None:
    counts = memory_counts(events or [])
    event_stage_by_title = {
        "Ingestion": "Ingestion",
        "Classification": "Classification",
        "Reconciliation": "Reconciliation",
        "Narrative": "Narrative",
        "Demo Surface": "Memory",
    }
    cols = st.columns(5, gap="small")
    for col, (num, title, detail) in zip(cols, STAGES):
        stage_key = event_stage_by_title[title]
        read_count = counts.get(stage_key, {}).get("read", 0)
        write_count = counts.get(stage_key, {}).get("write", 0)
        foot = f"{read_count} recall / {write_count} writes" if events else "ready"
        with col:
            st.markdown(
                f"""
                <div class="stage-card">
                  <div class="num">{html(num)}</div>
                  <strong>{html(title)}</strong>
                  <p>{html(detail)}</p>
                  <div class="stage-foot">{html(foot)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_memory_events(events: list[Any], limit: int = 10) -> None:
    for event in events[-limit:]:
        label = "RECALL" if event.event_type == "read" else "WRITE"
        panel(
            f"{label} / {event.key}",
            event.summary,
            f"{event.stage} · {event.source} · {event.created_at}",
            dark=True,
        )


def top_risk_panels(risk_rows: list[dict[str, Any]], limit: int = 4) -> None:
    for row in risk_rows[:limit]:
        reasons = "; ".join(row["reasons"][:2])
        st.markdown(
            f"""
            <div class="panel panel-tight">
              <strong>{html(row['account_name'])}</strong>
              <div style="margin-bottom:4px">
                {risk_chip(row['label'])}
                {chip('score ' + str(row['score']))}
                {chip('p=' + str(row['probability']), 'chip-blue')}
              </div>
              <p class="small-note">{html(reasons)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_selected_account(result: Any, risk_rows: list[dict[str, Any]]) -> None:
    account_options = {
        f"{row['label'].upper()} · {row['account_name']} · score {row['score']}": row["account_id"]
        for row in risk_rows
    }
    selected_label = st.selectbox("Inspect account evidence", options=list(account_options.keys()))
    selected_account_id = account_options[selected_label]
    evidence = result.evidence_by_account[selected_account_id]
    selected_risk = evidence["risk"]
    usage_summary = evidence["usage_summary"]

    st.markdown(
        f"""
        <div class="evidence-head">
          <div class="kicker">Selected account evidence chain</div>
          <h2>{html(selected_risk['account_name'])}</h2>
          <div>
            {risk_chip(selected_risk['label'])}
            {chip('SCORE ' + str(selected_risk['score']))}
            {chip('P=' + str(selected_risk['probability']), 'chip-blue')}
            {chip('CONF ' + str(selected_risk['confidence']), 'chip-green')}
          </div>
          <p class="small-note">{html('; '.join(selected_risk['reasons']))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    usage_cols = st.columns(4, gap="small")
    usage_cols[0].metric("Post API errors", usage_summary.get("post_api_error_avg", 0))
    usage_cols[1].metric("Pre workflow", usage_summary.get("pre_workflow_avg", 0))
    usage_cols[2].metric("Post workflow", usage_summary.get("post_workflow_avg", 0))
    usage_cols[3].metric("Active users", usage_summary.get("latest_active_users", 0))

    tab_tickets, tab_opps, tab_proof = st.tabs(["Support Trail", "Revenue Exposure", "Dataset Proof"])
    with tab_tickets:
        st.dataframe(evidence_table(evidence["tickets"]), use_container_width=True, hide_index=True)
    with tab_opps:
        st.dataframe(evidence_table(evidence["opportunities"]), use_container_width=True, hide_index=True)
    with tab_proof:
        st.json({"row_counts": result.dataset_profile["row_counts"], "date_ranges": result.dataset_profile["date_ranges"]})


with st.sidebar:
    st.subheader("Demo Controls")
    use_cognee = st.toggle("Use Cognee memory writes", value=False)
    use_llm = st.toggle("Use Anthropic narrative", value=False)
    run_clicked = st.button("Run Five-Agent Pipeline", type="primary", use_container_width=True)
    reset_clicked = st.button("Reset cached result", use_container_width=True)
    st.caption("Default mode is local. Enable external calls only when you want to demonstrate that path.")

if reset_clicked:
    st.session_state.pop("pipeline_result", None)
    st.session_state.pop("pipeline_error", None)

if run_clicked:
    with st.spinner("Running five agents..."):
        try:
            st.session_state["pipeline_result"] = run_cached_pipeline(use_cognee=use_cognee, use_llm=use_llm)
            st.session_state.pop("pipeline_error", None)
        except Exception as exc:
            st.session_state["pipeline_error"] = str(exc)

if "pipeline_error" in st.session_state:
    st.error(f"Pipeline failed: {st.session_state['pipeline_error']}")

if "pipeline_result" not in st.session_state:
    tables = load_tables(DEFAULT_DATA_DIR)
    render_header("READY", use_cognee, use_llm)

    metric_cols = st.columns(4, gap="small")
    metric_cols[0].metric("Ready tables", len(tables))
    metric_cols[1].metric("Accounts", len(tables["accounts"]))
    metric_cols[2].metric("Support tickets", len(tables["support_tickets"]))
    metric_cols[3].metric("Incidents", len(tables["incident_log"]))

    section_title("Demo logic before run")
    render_stage_flow()

    left, right = st.columns([1.45, 1.0], gap="large")
    with left:
        section_title("Data pack readiness")
        table_summary = pd.DataFrame(
            [
                {"table": name, "rows": len(frame), "columns": len(frame.columns)}
                for name, frame in tables.items()
            ]
        )
        st.dataframe(table_summary, use_container_width=True, hide_index=True)
    with right:
        section_title("Runbook")
        panel("First click", "Run the pipeline with local memory and template narrative.", "fastest stable path")
        panel("Second click", "Select a critical account and walk through tickets, usage, and opportunity exposure.", "evidence chain")
        panel("Judge point", "The key differentiator is memory handoff: each conclusion is traceable to prior agent writes and recalls.", "sponsor fit")
    st.stop()

result = st.session_state["pipeline_result"]
profile = result.dataset_profile
classification = result.classification
reconciliation = result.reconciliation
narrative = result.narrative

row_counts = profile["row_counts"]
label_counts = classification["label_counts"]
risk_rows = classification["risk_scores"]
risk_df = pd.DataFrame(risk_rows)

render_header("LIVE", use_cognee, use_llm)

metric_cols = st.columns(5, gap="small")
metric_cols[0].metric("Tables loaded", len(row_counts))
metric_cols[1].metric("Tickets matched", reconciliation["summary"]["tickets_matched"])
metric_cols[2].metric("Critical accounts", label_counts.get("critical", 0))
metric_cols[3].metric("High accounts", label_counts.get("high", 0))
metric_cols[4].metric("Memory events", len(result.memory_events))

section_title("Five-agent handoff map")
render_stage_flow(result.memory_events)

top_left, top_right = st.columns([1.35, 1.0], gap="large")
with top_left:
    section_title("Risk command table")
    display_df = risk_df[
        ["account_id", "account_name", "segment", "arr", "label", "score", "probability", "confidence", "reasons"]
    ].copy()
    display_df["reasons"] = display_df["reasons"].apply(lambda values: "; ".join(values[:3]))
    st.dataframe(display_frame(display_df.head(12)), use_container_width=True, hide_index=True)

with top_right:
    section_title("Top risk radar")
    top_risk_panels(risk_rows, limit=4)

main_left, main_right = st.columns([1.35, 1.0], gap="large")
with main_left:
    section_title("Account evidence drill-down")
    render_selected_account(result, risk_rows)

with main_right:
    section_title("Executive action package")
    st.markdown(
        f"""
        <div class="narrative">
          <div class="kicker">Executive narrative</div>
          <h2>{html(narrative['title'])}</h2>
          <p>{html(narrative['what_happened'])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    action_tab, question_tab, memory_tab, quality_tab = st.tabs(["Actions", "Questions", "Memory", "Quality"])
    with action_tab:
        for index, action in enumerate(narrative["actions"], start=1):
            panel(f"Action {index}", action)
    with question_tab:
        for index, item in enumerate(narrative["uncertainty"], start=1):
            panel(f"Question {index}", item)
    with memory_tab:
        render_memory_events(result.memory_events, limit=10)
    with quality_tab:
        for issue in profile["suspicious_records"]:
            panel(str(issue["table"]), f"{issue['count']} {issue['issue']}", "ingestion quality flag")

with st.expander("Raw memory events"):
    st.json([asdict(event) for event in result.memory_events])
