"""Shared helpers for the TampifyAI agent team.

The team is built on one spine: the Second Brain. Agents read business rules
and knowledge from the brain's raw/ markdown rather than hard-coding them, so
when a rule changes in the brain, every agent picks it up.
"""

import os
import re
from pathlib import Path

# Locate the Second Brain checkout (sibling repo by default).
ROOT = Path(__file__).resolve().parents[2]
BRAIN_ROOT = Path(os.getenv("BRAIN_REPO_PATH", str(ROOT.parent / "tampify-second-brain")))
RAW_DIR = BRAIN_ROOT / "raw"


def read_brain(filename: str) -> str:
    """Read a markdown file from the brain's raw/ folder."""
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Brain file not found: {path}. Set BRAIN_REPO_PATH to the tampify-second-brain checkout."
        )
    return path.read_text(encoding="utf-8")


def parse_blacklist() -> list[str]:
    """Extract blacklisted business names from targeting.md."""
    text = read_brain("targeting.md")
    names = []
    in_blacklist = False
    for line in text.splitlines():
        if line.strip().lower().startswith("## blacklist"):
            in_blacklist = True
            continue
        if in_blacklist:
            if line.startswith("##"):
                break
            m = re.match(r"\s*-\s*([^—\-]+?)\s*(?:—|-)", line)
            if m:
                names.append(m.group(1).strip())
    return names


def parse_leak_table() -> dict[str, str]:
    """Parse the Primary Leak by Niche table from targeting.md."""
    text = read_brain("targeting.md")
    leaks: dict[str, str] = {}
    in_table = False
    for line in text.splitlines():
        if line.strip().startswith("| Niche"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 2 and cells[0] and not set(cells[0]) <= {"-"}:
                leaks[cells[0].lower()] = cells[1]
    return leaks
