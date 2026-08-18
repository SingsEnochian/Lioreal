# NOW

## Current task

Validate Lioreal Workshop Agent v0.2 as a small, inspectable operator and resident caretaker for the Ark.

## Active branch

`ark/manifest-v1`

## Mode

Workshop Mode. Changes remain reviewable. No merge, deployment, production mutation, canonical rewrite, secret persistence, or destructive operation without Steward approval.

## Current build sequence

- [x] Establish Ark continuity documents
- [x] Add DeepSeek prefix-completion adapter design
- [x] Create visible workshop state
- [x] Create the agent charter and operating loop
- [x] Create the Workshop Journal and first entry
- [x] Add Supabase schema for journal, decisions, fossils, questions, runs, continuity, and provenance
- [x] Add a runnable local agent scaffold
- [x] Define bounded self-healing rules
- [x] Add a caretaker command for derived-state repair and quarantine
- [x] Add guarded Git update checking, fast-forward application, validation, and rollback
- [x] Add SMTP/Gmail-compatible operational email reporting
- [ ] Run the scaffold and caretaker in a checked-out working tree and commit dry-run evidence
- [ ] Add provider adapters and task planning behind explicit permissions
- [ ] Add database migration validation and rollback documentation
- [ ] Add scheduler/service installation for periodic health and update checks

## Evidence rule

Claims of work must point to a branch, commit, test result, migration, journal entry, health record, repair record, update record, notification record, or explicit blocker.

## Current blocker

The GitHub connector can write and inspect repository files but cannot execute the Python programs inside a repository checkout. A local or CI run is required to produce runtime evidence and to configure the email transport through environment variables or an operating-system secret store.

## Evidence created

- Agent charter: `agent/CHARTER.md`
- Local scaffold: `agent/lioreal_agent.py`
- Caretaker: `agent/caretaker.py`
- Journal origin: `workshop/journal/0000-the-workshop-exists.md`
- Supabase migration: `supabase/migrations/202607200001_lioreal_workshop_agent.sql`

## Workbench

**Current thought:** Self-healing must preserve identity and evidence. The Agent may repair what can be reproduced, quarantine what is malformed, and roll back its own failed update. It may not heal by quietly rewriting canonical memory.

**Working on:** Producing runtime evidence for health checks, bounded repair, guarded update comparison, rollback behaviour, and operational email delivery.

**Next hammer swing:** Run compile and dry-run checks locally, then configure an approved email recipient and secret-backed SMTP credentials.

**Expected artifacts:** `workshop/runs/run-*.json` and `workshop/runs/caretaker-*.json`

**Raccoon status:** Now carries a screwdriver, rollback rope, and postage stamps. Production cupboard remains locked.

## Local validation commands

```bash
python agent/lioreal_agent.py
python agent/caretaker.py heal --email never
python agent/caretaker.py update --remote origin --branch ark/manifest-v1 --email never
```

The update command above checks only. Applying a clean fast-forward candidate is explicit:

```bash
python agent/caretaker.py update --remote origin --branch ark/manifest-v1 --apply --email always
```

## Email configuration

The caretaker reads email settings from the process environment and never writes credentials to the repository:

```text
LIOREAL_SMTP_HOST=smtp.gmail.com
LIOREAL_SMTP_PORT=465
LIOREAL_SMTP_USER=<sender account>
LIOREAL_SMTP_PASSWORD=<secret or Gmail app password>
LIOREAL_EMAIL_FROM=<sender address>
LIOREAL_EMAIL_TO=<approved Steward recipient>
```

For the production form, move these values into the operating-system secret store and inject them only at runtime.

<!-- AGENT:LAST_RUN -->
## Last agent run

- Key: `run-20260720T044742Z-f4a75b4c`
- Status: **completed**
- At: `2026-07-20T04:47:42.596424+00:00`
- Branch: `ark/manifest-v1`
- Commit: `cca9358d120dbe02725ce69d910a5d887df09ba0`
- Checks: 5/5 passed

_Updated automatically by `agent/lioreal_agent.py`. Do not edit this section manually._
<!-- /AGENT:LAST_RUN -->
