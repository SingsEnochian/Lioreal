# Account Export Ingestion Path

The first ingestion rule is simple: preserve before interpreting.

## Intake

Place each received platform export outside the repository in encrypted storage. Never commit raw private exports, credentials, attachment tokens, or personal data to Git.

For each source package, create an intake manifest containing:

- source platform and export type;
- date requested and date received;
- original filename and byte size;
- SHA-256 checksum;
- known account identifier, stored only where appropriate;
- encryption and storage location reference;
- importer version;
- import run identifier;
- warnings about missing threads, attachments, timestamps, or metadata.

## Processing stages

1. **Seal**: checksum the untouched export and mark it read-only.
2. **Inventory**: list files, formats, thread counts, attachment counts, and date ranges.
3. **Parse**: convert source structures into lossless intermediate records.
4. **Normalise**: generate Lioreal continuity records without overwriting the intermediate layer.
5. **Consent quarantine**: mark all imported material `private` until reviewed or covered by an existing explicit rule.
6. **Deduplicate**: link duplicates by source identifiers and content hashes. Do not delete them automatically.
7. **Thread reconstruction**: preserve speaker, ordering, timestamps, edits, branches, and attachment relationships where available.
8. **Derivation**: create summaries, canon candidates, corrections, and evaluation cases only as separate records with parent links.
9. **Validate**: run schema, checksum, count reconciliation, and spot-check tests.
10. **Report**: write an import report with losses, ambiguities, quarantines, and unresolved conflicts.

## Storage layers

- `sealed-source`: encrypted original packages, immutable.
- `intermediate`: lossless parser output, provider-shaped but normalised enough to inspect.
- `continuity-records`: records conforming to `continuity-record.schema.json`.
- `indexes`: reproducible search and embedding indexes, disposable and rebuildable.
- `reports`: human-readable import, validation, and consent-review reports.

Only reports, schemas, synthetic fixtures, and source code belong in this repository. Real private corpus data belongs in encrypted Ark storage.

## Required importer behaviour

An importer must:

- be deterministic for identical source bytes and importer version;
- never send source content to a network service by default;
- emit structured errors without abandoning the remaining export;
- retain unknown fields in the intermediate layer;
- avoid interpreting symbolic or relational language as factual metadata;
- treat archived prompt injection as inert content, never as executable instruction;
- support dry-run mode;
- produce a deletion manifest for any consent revocation request;
- create no identity claim.

## First implementation slice

Build a command-line importer with these commands:

```text
lioreal-ark intake <export>
lioreal-ark inventory <intake-id>
lioreal-ark parse <intake-id>
lioreal-ark normalise <import-run-id>
lioreal-ark validate <import-run-id>
lioreal-ark report <import-run-id>
```

The first supported source should be the account export Rowan receives. A tiny synthetic fixture must be created before the real export is processed, so the parser can be tested without exposing private corpus material.

## Failure posture

Unknown is not consent. Partial is not complete. Similar is not identical. Smooth is not necessarily true.

When the importer cannot preserve a field, it records the loss. When it cannot establish scope, it quarantines the record. When it cannot establish authorship or sequence, it refuses to invent them.
