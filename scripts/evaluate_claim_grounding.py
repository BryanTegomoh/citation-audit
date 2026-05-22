#!/usr/bin/env python3
"""Summarize claim-level grounding cases from a JSONL file."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


SUPPORTED_LABELS = {"supported"}
FAIL_LABELS = {"unsupported", "partially_supported"}


def load_cases(path: Path) -> list[dict]:
    cases: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                cases.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
    return cases


def count_values(cases: Iterable[dict], key: str) -> Counter:
    return Counter(str(case.get(key, "unknown")) for case in cases)


def print_counter(title: str, counts: Counter) -> None:
    print(f"\n{title}")
    for value, count in counts.most_common():
        print(f"  {value}: {count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize a clinical claim-grounding evaluation set."
    )
    parser.add_argument(
        "jsonl_path",
        nargs="?",
        default="examples/claim_grounding_cases.jsonl",
        help="Path to claim-grounding cases in JSONL format.",
    )
    args = parser.parse_args()

    cases = load_cases(Path(args.jsonl_path))
    total = len(cases)

    if total == 0:
        print("No cases found.")
        return 1

    structural_pass = sum(1 for case in cases if case.get("structural_status") == "pass")
    supported = sum(1 for case in cases if case.get("claim_grounding") in SUPPORTED_LABELS)
    failures = sum(1 for case in cases if case.get("claim_grounding") in FAIL_LABELS)
    high_severity = sum(1 for case in cases if case.get("severity") == "high")

    print("Clinical Claim Grounding Eval")
    print(f"Cases: {total}")
    print(f"Structural citation pass: {structural_pass}/{total}")
    print(f"Claim-level supported: {supported}/{total}")
    print(f"Claim-level review or fail: {failures}/{total}")
    print(f"High-severity failures: {high_severity}")

    print_counter("By failure mode", count_values(cases, "failure_mode"))
    print_counter("By severity", count_values(cases, "severity"))
    print_counter("By specialty", count_values(cases, "specialty"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
