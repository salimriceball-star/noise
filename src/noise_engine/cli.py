from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .guivm import GUIVMClient
from .local_client import DeterministicNoiseClient
from .pipeline import NoisePipeline


DEFAULT_BASE_URL = "http://10.0.2.2:8765"



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interpretation-collision design engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check guivm connectivity")
    doctor.add_argument("--base-url", default=DEFAULT_BASE_URL)

    smoke = subparsers.add_parser("smoke", help="Run a minimal live guivm JSON smoke test")
    smoke.add_argument("--base-url", default=DEFAULT_BASE_URL)
    smoke.add_argument("--symbol", default="noise-smoke")

    run = subparsers.add_parser("run", help="Run bundle generation")
    run.add_argument("--brief", required=True)
    run.add_argument("--comments", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--base-url", default=DEFAULT_BASE_URL)
    run.add_argument("--symbol", default="noise")
    run.add_argument("--offline", action="store_true")

    demo = subparsers.add_parser("demo", help="Run the bundled humanoid-household demo")
    demo.add_argument("--output-dir", required=True)
    demo.add_argument("--base-url", default=DEFAULT_BASE_URL)
    demo.add_argument("--symbol", default="noise-demo")
    demo.add_argument("--offline", action="store_true")

    return parser



def _resolve_client(base_url: str, client: Any | None, *, offline: bool = False) -> Any:
    if client is not None:
        return client
    if offline:
        return DeterministicNoiseClient()
    return GUIVMClient(base_url=base_url)



def main(argv: list[str] | None = None, *, client: Any | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        resolved = _resolve_client(args.base_url, client)
        payload = {"health": resolved.check_health(), "capacity": resolved.check_capacity()}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "smoke":
        resolved = _resolve_client(args.base_url, client)
        payload = resolved.infer_json(
            stage="noise-smoke",
            symbol=args.symbol,
            request_id="noise-smoke-cli",
            prompt='Return strict JSON only. {"ok": true, "summary": "noise smoke"}',
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "run":
        resolved = _resolve_client(args.base_url, client, offline=args.offline)
        pipeline = NoisePipeline(client=resolved)
        result = pipeline.run(
            brief_path=args.brief,
            comments_path=args.comments,
            output_dir=args.output_dir,
            symbol=args.symbol,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "demo":
        resolved = _resolve_client(args.base_url, client, offline=args.offline)
        pipeline = NoisePipeline(client=resolved)
        project_root = Path(__file__).resolve().parents[2]
        example_dir = project_root / "examples" / "humanoid-household"
        result = pipeline.run(
            brief_path=example_dir / "brief.md",
            comments_path=example_dir / "comments.jsonl",
            output_dir=args.output_dir,
            symbol=args.symbol,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
