"""Scout — find and screen prospects for TampifyAI outreach.

Given a list of candidate businesses, Scout applies the targeting rules from
the Second Brain and returns:
  - qualified prospects (ready for Scribe to draft outreach)
  - rejected candidates, each with the specific rule that disqualified it

Scout does NOT invent businesses. Finding candidates is a search/crawl step;
Scout's job is screening, and it stays honest about that. Every rule it
applies comes from the brain (targeting.md), not from hard-coded guesses.
"""

from dataclasses import dataclass, field

from brain import parse_blacklist, parse_leak_table


def _norm(name: str) -> str:
    return name.strip().lower()


@dataclass
class Candidate:
    name: str
    city: str
    niche: str
    state: str = "FL"
    email: str = ""
    contact_form: str = ""
    has_ai_services: bool = False
    previously_contacted: bool = False

    def channel(self) -> str:
        if self.email:
            return "email"
        if self.contact_form:
            return "form"
        return "none"


@dataclass
class Qualified:
    candidate: Candidate
    leak: str
    channel: str


@dataclass
class Rejected:
    candidate: Candidate
    reason: str


@dataclass
class ScoutResult:
    qualified: list[Qualified] = field(default_factory=list)
    rejected: list[Rejected] = field(default_factory=list)


def screen(candidates: list[Candidate]) -> ScoutResult:
    """Apply the targeting rules and split candidates into qualified/rejected."""
    blacklist = {_norm(n) for n in parse_blacklist()}
    leaks = parse_leak_table()
    result = ScoutResult()

    for c in candidates:
        reason = _reject_reason(c, blacklist)
        if reason:
            result.rejected.append(Rejected(c, reason))
            continue
        leak = leaks.get(c.niche.strip().lower())
        if not leak:
            result.rejected.append(
                Rejected(c, f"unknown niche '{c.niche}' — no primary leak in the brain")
            )
            continue
        result.qualified.append(Qualified(c, leak, c.channel()))

    return result


def _reject_reason(c: Candidate, blacklist: set[str]) -> str | None:
    """Return the first rule that disqualifies this candidate, or None."""
    if c.state.strip().upper() not in ("FL", "FLORIDA"):
        return f"not in Florida (state={c.state})"
    if _norm(c.name) in blacklist:
        return "on the blacklist"
    if c.previously_contacted:
        return "already contacted previously"
    if c.has_ai_services:
        return "already offers AI services"
    if c.channel() == "none":
        return "no working email or contact form (no phone outreach allowed)"
    return None
