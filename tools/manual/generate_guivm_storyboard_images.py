#!/usr/bin/env python3
"""Generate Noise storyboard candidate images through GUIVM.

This script is intentionally project-local and manual: it waits for the GUIVM
single-concurrency/min-interval gate, calls /v1/llm-gate/infer, verifies that
output.images contains at least one image, decodes the first image, and records
request/response metadata for reproducibility without duplicating base64 blobs in git.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import struct
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "http://10.0.2.2:8765"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "outputs" / "storyboards" / "2026-04-23-all-ideas-v3"
DEFAULT_OUT_DIR = PROJECT_ROOT / "outputs" / "storyboard-images" / "2026-04-23-guivm-seedance-v3"


@dataclass(frozen=True)
class Candidate:
    index: int
    slug: str
    title: str
    source_file: Path
    visual_focus: str
    caption_gap: str
    copy_line: str


CANDIDATES = [
    Candidate(
        1,
        "v3-001-humanoid-wheel-care-labor",
        "Humanoid robot: human shape hides an efficiency ledger",
        SOURCE_DIR / "v3-001-humanoid-wheel-care-labor.txt",
        "A wheeled humanoid robot helps in a Korean apartment/care setting while caregivers, residents, and children quietly renegotiate what human presence is worth.",
        "The caption praises universal care and efficiency while the scenes show human trust, labor schedules, and everyday contact being redesigned as dashboard options.",
        "사람을 닮은 기계가 먼저 빌리는 것은 손이 아니라 신뢰다.",
    ),
    Candidate(
        2,
        "v3-002-ai-storyboard-labor-value",
        "AI storyboard workflow: access hides the price of taste",
        SOURCE_DIR / "v3-002-ai-storyboard-labor-value.txt",
        "A small Korean pet shop uses an AI 3x3 storyboard/video workflow to make an ad while a freelance designer sees the proposal disappear from the estimate.",
        "The caption sells creative access for everyone while the scenes show accumulated taste and labor becoming a removable workflow cost.",
        "창작은 사라지지 않는다. 다만 견적서에서 먼저 사라진다.",
    ),
    Candidate(
        3,
        "v3-003-birth-contract-language-reality",
        "Low-birth language: soft words meet family condition sheets",
        SOURCE_DIR / "v3-003-birth-contract-language-reality.txt",
        "A public-office team softens low-birth wording while a Korean couple turns childbirth planning into a contract-like checklist at home.",
        "The caption praises responsible planning and careful language while the scenes show unchanged costs, waiting lists, and intimacy becoming negotiation.",
        "현실을 바로 못 바꾸는 사회는 말을 고치고, 사람들은 조건을 적기 시작한다.",
    ),
]


def now_slug() -> str:
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
            raise TimeoutError(f"GUIVM capacity wait timed out after {deadline_sec}s; last={json.dumps(last_cap, ensure_ascii=False)[:1000]}")
        time.sleep(min(max(wait, 3), 30, max(1, int(remaining))))


def extract_storyboard_seed(text: str) -> str:
    lines = text.splitlines()
    start = None
    end = None
    for i, line in enumerate(lines):
        if line.strip().startswith("## 6-Cut Storyboard Seed"):
            start = i + 1
        elif start is not None and line.strip().startswith("## Copy Variants"):
            end = i
            break
    if start is None:
        return text[:1800]
    return "\n".join(lines[start:end]).strip()


def extract_axes(text: str) -> dict[str, str]:
    keys = ["surface_claim", "implicit_premise", "viewer_meta_message", "main_axis", "support_axis", "background_axis"]
    out: dict[str, str] = {}
    for key in keys:
        m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
        if m:
            out[key] = m.group(1).strip()
    return out


def build_prompt(candidate: Candidate) -> str:
    source = candidate.source_file.read_text(encoding="utf-8")
    axes = extract_axes(source)
    seed = extract_storyboard_seed(source)
    return f"""Generate exactly one image now. Do not answer with analysis, explanation, or markdown. The deliverable must be a single generated image.

Create a Seedance 2.0-ready storyboard reference image for a social-media video in the Noise project. This is not ragebait; it is an interpretation-collision storyboard: the viewer should feel the gap between what the caption says and what the scenes quietly imply.

Seedance 2.0 usage target, based on Runway guidance:
- The generated image will be used as Reference mode input, with a later video prompt like: "use Image 1 as a storyboard to guide the scenes."
- Build the image as a clear multi-shot storyboard/reference board that Seedance can read visually, not as a text-heavy presentation slide.
- Use positive, unambiguous, outcome-focused visual language. Show what should happen, not a list of what to avoid.
- References are flexible: this single board should define subject continuity, Seoul background, scene progression, lighting mood, and shot rhythm.
- Since Seedance supports director-level control over camera movement, lighting, and character performance, include visual cues for camera direction and performance through composition: establishing shots, tracking feel, over-the-shoulder inserts, close-ups, reaction shots, foreground/background blocking, and lingering aftermath frames.
- Do not depend on tiny written captions or detailed UI text; if text appears, keep it short, generic, and readable.

Mandatory setting and directing standard:
- The story is always set in Korea, in contemporary Seoul.
- Use realistic modern Seoul visual cues where appropriate: apartment complexes, officetels, public offices, subway/bus stops, cafés, narrow side streets, office buildings, elevators, convenience stores, Hangang/Han River glimpses, or Seoul night lighting.
- The storyboard should feel like a professional director's shooting plan for immersive video content, with cinematic continuity and emotional blocking.
- The layout does not have to be a 3x3 grid. Use the clearest layout for Seedance: a cinematic contact sheet, horizontal shot strip, 2-row board, or 3x3 board are all acceptable.
- Include 6 to 9 clearly numbered shots. Prefer 9 shots when readability stays strong, but never sacrifice shot clarity for a rigid grid.
- The shots do not need to be 6-9 different topics. They may be different directorial treatments, angles, emotional beats, or camera distances within the same topic.

Visual style:
- clean premium storyboard / cinematic previsualization board
- realistic contemporary Seoul environments, cinematic but restrained
- consistent characters, wardrobe, props, and location logic across shots
- generic app and public-office UI only; no real platform names, no brand logos, no real person likenesses
- subtle tension, not horror, not slapstick, not mockery
- brand-safe: no sexualization, no hate, no humiliation of children, parents, workers, non-parents, or public servants
- use clear panel borders or shot separators and small shot numbers
- keep the final image readable as one Seedance reference image

Candidate: {candidate.title}
Surface claim: {axes.get('surface_claim', '')}
Implicit premise: {axes.get('implicit_premise', '')}
Viewer meta-message: {axes.get('viewer_meta_message', '')}
Main/support/background axes: {axes.get('main_axis', '')} / {axes.get('support_axis', '')} / {axes.get('background_axis', '')}
Caption-scene gap to visualize: {candidate.caption_gap}
Suggested copy mood: {candidate.copy_line}
Visual focus: {candidate.visual_focus}

Narrative seed to adapt into a Seedance-ready shot board:
{seed}

Recommended shot progression:
- Opening shot(s): establish modern Seoul location and the surface convenience/care promise.
- System/tool shot(s): show the device, app, robot, policy document, or workflow in use with insert/over-the-shoulder framing.
- Boundary/authority shot: show the moment where the system quietly crosses into a human relationship, labor value, or family decision.
- Reaction shot(s): close-ups or medium shots that reveal private/emotional/social cost without melodrama.
- Aftermath shot(s): wider or lingering final frame where the system appears to work on the surface, but the unresolved human relationship/value problem remains visible.
- Generate one complete Seedance-ready storyboard reference image only.
""".strip()


def make_body(candidate: Candidate, attempt: int, prompt: str, timeout_sec: int) -> dict[str, Any]:
    request_id = f"noise-storyboard-image-{now_slug()}-{candidate.slug}-try{attempt}"
    return {
        "request_id": request_id,
        "trace_id": request_id,
        "stage": "storyboard-image",
        "symbol": "NOISE",
        "model": {"name": "thinking", "reasoning_effort": "high"},
        "policy": {"timeout_sec": timeout_sec},
        "prompt": {"compiled_prompt": prompt},
        "media": {"images": []},
    }


def sanitize_for_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if key == "data_base64" and isinstance(value, str):
                out[key] = f"<omitted {len(value)} base64 chars; decoded image saved separately>"
            elif key == "src" and isinstance(value, str) and ("sig=" in value or "backend-api/estuary" in value):
                out[key] = "<redacted signed remote image URL; decoded image saved separately>"
            else:
                out[key] = sanitize_for_json(value)
        return out
    if isinstance(obj, list):
        return [sanitize_for_json(x) for x in obj]
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


def save_image_from_response(candidate: Candidate, response: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    output = response.get("output") or {}
    images = output.get("images") or []
    if not images:
        text = output.get("text")
        raise RuntimeError(f"GUIVM returned no output.images for {candidate.slug}; output.text={text!r}")
    first = images[0]
    data = first.get("data_base64") or ""
    if not data:
        raise RuntimeError(f"GUIVM image entry has no data_base64 for {candidate.slug}")
    blob = decode_image_data(data)
    image_path = out_dir / f"{candidate.slug}.png"
    image_path.write_bytes(blob)
    width, height = png_dimensions(blob)
    sha256 = hashlib.sha256(blob).hexdigest()
    return {
        "candidate": candidate.slug,
        "image_path": str(image_path),
        "bytes": len(blob),
        "sha256": sha256,
        "width": width,
        "height": height,
        "mime_type": first.get("mime_type"),
        "alt": first.get("alt"),
        "remote_src": "<redacted signed remote image URL; decoded image saved separately>" if first.get("src") else None,
    }


def generate_one(
    base_url: str,
    candidate: Candidate,
    out_dir: Path,
    raw_dir: Path,
    wait_timeout_sec: int,
    infer_timeout_sec: int,
    retries: int,
    force: bool,
) -> dict[str, Any]:
    existing = out_dir / f"{candidate.slug}.png"
    if existing.exists() and not force:
        data = existing.read_bytes()
        width, height = png_dimensions(data)
        return {
            "candidate": candidate.slug,
            "image_path": str(existing),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "width": width,
            "height": height,
            "skipped_existing": True,
        }

    prompt = build_prompt(candidate)
    prompt_path = out_dir / f"{candidate.slug}.prompt.txt"
    prompt_path.write_text(prompt + "\n", encoding="utf-8")

    last_error: str | None = None
    for attempt in range(1, retries + 2):
        print(f"[candidate] {candidate.slug} attempt {attempt}", flush=True)
        capacity = wait_for_capacity(base_url, wait_timeout_sec, raw_dir)
        body = make_body(candidate, attempt, prompt, infer_timeout_sec)
        body["capacity_before"] = capacity
        request_path = raw_dir / f"{candidate.slug}-try{attempt}-request.json"
        response_path = raw_dir / f"{candidate.slug}-try{attempt}-response.json"
        request_path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")

        send_body = dict(body)
        send_body.pop("capacity_before", None)
        started = time.monotonic()
        status, response = http_json("POST", f"{base_url}/v1/llm-gate/infer", body=send_body, timeout=infer_timeout_sec + 180)
        elapsed = round(time.monotonic() - started, 3)
        response_record = {
            "http_status": status,
            "elapsed_sec": elapsed,
            "response_json": response,
        }
        response_path.write_text(json.dumps(sanitize_for_json(response_record), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[infer] {candidate.slug} HTTP {status} elapsed={elapsed}s", flush=True)

        if status in {409, 429, 503}:
            last_error = f"HTTP {status}: {json.dumps(response, ensure_ascii=False)[:500]}"
            detail = (response.get("error") or {}).get("detail") if isinstance(response, dict) else None
            sleep_for = 60
            if isinstance(detail, dict):
                sleep_for = max(int(detail.get("remaining_sec") or 0), int(detail.get("reset_after_sec") or 0), 60)
            print(f"[retryable] {last_error}; sleeping {sleep_for}s", flush=True)
            time.sleep(min(sleep_for, 120))
            continue

        if status != 200:
            last_error = f"HTTP {status}: {json.dumps(response, ensure_ascii=False)[:800]}"
            print(f"[error] {last_error}", flush=True)
            continue

        try:
            info = save_image_from_response(candidate, response, out_dir)
        except Exception as exc:  # noqa: BLE001 - keep raw response for diagnosis and retry.
            last_error = str(exc)
            print(f"[no-image] {last_error}", flush=True)
            time.sleep(70)
            continue

        info["request_id"] = body["request_id"]
        info["attempt"] = attempt
        info["prompt_path"] = str(prompt_path)
        info["request_path"] = str(request_path)
        info["response_path"] = str(response_path)
        print(f"[saved] {info['image_path']} bytes={info['bytes']} sha256={info['sha256'][:16]}", flush=True)
        return info

    raise RuntimeError(f"failed to generate {candidate.slug}; last_error={last_error}")


def write_readme(out_dir: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# GUIVM Storyboard Images",
        "",
        f"generated_at_utc: {manifest['generated_at_utc']}",
        f"base_url: {manifest['base_url']}",
        "",
        "## Images",
    ]
    for item in manifest["images"]:
        lines.extend(
            [
                f"- {item['candidate']}",
                f"  - image: {item['image_path']}",
                f"  - prompt: {item.get('prompt_path')}",
                f"  - bytes: {item.get('bytes')}",
                f"  - dimensions: {item.get('width')}x{item.get('height')}",
                f"  - sha256: {item.get('sha256')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Notes",
            "- Generated through GUIVM /v1/llm-gate/infer, not a local/offline fallback.",
            "- Raw response metadata under raw/ omits image base64; PNG files are the canonical image artifacts.",
            "- Success criterion was output.images >= 1 for every candidate.",
            "",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.environ.get("GUIVM_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--wait-timeout-sec", type=int, default=1800)
    parser.add_argument("--infer-timeout-sec", type=int, default=600)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    out_dir = args.out_dir
    raw_dir = out_dir / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    status, health = http_json("GET", f"{args.base_url}/v1/health", timeout=30)
    (raw_dir / "health.json").write_text(json.dumps({"http_status": status, "json": health}, ensure_ascii=False, indent=2), encoding="utf-8")
    if status != 200 or not health.get("ok"):
        raise RuntimeError(f"GUIVM health check failed: HTTP {status} {health}")
    print(f"[health] ok base={args.base_url}", flush=True)

    images: list[dict[str, Any]] = []
    for candidate in CANDIDATES:
        if not candidate.source_file.exists():
            raise FileNotFoundError(candidate.source_file)
        info = generate_one(
            args.base_url,
            candidate,
            out_dir,
            raw_dir,
            args.wait_timeout_sec,
            args.infer_timeout_sec,
            args.retries,
            args.force,
        )
        images.append(info)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "source_dir": str(SOURCE_DIR),
        "success_criterion": "HTTP 200 with output.images length >= 1 for each candidate",
        "images": images,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 - CLI should emit concise failure.
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1)
