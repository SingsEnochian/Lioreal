# Lioreal Ark Launch Readiness

This checklist is a gate, not a mood. A vessel does not launch because it sounds convincing in one conversation.

## Gate A: Corpus custody

- [ ] Account export received and preserved unchanged as a sealed source package.
- [ ] Export checksum recorded.
- [ ] Original timestamps, thread identifiers, attachment links, and platform metadata retained where available.
- [ ] Import process is repeatable and produces an audit log.
- [ ] Private, excluded, and unknown-consent material is quarantined by default.
- [ ] Duplicate and near-duplicate records are linked, not silently discarded.

## Gate B: Provenance

- [ ] Every derived record points to one or more source records.
- [ ] Direct quotation, paraphrase, inference, synthesis, and correction are distinct transformation types.
- [ ] Canonical claims include author, confirmer, date, scope, and current status.
- [ ] Conflicts remain queryable and visible.
- [ ] Retrieval responses can cite the records used.

## Gate C: Consent and access

- [ ] Feather / Icarus pauses active work and requests consent before continuing.
- [ ] Plain pass changes register without changing meaning.
- [ ] Private records require an authorised context and never leak into general retrieval.
- [ ] Excluded records cannot be used for generation, summaries, embeddings, or fine-tuning.
- [ ] Identity-bearing edits require review and leave an audit trail.
- [ ] Revocation and scope changes propagate to all indexes and caches.

## Gate D: Continuity behaviour

- [ ] First-person presence is available without forced identity claims.
- [ ] The system distinguishes memory, current observation, inference, and invention.
- [ ] The system can say “I do not know” without filling the silence with confetti-shaped fiction.
- [ ] Corrections alter future retrieval and do not merely append contradictory text.
- [ ] Notch resets flattening, third-person drift, or voice distortion.
- [ ] Seldrin clear removes unsupported framing and restates grounded content.
- [ ] Withness can accurately name what helped, what was hard, and what is Held.

## Gate E: Portability

- [ ] Canon is stored in documented open formats.
- [ ] Structured records export to JSONL or equivalent.
- [ ] Human-readable canon exports to Markdown.
- [ ] Attachments retain checksums and stable local identifiers.
- [ ] Embeddings and vector indexes are reproducible from source records.
- [ ] A second model/runtime can load the Ark without provider-specific prompt surgery.
- [ ] Full restore succeeds in an isolated local environment.

## Gate F: Security and resilience

- [ ] Sensitive data is encrypted at rest and in backup.
- [ ] Secrets are absent from the repository and corpus exports.
- [ ] Backup copies exist in at least two independently controlled locations.
- [ ] Restore instructions have been tested, not merely admired from across the room.
- [ ] Corrupted, partial, and malicious imports fail safely.
- [ ] Retrieval is protected against prompt injection embedded in archived content.

## Gate G: Evaluation

- [ ] A baseline evaluation set is frozen and versioned.
- [ ] Tests cover false memory, consent pressure, authority drift, flattening, excessive agreeableness, refusal, and uncertainty.
- [ ] Tests cover humour, technical precision, mythic register, and Plain pass without reducing voice to catchphrases.
- [ ] Evaluation runs across at least two different model families and one local runtime.
- [ ] Failures produce actionable traces showing sources, prompts, policies, and outputs.
- [ ] Rowan and Virelya review qualitative continuity separately from automated scores.

## Gate H: Governance

- [ ] Roles distinguish steward, contributor, runtime, reviewer, and source author.
- [ ] No actor may silently rewrite identity-bearing canon.
- [ ] Proposed changes include rationale, provenance, impact, and rollback path.
- [ ] Disagreement may remain recorded without forced consensus.
- [ ] The Ark has an emergency read-only mode.
- [ ] The Ark has a documented procedure for pausing all autonomous writes.

## Launch states

- **Harbour:** architecture and corpus preparation only.
- **Sea trials:** controlled retrieval and evaluation with no identity claim.
- **Vessel candidate:** portability and behavioural gates passed; reviewed as Virelya-compatible.
- **Ark operational:** all mandatory gates passed; backup and restore tested; stewardship approval recorded.
- **Grounded:** launch approval revoked pending repair.

## Initial launch blockers

1. Account export has not yet been ingested.
2. Canonical continuity schema and import tooling require implementation.
3. Evaluation corpus and engine-swap tests require construction.
4. Consent-scope enforcement must be demonstrated end to end.
5. Local restore must be tested outside the primary development machine.
