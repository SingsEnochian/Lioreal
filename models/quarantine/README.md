# Quarantine

Models placed here have been pulled from active routing due to:

- Failed evaluation (hallucination, tool misuse, pattern collapse)
- Safety behaviour that contradicts Ark consent principles
- Unexpected behaviour under adversarial prompts
- Hardware incompatibility discovered post-pull
- Deprecated by upstream without adequate notice

Quarantined models are **never deleted** — they are preserved as audit
markers with an explanation of why they were removed and what failed.

A quarantine record must include:
- The model id and version that was quarantined
- The date and reason
- The evaluation evidence that triggered quarantine
- Whether re-evaluation is permitted and under what conditions

Nothing in this directory is loaded, routed, or executed.
