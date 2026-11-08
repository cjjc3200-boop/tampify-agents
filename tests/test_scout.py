"""Tests for Scout's screening rules.

Plain stdlib asserts — run with `python tests/test_scout.py` (no pytest needed).
Each test maps to one targeting rule from the brain.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scout import Candidate, screen  # noqa: E402


def _names(items):
    return [i.candidate.name if hasattr(i, "candidate") else i.name for i in items]


def test_florida_only():
    res = screen([Candidate(name="OutOfState", city="Atlanta", niche="HVAC", state="GA", email="a@b.com")])
    assert len(res.qualified) == 0, "non-Florida business should be rejected"
    assert "not in Florida" in res.rejected[0].reason


def test_blacklist():
    res = screen([Candidate(name="Gro Yoga", city="Miami", niche="Gyms", state="FL", email="a@b.com")])
    assert len(res.qualified) == 0
    assert "blacklist" in res.rejected[0].reason


def test_already_has_ai():
    res = screen([Candidate(name="X", city="Miami", niche="Gyms", state="FL", email="a@b.com", has_ai_services=True)])
    assert len(res.qualified) == 0
    assert "already offers AI" in res.rejected[0].reason


def test_previously_contacted():
    res = screen([Candidate(name="Y", city="Miami", niche="Gyms", state="FL", email="a@b.com", previously_contacted=True)])
    assert len(res.qualified) == 0
    assert "already contacted" in res.rejected[0].reason


def test_needs_email_or_form():
    res = screen([Candidate(name="Z", city="Ocala", niche="Gyms", state="FL")])
    assert len(res.qualified) == 0
    assert "no working email or contact form" in res.rejected[0].reason


def test_unknown_niche_rejected():
    res = screen([Candidate(name="Mystery", city="Tampa", niche="Underwater Basket Weaving", state="FL", email="a@b.com")])
    assert len(res.qualified) == 0
    assert "unknown niche" in res.rejected[0].reason


def test_qualified_gets_correct_leak():
    res = screen([Candidate(name="Sunshine Roofing", city="Orlando", niche="Roofing", state="FL", contact_form="https://x.com/c")])
    assert len(res.qualified) == 1
    assert res.qualified[0].leak == "slow lead response"
    assert res.qualified[0].channel == "form"


def test_email_preferred_over_form():
    res = screen([Candidate(name="Both", city="Tampa", niche="Gyms", state="FL", email="a@b.com", contact_form="https://x.com/c")])
    assert res.qualified[0].channel == "email"


def test_all_leaks_present():
    """Every niche in the brain should have a leak Scout can attach."""
    from brain import parse_leak_table

    leaks = parse_leak_table()
    assert len(leaks) >= 15, f"expected the full leak table, got {len(leaks)}"
    assert leaks["gyms"] == "member drop-off"


def test_full_sample_screening():
    import json

    data = json.loads((Path(__file__).resolve().parents[1] / "data" / "prospects_sample.json").read_text())
    res = screen([Candidate(**row) for row in data])
    assert len(res.qualified) >= 3, f"expected several qualifiers, got {_names(res.qualified)}"
    assert len(res.rejected) >= 5, f"expected several rejects, got {_names(res.rejected)}"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    raise SystemExit(0 if passed == len(tests) else 1)
