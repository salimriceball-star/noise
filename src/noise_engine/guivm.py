from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass(slots=True)
class GUIVMClient:
    base_url: str = "http://10.0.2.2:8765"
    symbol: str = "noise"
    reasoning_effort: str = "medium"
    timeout_sec: int = 240
    capacity_wait_timeout_sec: int = 180
    busy_poll_interval_sec: int = 10
    session: requests.Session = field(init=False, repr=False)
    last_exchange: dict[str, Any] | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self.session = requests.Session()

    def check_health(self) -> dict:
        response = self.session.get(f"{self.base_url}/v1/health", timeout=30)
        response.raise_for_status()
        return response.json()

    def check_capacity(self) -> dict:
        response = self.session.get(f"{self.base_url}/v1/llm-gate/capacity", timeout=30)
        response.raise_for_status()
        return response.json()

    def wait_for_capacity(self, extra_buffer: int = 2, max_total_wait_sec: int | None = None) -> dict:
        wait_budget = max_total_wait_sec if max_total_wait_sec is not None else self.capacity_wait_timeout_sec
        deadline = time.time() + wait_budget
        while True:
            data = self.check_capacity()
            running = data.get("running", 0) or 0
            next_allowed = data.get("infer_quota", {}).get("phase", {}).get("next_allowed_in_sec", 0) or 0
            wait_s = 0
            if next_allowed > 0:
                wait_s = max(wait_s, next_allowed + extra_buffer)
            if running > 0:
                wait_s = max(wait_s, self.busy_poll_interval_sec)
            if wait_s <= 0:
                return data
            remaining = deadline - time.time()
            if remaining <= 0 or wait_s > remaining:
                raise TimeoutError(
                    "GUIVM capacity wait timed out "
                    f"after {wait_budget}s (running={running}, next_allowed={next_allowed})"
                )
            time.sleep(wait_s)

    def infer_json(self, *, stage: str, symbol: str, prompt: str, request_id: str) -> dict:
        capacity_before = self.wait_for_capacity()
        body = {
            "request_id": request_id,
            "trace_id": request_id,
            "stage": stage,
            "symbol": symbol,
            "model": {"name": "thinking", "reasoning_effort": self.reasoning_effort},
            "policy": {"timeout_sec": self.timeout_sec},
            "prompt": {"compiled_prompt": prompt},
        }
        response = self.session.post(f"{self.base_url}/v1/llm-gate/infer", json=body, timeout=self.timeout_sec + 60)
        response.raise_for_status()
        payload = response.json()
        parsed = self._extract_json(payload)
        self.last_exchange = {
            "request_body": body,
            "capacity_before": capacity_before,
            "http_status": response.status_code,
            "response_json": payload,
            "parsed_json": parsed,
        }
        return parsed

    def export_last_exchange(self) -> dict[str, Any] | None:
        return self.last_exchange

    def _extract_json(self, payload: dict[str, Any]) -> dict:
        output = payload.get("output") or {}
        json_payload = output.get("json")
        if isinstance(json_payload, dict):
            return json_payload
        text = output.get("text", "") or ""
        try:
            return json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                return json.loads(match.group(0))
        raise ValueError("GUIVM response did not contain valid JSON output")
