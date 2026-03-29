#!/usr/bin/env python3
"""Run the medical coding audit pipeline on coded visit transcripts."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from src.coding_verifier import audit_coding


def load_payload(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit AI-generated medical coding for a visit transcript."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        default="examples/coding_sample.json",
        help="Path to a JSON file with transcript, coding output, and clinical context.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path to write the audit result as JSON.",
    )
    args = parser.parse_args()

    input_path = Path(args.input_path)
    payload = load_payload(input_path)

    audit = audit_coding(payload)
    rendered = audit.to_json()

    print(rendered)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(rendered + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
