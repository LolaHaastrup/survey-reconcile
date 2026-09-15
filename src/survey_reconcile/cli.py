from __future__ import annotations

import argparse
import json

from .pipeline import run_pipeline


def _repeat(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("repeat must use NAME=PATH")
    name, path = value.split("=", 1)
    if not name or not path:
        raise argparse.ArgumentTypeError("repeat must use NAME=PATH")
    return name, path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="survey-reconcile")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="reconcile survey exports")
    run.add_argument("--config", required=True)
    run.add_argument("--households", required=True)
    run.add_argument("--repeat", action="append", type=_repeat, default=[])
    run.add_argument("--output", required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "run":
        summary = run_pipeline(
            args.config, args.households, dict(args.repeat), args.output
        )
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

