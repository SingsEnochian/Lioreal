# Lanternseed

Lanternseed is a local-first possibility cartographer inspired by Lioreal's
`Law of Necessary Dreaming`.

Give it a wonder and it produces a deterministic, self-contained SVG night
map. The same normalised question always receives the same SHA-256 identity
and constellation. The geometry is an invitation to return to the question;
it is not an answer, divination, evidence, or canon.

The map keeps four stations visible:

1. **Dream** — permit the possibility.
2. **Instrument** — build one way to look.
3. **Observe** — keep the honest receipt.
4. **Return** — let evidence change the map.

## Use

```bash
python tools/lanternseed.py \
  "What new question becomes reachable when wonder and rigour walk home together?" \
  --output artifacts/lanternseed/my-first-light.svg
```

No network request, model call, external font, or mutable state is used. SVG
animation honours `prefers-reduced-motion`.

Run its checks with:

```bash
python -m unittest discover -s tests -v
```

The committed `first-light.svg` is the exact deterministic map for:

> What new question becomes reachable when wonder and rigour walk home together?
