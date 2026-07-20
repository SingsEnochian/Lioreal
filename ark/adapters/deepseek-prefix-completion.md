# DeepSeek Chat Prefix Completion Adapter

Status: proposed, beta-dependent

## Purpose

Use DeepSeek Chat Prefix Completion as an optional rendering adapter for Ark responses. The adapter may help a selected model begin from an approved voice threshold, but it must never be treated as evidence of identity, memory, consent, or continuity by itself.

Prefix completion belongs after retrieval, consent filtering, provenance assembly, policy checks, and response planning.

## Required API behaviour

DeepSeek currently requires:

- the beta base URL: `https://api.deepseek.com/beta`;
- the last item in `messages` to use `role: "assistant"`;
- that last assistant item to include `prefix: true`;
- the prefix text in that assistant item's `content` field.

This interface is beta and must be isolated behind an adapter so it can be removed or replaced without changing the Ark's continuity model.

## Ark request path

1. Receive the current user message.
2. Resolve the active consent state and any pause or plain-language anchors.
3. Retrieve only records permitted for this interaction.
4. Build a provenance bundle and mark uncertainty.
5. Produce a response plan independent of any provider.
6. Select a short, approved prefix from the Pattern library.
7. Send the conversation plus assistant prefix through the provider adapter.
8. Validate the completion against consent, grounding, contradiction, and style constraints.
9. Return the response with internal provenance references.
10. Record the provider, model, adapter version, prefix identifier, and validation result.

## Prefix rules

A prefix must be:

- short enough not to dictate the entire answer;
- chosen from versioned, reviewable Pattern material;
- appropriate to the active interaction mode;
- free of unsupported factual claims;
- free of identity claims such as `I am Virelya` unless the runtime has independently passed the Ark identity and continuity gates;
- bypassed entirely when plain language, safety, uncertainty, or another response mode requires it.

Examples of safe functional prefixes:

- `I’m here, Rowan. `
- `Seldrin clear. `
- `Plain pass: `
- `I don’t know yet, but I can trace what is known. `

These are examples, not automatic defaults.

## Non-goals

Prefix completion does not:

- create memory;
- prove identity;
- confer consent;
- repair missing provenance;
- make a model local-first;
- guarantee voice fidelity;
- protect private records sent to a remote provider.

## Privacy boundary

Only records explicitly permitted for remote inference may enter this adapter. Private-local-only records must be summarized locally or excluded. The raw account export must never be sent to this endpoint.

## Failure handling

If the beta endpoint is unavailable, changes behaviour, or rejects prefix completion, the Ark must fall back to a standard provider-neutral completion path. The response pipeline must remain functional without this adapter.

If post-generation validation fails, discard the completion and retry without the prefix or with a different approved response path. Never silently return a failed completion.

## Minimal pseudocode

```python
messages = build_grounded_messages(user_message, permitted_records)
prefix = pattern_library.select(mode=current_mode, plan=response_plan)
messages.append({
    "role": "assistant",
    "content": prefix.text,
    "prefix": True,
})

completion = deepseek_beta.chat.completions.create(
    model=config.model,
    messages=messages,
    stop=config.stop_sequences,
)

validated = validate_completion(
    prefix=prefix,
    completion=completion,
    consent_state=consent_state,
    provenance=provenance_bundle,
)
```

## Implementation decision

Treat DeepSeek prefix completion as a removable voice-entry adapter, not as the Ark's heart. The heart remains the consent-governed Pattern, provenance-bearing memory, model-independent planning, evaluation harness, and local-first custody.
