from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from src.models import MemoryEvent


class MemoryStore:
    def __init__(
        self,
        dataset_name: str = "m_agents_hackathon",
        local_path: str | Path = ".cache/memory_events.json",
        use_cognee: bool = True,
    ) -> None:
        self.dataset_name = dataset_name
        self.local_path = Path(local_path)
        self.use_cognee = use_cognee
        self._events: list[MemoryEvent] = []
        self._cognee_available: bool | None = None

    @property
    def backend_label(self) -> str:
        if self.use_cognee and self._cognee_available:
            return "cognee+local"
        if self.use_cognee and self._cognee_available is None:
            return "cognee-pending+local"
        return "local"

    def remember(self, key: str, payload: dict[str, Any], stage: str, summary: str) -> MemoryEvent:
        source = "local"
        if self.use_cognee:
            try:
                self._run_async(self._remember_cognee(key, payload, stage, summary))
                self._cognee_available = True
                source = "cognee+local"
            except Exception:
                self._cognee_available = False
                source = "local-fallback"

        event = MemoryEvent(key=key, stage=stage, summary=summary, payload=payload, source=source)
        self._events.append(event)
        self._persist()
        return event

    def recall(self, query: str, keys: list[str] | None = None) -> list[MemoryEvent]:
        matched = [event for event in self._events if event.event_type == "write"]
        if keys:
            wanted = set(keys)
            matched = [event for event in matched if event.key in wanted]

        recall_event = MemoryEvent(
            key="memory_recall",
            stage="Memory",
            summary=f"Recall query: {query}",
            payload={"query": query, "keys": keys or [], "matched_keys": [event.key for event in matched]},
            event_type="read",
            source=self.backend_label,
            query=query,
        )
        self._events.append(recall_event)
        self._persist()
        return matched

    def list_events(self) -> list[MemoryEvent]:
        return list(self._events)

    def reset(self) -> None:
        self._events = []
        if self.local_path.exists():
            self.local_path.unlink()

    async def _remember_cognee(self, key: str, payload: dict[str, Any], stage: str, summary: str) -> None:
        if os.getenv("DISABLE_COGNEE", "").lower() in {"1", "true", "yes"}:
            raise RuntimeError("Cognee disabled by environment")
        import cognee

        text = json.dumps({"key": key, "stage": stage, "summary": summary, "payload": payload}, default=str)
        timeout = float(os.getenv("COGNEE_TIMEOUT_SECONDS", "3"))
        await asyncio.wait_for(cognee.remember(text, dataset_name=self.dataset_name), timeout=timeout)

    def _run_async(self, coroutine: Any) -> Any:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coroutine)
        return loop.run_until_complete(coroutine)

    def _persist(self) -> None:
        self.local_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [event.__dict__ for event in self._events]
        self.local_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
