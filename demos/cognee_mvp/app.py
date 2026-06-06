from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_LOG_PATH = PROJECT_ROOT / ".cache" / "cognee_mvp_events.json"
DATASET_NAME = "cognee_mvp_minimal_memory"

DEFAULT_FACTS = [
    {
        "source": "incident_log",
        "text": (
            "On 2026-06-05, Acme Ops saw a post-incident API error spike. "
            "The renewal is 31 days away and the executive owner is Mei Chen."
        ),
    },
    {
        "source": "usage_events",
        "text": (
            "Acme Ops workflow completions fell by 42% after the Data Sync incident. "
            "Customer Success promised a remediation plan before Monday."
        ),
    },
    {
        "source": "support_ticket",
        "text": (
            "Support ticket T-778 and incident row INC-042 are the evidence to cite "
            "when explaining the Acme Ops escalation."
        ),
    },
]

DEFAULT_QUERY = "What should I remember about the Acme Ops renewal risk?"


@dataclass
class DemoEvent:
    step: str
    detail: str
    backend: str
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


def configure_page() -> None:
    st.set_page_config(page_title="Cognee Minimal Memory MVP", layout="wide", initial_sidebar_state="expanded")
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

        :root {
          --paper: #f4f0e8;
          --ink: #151718;
          --muted: #5e655f;
          --panel: #fffdf7;
          --line: #c9c0ad;
          --black: #151718;
          --blue: #175d7a;
          --green: #2f6f4f;
          --amber: #a46a20;
          --red: #a93a32;
        }

        .stApp {
          background:
            linear-gradient(90deg, rgba(21,23,24,.055) 1px, transparent 1px),
            linear-gradient(0deg, rgba(21,23,24,.045) 1px, transparent 1px),
            radial-gradient(circle at 20% 12%, rgba(23,93,122,.12), transparent 30%),
            radial-gradient(circle at 86% 8%, rgba(47,111,79,.12), transparent 28%),
            var(--paper);
          background-size: 28px 28px, 28px 28px, auto, auto, auto;
          color: var(--ink);
        }

        html, body, [class*="css"] {
          font-family: 'Archivo', 'Segoe UI', sans-serif;
        }

        .block-container {
          max-width: 1320px;
          padding: 22px 28px 42px;
        }

        header[data-testid="stHeader"], div[data-testid="stToolbar"] {
          visibility: hidden;
        }

        section[data-testid="stSidebar"] {
          background: #171918;
          border-right: 1px solid #3d413d;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
          color: #f7f1e6;
        }

        .hero {
          border: 1px solid var(--black);
          background: rgba(255,253,247,.95);
          box-shadow: 7px 7px 0 rgba(21,23,24,.92);
          padding: 18px 20px 16px;
          margin-bottom: 16px;
        }

        .kicker, .mono, .step-index, .call-label {
          font-family: 'IBM Plex Mono', monospace;
        }

        .kicker {
          color: var(--red);
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
        }

        .hero h1 {
          margin: 5px 0 8px;
          font-size: clamp(34px, 5vw, 64px);
          line-height: .95;
          letter-spacing: 0;
        }

        .hero p {
          margin: 0;
          max-width: 900px;
          color: var(--muted);
          font-size: 15px;
          line-height: 1.5;
        }

        .bench {
          border: 1px solid var(--line);
          background: rgba(255,253,247,.93);
          padding: 13px 14px;
          min-height: 154px;
          margin-bottom: 10px;
        }

        .bench-strong {
          border-color: var(--black);
          box-shadow: 4px 4px 0 rgba(21,23,24,.88);
        }

        .step-index {
          color: var(--muted);
          font-size: 11px;
          text-transform: uppercase;
        }

        .bench h3 {
          margin: 4px 0 8px;
          font-size: 18px;
        }

        .bench p, .event-row p {
          margin: 0;
          color: var(--muted);
          font-size: 14px;
          line-height: 1.45;
        }

        .call {
          border-left: 4px solid var(--blue);
          background: #eef5f3;
          padding: 9px 10px;
          margin-top: 10px;
        }

        .call-label {
          color: var(--blue);
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          margin-bottom: 4px;
        }

        .status {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          border: 1px solid var(--black);
          background: #f8e6bf;
          color: var(--ink);
          padding: 5px 8px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          margin: 0 6px 6px 0;
        }

        .status-blue { background: #dcecf0; color: var(--blue); }
        .status-green { background: #dceade; color: var(--green); }
        .status-red { background: #f3d8d2; color: var(--red); }

        .event-row {
          border: 1px solid var(--line);
          background: rgba(255,253,247,.92);
          padding: 10px 12px;
          margin-bottom: 8px;
        }

        .event-row strong {
          display: block;
          margin-bottom: 3px;
        }

        div.stButton > button {
          border-radius: 4px;
          border: 1px solid var(--black);
          background: var(--black);
          color: #fffdf7;
          font-weight: 800;
          min-height: 40px;
        }

        div.stButton > button:hover {
          border-color: var(--blue);
          background: var(--blue);
          color: #fffdf7;
        }

        textarea, input {
          font-family: 'IBM Plex Mono', monospace !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def has_real_key(name: str) -> bool:
    value = os.getenv(name, "").strip()
    return bool(value and "your_" not in value.lower() and "placeholder" not in value.lower())


def load_events() -> list[DemoEvent]:
    if not LOCAL_LOG_PATH.exists():
        return []
    try:
        rows = json.loads(LOCAL_LOG_PATH.read_text(encoding="utf-8"))
        return [DemoEvent(**row) for row in rows]
    except Exception:
        return []


def save_events(events: list[DemoEvent]) -> None:
    LOCAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_LOG_PATH.write_text(
        json.dumps([asdict(event) for event in events], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_event(step: str, detail: str, backend: str, payload: dict[str, Any]) -> DemoEvent:
    events = load_events()
    event = DemoEvent(step=step, detail=detail, backend=backend, payload=payload)
    events.append(event)
    save_events(events)
    return event


def reset_events() -> None:
    if LOCAL_LOG_PATH.exists():
        LOCAL_LOG_PATH.unlink()


def run_async(coroutine: Any) -> Any:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)
    raise RuntimeError(f"Streamlit already has a running loop: {loop}")


async def cognee_remember(text: str) -> None:
    import cognee

    await cognee.remember(text, dataset_name=DATASET_NAME)


async def cognee_recall(query: str) -> Any:
    import cognee

    return await cognee.recall(query_text=query, datasets=[DATASET_NAME])


def cognee_timeout_seconds() -> float:
    return float(os.getenv("COGNEE_TIMEOUT_SECONDS", "15"))


def write_fact(fact: dict[str, str], use_cognee: bool) -> DemoEvent:
    memory_text = f"[{fact['source']}] {fact['text']}"
    if use_cognee:
        try:
            run_async(asyncio.wait_for(cognee_remember(memory_text), timeout=cognee_timeout_seconds()))
            return append_event(
                "remember",
                f"Stored {fact['source']} in {DATASET_NAME}",
                "cognee",
                {"dataset": DATASET_NAME, "text": memory_text},
            )
        except Exception as exc:
            return append_event(
                "remember",
                f"Cognee write failed; kept local copy for demo continuity.",
                "local fallback",
                {"dataset": DATASET_NAME, "text": memory_text, "error": str(exc)},
            )

    return append_event(
        "remember",
        f"Stored {fact['source']} in local fallback",
        "local fallback",
        {"dataset": DATASET_NAME, "text": memory_text},
    )


def local_recall(query: str, events: list[DemoEvent]) -> str:
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    candidates = []
    for event in events:
        text = str(event.payload.get("text", ""))
        score = len(words & set(re.findall(r"[a-z0-9]+", text.lower())))
        if score:
            candidates.append((score, text))

    selected = [text for _, text in sorted(candidates, reverse=True)[:3]]
    if not selected:
        return "No local memory matched this query yet. Write the seed facts first."
    return "\n\n".join(selected)


def recall_answer(query: str, use_cognee: bool) -> DemoEvent:
    if use_cognee:
        try:
            response = run_async(asyncio.wait_for(cognee_recall(query), timeout=cognee_timeout_seconds()))
            return append_event(
                "recall",
                f"Asked cognee to answer from {DATASET_NAME}",
                "cognee",
                {"dataset": DATASET_NAME, "query": query, "response": stringify_response(response)},
            )
        except Exception as exc:
            events = load_events()
            response = local_recall(query, events)
            return append_event(
                "recall",
                "Cognee recall failed; answered from local event log.",
                "local fallback",
                {"dataset": DATASET_NAME, "query": query, "response": response, "error": str(exc)},
            )

    events = load_events()
    response = local_recall(query, events)
    return append_event(
        "recall",
        "Answered from local event log.",
        "local fallback",
        {"dataset": DATASET_NAME, "query": query, "response": response},
    )


def stringify_response(response: Any) -> str:
    if isinstance(response, str):
        return response
    try:
        return json.dumps(response, ensure_ascii=False, indent=2, default=str)
    except TypeError:
        return str(response)


def render_flow(use_cognee: bool, ready_for_cognee: bool) -> None:
    backend_class = "status-green" if use_cognee and ready_for_cognee else "status-blue"
    backend_label = "cognee enabled" if use_cognee else "local fallback"
    key_label = "keys detected" if ready_for_cognee else "keys missing"

    st.markdown(
        f"""
        <div class="hero">
          <div class="kicker">Cognee memory loop / minimal MVP</div>
          <h1>Remember, then recall.</h1>
          <p>这个 demo 把 cognee 放在最小闭环里：把几条业务事实写进同一个 dataset，然后用一个自然语言问题把相关记忆召回。旁边的事件日志展示系统实际做了什么。</p>
          <div style="margin-top:12px">
            <span class="status {backend_class}">{backend_label}</span>
            <span class="status">{DATASET_NAME}</span>
            <span class="status {'status-green' if ready_for_cognee else 'status-red'}">{key_label}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="bench bench-strong">
              <div class="step-index">Step 01</div>
              <h3>Write memory</h3>
              <p>三条事实被写入同一个 dataset，后续 agent 不需要重新读取原始材料。</p>
              <div class="call">
                <div class="call-label">call</div>
                <code>await cognee.remember(text, dataset_name=...)</code>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="bench bench-strong">
              <div class="step-index">Step 02</div>
              <h3>Persist context</h3>
              <p>cognee 负责把自然语言上下文变成可被后续查询复用的记忆层。</p>
              <div class="call">
                <div class="call-label">dataset</div>
                <code>cognee_mvp_minimal_memory</code>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="bench bench-strong">
              <div class="step-index">Step 03</div>
              <h3>Recall by question</h3>
              <p>新的 agent 只发送问题，cognee 从 dataset 里取回相关上下文。</p>
              <div class="call">
                <div class="call-label">call</div>
                <code>await cognee.recall(query_text=..., datasets=[...])</code>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_events(events: list[DemoEvent]) -> None:
    st.markdown("#### Event log")
    if not events:
        st.info("No events yet. Write seed memory to start the loop.")
        return

    for event in reversed(events[-8:]):
        backend_class = "status-green" if event.backend == "cognee" else "status-blue"
        response = event.payload.get("response")
        error = event.payload.get("error")
        st.markdown(
            f"""
            <div class="event-row">
              <span class="status {backend_class}">{event.backend}</span>
              <span class="status">{event.step}</span>
              <strong>{event.detail}</strong>
              <p class="mono">{event.created_at}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if response:
            st.code(response, language="text")
        if error:
            with st.expander("Error details"):
                st.code(error, language="text")


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    configure_page()

    ready_for_cognee = has_real_key("LLM_API_KEY") and has_real_key("EMBEDDING_API_KEY")
    with st.sidebar:
        st.title("MVP Controls")
        use_cognee = st.toggle("Use real cognee calls", value=ready_for_cognee)
        st.caption("Without provider keys, the demo uses a tiny local fallback so the flow remains visible.")
        query = st.text_area("Recall query", value=DEFAULT_QUERY, height=110)

        loop_sidebar = st.button("Run full MVP loop", use_container_width=True, key="loop_sidebar")
        write_sidebar = st.button("Write seed memory", use_container_width=True, key="write_sidebar")
        recall_sidebar = st.button("Recall answer", use_container_width=True, key="recall_sidebar")
        reset_sidebar = st.button("Reset local log", use_container_width=True, key="reset_sidebar")

    render_flow(use_cognee=use_cognee, ready_for_cognee=ready_for_cognee)

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown("#### Seed facts")
        edited_facts = []
        for index, fact in enumerate(DEFAULT_FACTS, start=1):
            st.markdown(f"**{index}. {fact['source']}**")
            text = st.text_area(
                f"Fact {index}",
                value=fact["text"],
                label_visibility="collapsed",
                height=82,
                key=f"fact_{index}",
            )
            edited_facts.append({"source": fact["source"], "text": text})

        action_cols = st.columns(3)
        with action_cols[0]:
            loop_main = st.button("Run full MVP loop", use_container_width=True, key="loop_main")
        with action_cols[1]:
            write_main = st.button("Write seed memory", use_container_width=True, key="write_main")
        with action_cols[2]:
            recall_main = st.button("Recall answer", use_container_width=True, key="recall_main")

        if loop_sidebar or loop_main:
            for fact in edited_facts:
                write_fact(fact, use_cognee=use_cognee)
            recall_answer(query, use_cognee=use_cognee)
            st.toast("Full memory loop complete.")
            st.rerun()

        if write_sidebar or write_main:
            for fact in edited_facts:
                write_fact(fact, use_cognee=use_cognee)
            st.toast("Seed memory written.")
            st.rerun()

        if recall_sidebar or recall_main:
            recall_answer(query, use_cognee=use_cognee)
            st.toast("Recall complete.")
            st.rerun()

        if reset_sidebar:
            reset_events()
            st.toast("Local event log reset.")
            st.rerun()

    with right:
        events = load_events()
        latest_recall = next((event for event in reversed(events) if event.step == "recall"), None)
        st.markdown("#### Latest recall")
        if latest_recall:
            st.code(str(latest_recall.payload.get("response", "")), language="text")
        else:
            st.info("Run recall after writing memory.")
        render_events(events)


if __name__ == "__main__":
    main()
