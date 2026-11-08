# TampifyAI Agent Team

A team of hand-built AI agents that run TampifyAI's operations. Hand-built in Python (not drag-and-drop tools) because the goal is both a working business and real engineering depth.

## The spine

Every agent reads business rules and knowledge from the [Second Brain](https://github.com/cjjc3200-boop/tampify-second-brain), and uses the [Librarian](https://github.com/cjjc3200-boop/tampify-librarian) for retrieval. No agent hard-codes business facts that belong in the brain — change a rule in `targeting.md` and every agent picks it up.

```
tampify-second-brain   (the knowledge)
        |
  tampify-librarian     (retrieval over the knowledge)
        |
  tampify-agents        (the team that does the work)
```

## The team

| Agent | Job | Sells as |
|---|---|---|
| **Scout** | Find + screen prospects against the targeting rules | (internal — faster outreach) |
| **Scribe** | Draft the copy-ready outreach batch HTML | Email Marketing |
| **Qualifier** | Handle + qualify inbound replies | AI Lead Qualifier Agent |
| **Nudger** | Run the Day 3 / 6 / 10 follow-up sequence | AI Follow-Up Tool |
| **Analyst** | Report which niches and leaks convert | Reputation / Reporting |

**Status:** Scout is built and tested. The other four are planned.

## Scout

Scout screens candidate businesses against the targeting rules in the brain and returns qualified prospects (with the correct "primary leak" attached) plus rejected ones, each with the specific rule that disqualified it.

Scout does **not** invent businesses — finding candidates is a separate search step. Scout's job is honest screening, and every rule it applies is read from the brain, not hard-coded.

### Rules it applies (all from `targeting.md`)

- Florida only
- Not on the blacklist
- Not previously contacted
- Does not already offer AI services
- Has a working email or contact form (no phone outreach)
- Has a known niche with a mapped primary leak

### Run it

```bash
export BRAIN_REPO_PATH=../tampify-second-brain
python src/scout_cli.py data/prospects_sample.json
python tests/test_scout.py
```

### Test results

```
10/10 tests passed
```

Sample run over 10 candidates: 4 qualified, 6 rejected — one rejection per rule (out-of-state, blacklisted, has-AI, previously-contacted, no-channel, unknown-niche).

## Layout

```
src/
  brain.py        # shared: read rules/knowledge from the Second Brain
  scout.py        # Scout: screening logic
  scout_cli.py    # Scout: command-line runner
tests/
  test_scout.py   # Scout: screening-rule tests
data/
  prospects_sample.json
```

## Stack

Python (stdlib). No API key required for Scout — it applies deterministic rules, which is the honest way to screen.
