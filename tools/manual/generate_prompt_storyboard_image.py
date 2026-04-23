#!/usr/bin/env python3
"""Generate one storyboard/reference image from a prompt file through GUIVM.

This generic manual helper is used for user-supplied storyboard prompts. It waits
for GUIVM capacity, calls /v1/llm-gate/infer, decodes the first returned image,
and saves raw request/response records with signed remote image URLs and base64
payloads redacted.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import struct
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "http://10.0.2.2:8765"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = PROJECT_ROOT / "outputs" / "storyboard-images" / "custom-guivm-storyboard"


def utc_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def http_json(method: str, url: str, body: dict[str, Any] | None = None, timeout: int = 60) -> tuple[int, dict[str, Any]]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"raw": raw}
        return exc.code, payload


def capacity_ready(cap: dict[str, Any]) -> tuple[bool, int, str]:
    running = int(cap.get("running") or 0)
    max_concurrency = int(cap.get("max_concurrency") or 1)
    quota = cap.get("infer_quota") or {}
    minute = quota.get("per_minute") or {}
    phase = quota.get("phase") or {}
    cooldown = cap.get("upstream_cooldown") or {}
    next_allowed = int(phase.get("next_allowed_in_sec") or 0)
    minute_remaining = int(minute.get("remaining") or 0)
    reset_after = int(minute.get("reset_after_sec") or 0)
    cooldown_remaining = int(cooldown.get("remaining_sec") or 0) if cooldown.get("active") else 0
    ready = running < max_concurrency and next_allowed <= 0 and minute_remaining > 0 and cooldown_remaining <= 0
    wait = max(next_allowed, reset_after if minute_remaining <= 0 else 0, cooldown_remaining, 3)
    reason = f"running={running}/{max_concurrency}, minute_remaining={minute_remaining}, next_allowed={next_allowed}, cooldown={cooldown_remaining}"
    return ready, wait, reason


def wait_for_capacity(base_url: str, deadline_sec: int, raw_dir: Path) -> dict[str, Any]:
    deadline = time.monotonic() + deadline_sec
    last_cap: dict[str, Any] | None = None
    while True:
        status, cap = http_json("GET", f"{base_url}/v1/llm-gate/capacity", timeout=30)
        cap["_http_status"] = status
        cap["_checked_at"] = datetime.now(timezone.utc).isoformat()
        last_cap = cap
        (raw_dir / "capacity-last.json").write_text(json.dumps(cap, ensure_ascii=False, indent=2), encoding="utf-8")
        if status == 200:
            ready, wait, reason = capacity_ready(cap)
            print(f"[capacity] {reason}; ready={ready}", flush=True)
            if ready:
                return cap
        else:
            wait = 10
            print(f"[capacity] unexpected HTTP {status}; retrying", flush=True)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            last_excerpt = json.dumps(last_cap, ensure_ascii=False)[:1000]
            raise TimeoutError(f"GUIVM capacity wait timed out after {deadline_sec}s; last={last_excerpt}")
        time.sleep(min(max(wait, 3), 30, max(1, int(remaining))))


def sanitize_for_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            key_l = str(key).lower()
            if key == "data_base64" and isinstance(value, str):
                out[key] = f"<omitted {len(value)} base64 chars; decoded image saved separately>"
            elif key == "src" and isinstance(value, str) and ("sig=" in value or "backend-api/estuary" in value or "file_000000" in value):
                out[key] = "<redacted signed remote image URL; decoded image saved separately>"
            elif key_l in {"authorization", "api_key", "apikey", "token", "password", "secret", "credential"}:
                out[key] = "[REDACTED]"
            else:
                out[key] = sanitize_for_json(value)
        return out
    if isinstance(obj, list):
        return [sanitize_for_json(x) for x in obj]
    if isinstance(obj, str):
        return re.sub(r"(sig=)[^&\s\"]+", r"\1[REDACTED]", obj)
    return obj


def decode_image_data(data_base64: str) -> bytes:
    if data_base64.startswith("data:"):
        data_base64 = data_base64.split(",", 1)[1]
    return base64.b64decode(data_base64)


def png_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        width, height = struct.unpack(">II", data[16:24])
        return int(width), int(height)
    return None, None


def save_image_from_response(response: dict[str, Any], out_dir: Path, slug: str) -> dict[str, Any]:
    output = response.get("output") or {}
    images = output.get("images") or []
    if not images:
        text = output.get("text")
        raise RuntimeError(f"GUIVM returned no output.images; output.text={text!r}")
    first = images[0]
    data = first.get("data_base64") or ""
    if not data:
        raise RuntimeError("GUIVM image entry has no data_base64")
    blob = decode_image_data(data)
    image_path = out_dir / f"{slug}.png"
    image_path.write_bytes(blob)
    width, height = png_dimensions(blob)
    sha256 = hashlib.sha256(blob).hexdigest()
    return {
        "slug": slug,
        "image_path": str(image_path),
        "bytes": len(blob),
        "sha256": sha256,
        "sha256_16": sha256[:16],
        "width": width,
        "height": height,
        "mime_type": first.get("mime_type"),
        "alt": first.get("alt"),
        "remote_src": "<redacted signed remote image URL; decoded image saved separately>" if first.get("src") else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--wait-timeout-sec", type=int, default=900)
    parser.add_argument("--infer-timeout-sec", type=int, default=900)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    out_dir: Path = args.out_dir
    raw_dir = out_dir / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    prompt = args.prompt_file.read_text(encoding="utf-8").strip()
    prompt_path = out_dir / f"{args.slug}.prompt.txt"
    if args.prompt_file.resolve() != prompt_path.resolve():
        prompt_path.write_text(prompt + "\n", encoding="utf-8")

    status, health = http_json("GET", f"{args.base_url}/v1/health", timeout=30)
    health["_http_status"] = status
    (raw_dir / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")
    if status != 200 or not health.get("ok"):
        raise RuntimeError(f"GUIVM health check failed: HTTP {status} {health}")

    existing = out_dir / f"{args.slug}.png"
    if existing.exists() and not args.force:
        data = existing.read_bytes()
        width, height = png_dimensions(data)
        info = {
            "slug": args.slug,
            "image_path": str(existing),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "width": width,
            "height": height,
            "skipped_existing": True,
        }
    else:
        last_error = None
        info = None
        for attempt in range(1, args.retries + 2):
            print(f"[image] {args.slug} attempt {attempt}", flush=True)
            capacity = wait_for_capacity(args.base_url, args.wait_timeout_sec, raw_dir)
            request_id = f"noise-custom-storyboard-{utc_slug()}-{args.slug}-try{attempt}"
            body = {
                "request_id": request_id,
                "trace_id": request_id,
                "stage": "storyboard-image",
                "symbol": "NOISE",
                "model": {"name": "thinking", "reasoning_effort": "high"},
                "policy": {"timeout_sec": args.infer_timeout_sec},
                "prompt": {"compiled_prompt": prompt},
                "media": {"images": []},
                "capacity_before": capacity,
            }
            request_path = raw_dir / f"{args.slug}-try{attempt}-request.json"
            response_path = raw_dir / f"{args.slug}-try{attempt}-response.json"
            request_path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
            send_body = dict(body)
            send_body.pop("capacity_before", None)
            started = time.monotonic()
            status, response = http_json("POST", f"{args.base_url}/v1/llm-gate/infer", body=send_body, timeout=args.infer_timeout_sec + 180)
            elapsed = round(time.monotonic() - started, 3)
            response_path.write_text(
                json.dumps(sanitize_for_json({"http_status": status, "elapsed_sec": elapsed, "response_json": response}), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"[infer] HTTP {status} elapsed={elapsed}s", flush=True)
            if status in {409, 429, 503}:
                last_error = f"HTTP {status}: retryable"
                time.sleep(60)
                continue
            if status != 200:
                last_error = f"HTTP {status}: {json.dumps(response, ensure_ascii=False)[:500]}"
                continue
            try:
                info = save_image_from_response(response, out_dir, args.slug)
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                print(f"[no-image] {last_error}", flush=True)
                time.sleep(70)
                continue
            break
        if info is None:
            raise RuntimeError(last_error or "image generation failed")

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "prompt_file": str(prompt_path),
        "entries": [info],
        "notes": [
            "Single user-supplied Seedance storyboard-reference image.",
            "Prompt files define the requested frame/shot count and layout policy.",
            "Raw response files redact signed remote image URLs and omit base64 image payloads.",
        ],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    readme = f"""# GUIVM Seedance Storyboard Reference

Generated from a user-supplied storyboard prompt.

- Prompt: `{prompt_path}`
- Image: `{info['image_path']}`
- Manifest: `{out_dir / 'manifest.json'}`
- Raw GUIVM records: `{raw_dir}`

The prompt uses a Seedance Reference-mode storyboard role: use this image as a storyboard to guide the scenes.
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    sha_short = info.get("sha256_16") or str(info.get("sha256", ""))[:16]
    print(
        f"[saved] {info['image_path']} bytes={info['bytes']} sha256={sha_short} "
        f"width={info.get('width')} height={info.get('height')}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
