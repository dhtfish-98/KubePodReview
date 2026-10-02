"""Local command-line entry point for KubePodReview."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import review


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Review selected securityContext declarations in a local Kubernetes workload JSON object.")
    parser.add_argument("input", type=Path, help="local authorized input")

    parser.add_argument("--json", action="store_true", help="emit JSON findings")
    args = parser.parse_args(argv)
    input_path = args.input
    try:
        if input_path.is_symlink() or not input_path.is_file():
            raise ValueError("input must be a regular non-symlink file")
        if input_path.stat().st_size > 4 * 1024 * 1024:
            raise ValueError("input exceeds 4 MiB")
        text = input_path.read_text(encoding="utf-8")
        findings = review.review_text(text)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(findings, indent=2, ensure_ascii=False))
    else:
        for item in findings:
            print(f"{item['rule']}: {item['location']}: {item['note']}")
        if not findings:
            print("No review prompts for the checks implemented")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
