# Cognee Minimal MVP

This is a small standalone Streamlit demo that shows the core Cognee loop:

1. write facts with `cognee.remember(...)`
2. keep them in one named dataset
3. recall them with `cognee.recall(...)`
4. show the event log so the memory layer is visible

## Run

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run demos/cognee_mvp/app.py --server.port 8507
```

If `LLM_API_KEY` and `EMBEDDING_API_KEY` are configured in `.env`, turn on
`Use real cognee calls`. If not, the demo falls back to a tiny local text recall
so the MVP still demonstrates the control flow.

Use `Run full MVP loop` for the fastest live demo. It writes the seed facts and
then immediately asks the recall question.

## Dataset

The demo writes to:

```text
cognee_mvp_minimal_memory
```

Local event logs are stored at:

```text
.cache/cognee_mvp_events.json
```
