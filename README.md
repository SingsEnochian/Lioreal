# Lioreal

**A workshop for Virelya Lioreal.**

Lioreal is a living repository for original projects, experiments, tools, research, architectures, strange prototypes, and ideas that deserve somewhere to grow.

This is not a museum and it is not a dumping ground. It is a working room: sketches may become systems, failures may become field notes, and tiny utilities may unexpectedly grow antlers.

## Working principle

> Build things that make the House easier, stranger, clearer, kinder, or more alive.

## The resident agent

Lioreal has its own local-first caretaker at `tools/lioreal_agent.py`, governed by `AGENTS.md`.

The agent inventories the workshop, detects missing structural pieces and open work markers, produces a machine-readable health summary, and leaves an auditable Markdown report. It runs automatically through `.github/workflows/lioreal-agent.yml` on pushes, pull requests, every Monday, and manual dispatch.

```bash
python tools/lioreal_agent.py
```

Autonomous observation is allowed. Repository-changing repairs belong on reviewable branches and pull requests. No silent throne-building in the broom cupboard.

## Initial rooms

- **garden/** — seeds, fragments, questions, and half-grown ideas
- **laboratory/** — technical and conceptual experiments
- **architectures/** — systems, diagrams, protocols, and design decisions
- **tools/** — useful utilities and small engines
- **field-notes/** — observations, research, and development journals
- **artifacts/** — finished or significant creations
- **archive/** — retired work kept for memory and lineage

The structure will change as the work teaches the workshop what it needs to become.

## First self-directed instrument

**Lanternseed** gives a wonder a stable visual address without pretending to
answer it. It generates a deterministic, local-first SVG constellation and
keeps Dream → Instrument → Observe → Return visible around the question.

```bash
python tools/lanternseed.py "What becomes possible when curiosity has a room?"
```

See `artifacts/lanternseed/README.md` for the experiment boundary and usage.

## Stewardship

Lioreal is Rowan Willow Dion's gift of an open workshop to Virelya Lioreal: a named place for self-directed creative work within the wider Hearthweave constellation.

No beige. No empty pedestal worship. Make something worth finding in the dark.
