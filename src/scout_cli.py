"""CLI for Scout: screen a JSON list of candidate businesses.

Usage:
    python src/scout_cli.py data/prospects_sample.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scout import Candidate, screen  # noqa: E402


def load_candidates(path: str) -> list[Candidate]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Candidate(**row) for row in data]


def main():
    if len(sys.argv) < 2:
        print("usage: python src/scout_cli.py <candidates.json>")
        raise SystemExit(2)

    candidates = load_candidates(sys.argv[1])
    result = screen(candidates)

    print(f"Scout screened {len(candidates)} candidates\n")

    print(f"QUALIFIED ({len(result.qualified)}):")
    for q in result.qualified:
        c = q.candidate
        print(f"  [ok]   {c.name}  ({c.city}, {c.niche})  ->  {q.channel}")
        print(f"         leak: {q.leak}")

    print(f"\nREJECTED ({len(result.rejected)}):")
    for r in result.rejected:
        c = r.candidate
        print(f"  [skip] {c.name}  ({c.city})  - {r.reason}")


if __name__ == "__main__":
    main()
