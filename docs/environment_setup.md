# Environment Setup

This project is a demo Streamlit application. Share the environment files, not private keys, local caches, virtual environments, or demo-only generated artifacts.

## Recommended Sharing Method

For the team, share a small Git repository or zip package that includes:

- `requirements.txt`
- `.env.example`
- `app.py`
- `src/`
- `tools/`
- `docs/environment_setup.md`

Do not share:

- `.env`
- `.venv/`
- `.data_storage/`
- `.cognee_system/`
- `.cognee_cache/`
- `__pycache__/`
- private datasets or generated demo artifacts unless explicitly needed

The current `.gitignore` already excludes the sensitive/local environment folders above.

## Python Version

Use Python 3.12. The current local environment was verified with:

```powershell
Python 3.12.4
```

Python 3.11 should likely work, but Python 3.12 is the known-good target for this demo.

## Windows Setup

From the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Then edit `.env`.

For a local-only rehearsal, API keys can be left as placeholders because the app defaults to:

- local memory fallback
- template narrative fallback

To run:

```powershell
streamlit run app.py
```

Or with an explicit port:

```powershell
streamlit run app.py --server.port 8506
```

## macOS / Linux Setup

From the project root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env`.

To run:

```bash
streamlit run app.py
```

## Optional API Configuration

The app can run without external services. External services should be enabled only when needed for a live sponsor demo.

### Anthropic Narrative

If you want the Narrative Agent to call Anthropic, add:

```env
ANTHROPIC_API_KEY=your_key_here
```

Then enable `Use Anthropic narrative` in the Streamlit sidebar.

### Cognee Memory

Cognee configuration is represented in `.env.example`.

Important: the Cognee path values in `.env.example` are absolute paths. Each teammate should update them to their own local project path:

```env
DATA_ROOT_DIRECTORY=C:/path/to/project/.data_storage
SYSTEM_ROOT_DIRECTORY=C:/path/to/project/.cognee_system
CACHE_ROOT_DIRECTORY=C:/path/to/project/.cognee_cache
```

Then enable `Use Cognee memory writes` in the Streamlit sidebar.

If Cognee is not configured or fails, the app falls back to local memory events.

## Validation

Run the pipeline validation:

```powershell
python tools/validate_pipeline.py
```

Expected checks:

- six CSV tables load successfully
- account risk labels are produced
- ticket reconciliation runs
- pipeline completes end to end

Compile check:

```powershell
python -m compileall app.py src tools
```

## Team Hand-off Notes

For this demo project, the safest environment-sharing approach is:

1. Commit `requirements.txt`, `.env.example`, and `docs/environment_setup.md`.
2. Ask every teammate to create their own `.env`.
3. Never commit `.env`, `.venv`, Cognee local state, cache folders, or generated demo artifacts.
4. Keep external-service toggles off for first run.
5. Enable Anthropic or Cognee one at a time during rehearsal.

