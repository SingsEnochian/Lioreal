# NOW

## Current task

Validate and extend Lioreal Workshop Agent v0.1 as a small, inspectable operator for the Ark.

## Active branch

`ark/manifest-v1`

## Mode

Workshop Mode. Changes remain reviewable. No merge, deployment, production mutation, secret handling, or destructive operation without Steward approval.

## Current build sequence

- [x] Establish Ark continuity documents
- [x] Add DeepSeek prefix-completion adapter design
- [x] Create visible workshop state
- [x] Create the agent charter and operating loop
- [x] Create the Workshop Journal and first entry
- [x] Add Supabase schema for journal, decisions, fossils, questions, runs, continuity, and provenance
- [x] Add a runnable local agent scaffold
- [ ] Run the scaffold in a checked-out working tree and commit its dry-run evidence
- [ ] Add provider adapters and task planning behind explicit permissions
- [ ] Add database migration validation and rollback documentation

## Evidence rule

Claims of work must point to a branch, commit, test result, migration, journal entry, or explicit blocker.

## Current blocker

The GitHub connector can write and inspect repository files but cannot execute the new Python scaffold inside the repository checkout. The scaffold includes its own `py_compile` and artifact checks; a local or CI run is required to produce the first run record.

## Evidence created

- Agent charter: `agent/CHARTER.md`
- Local scaffold: `agent/lioreal_agent.py`
- Journal origin: `workshop/journal/0000-the-workshop-exists.md`
- Supabase migration: `supabase/migrations/202607200001_lioreal_workshop_agent.sql`

## Next action

Run:

```bash
python agent/lioreal_agent.py
```

Then inspect and commit the generated `workshop/runs/*.json` evidence before adding provider or repository-write capabilities.
