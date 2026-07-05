# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## What this is

`brain-storm` is a **business-idea incubator**, not a plain code repo. Each module is a
hypothesis about a market niche, refined until it's validated or discarded. The code inside
a module is the vehicle for testing the idea quickly (usually a prototype/MVP with Claude as
the backend); the business hypothesis is the actual deliverable. Discarding an idea with
documented learnings is also a valid, valuable outcome.

Each idea lives as its own module, developed independently by default — but modules are
allowed to depend on or interoperate with each other when the idea actually calls for it.
Isolation is the default, not a hard rule: don't force artificial independence between
modules that are genuinely related, and don't casually couple modules that aren't.

## The PITCH.md convention

Every module MUST have a `PITCH.md` at its root capturing the business hypothesis. This is
what makes the repo refine *ideas* and not just software. Sections:

- **Nicho** — the market niche in one line.
- **Problema** — what pain it solves, and how it's solved today.
- **Cliente** — who pays, and a rough sense of how much / how often.
- **Por qué ahora** — what Claude/LLMs made possible that used to be too expensive.
- **MVP** — the smallest thing that tests demand (usually what the module's code implements).
- **Monetización** — plausible pricing/packaging.
- **Señales de validación** — what evidence would move the idea forward or kill it.
- **Estado** — one of: `explorando` / `prototipado` / `validado` / `descartado`.
- **Aprendizajes** — running log of what was learned (especially if descartado).

When starting a new module, write the `PITCH.md` first — the code follows the hypothesis,
not the other way around. When an idea's status changes, update its `PITCH.md`.

## Current state

One module exists so far. There is no repo-wide build tooling or shared code yet; each
module is self-contained.

## Modules

### `fable-forge/` — generador de fábulas interactivas

- **Niche hypothesis:** personalized children's content (see `fable-forge/PITCH.md`).
  Status: `prototipado`.
- **What:** CLI that generates original fables (animal characters, conflict, explicit
  moral) from a moral/theme + audience + tone. Supports format variants (shorter, verse,
  narration script, per-scene illustration prompts) and series with recurring characters.
- **Stack:** Python 3.10+, `anthropic` SDK only. Backend is exclusively `claude-fable-5`
  via the Messages API — no RAG, no database, no other services. Persistence is flat files
  under `fable-forge/output/` (gitignored).
- **Run:** `cd fable-forge && pip install -r requirements.txt && python -m fable_forge new -m "<moraleja>" -a "<audiencia>" -t "<tono>"`.
  Requires Anthropic credentials in the environment. See `fable-forge/README.md`.
- **Depends on:** nothing else in this repo.
- **Key convention:** the system prompt (`fable_forge/prompts.py`) is the product — output
  quality lives there, not in the code. Treat prompt edits as the highest-risk change in
  the module and re-check generated output after touching them.

## Conventions established so far

- Module layout: top-level directory per idea, with its own `PITCH.md` (business
  hypothesis — see above), `README.md` (how to run it), `requirements.txt` (or
  equivalent), `.gitignore`, and source package inside. Generated artifacts go in a
  gitignored `output/` inside the module.
- Python modules are runnable as `python -m <package>` from the module directory; no
  repo-wide virtualenv or installer is assumed.
- Modules that call the Claude API read credentials from the environment
  (`ANTHROPIC_API_KEY` or an `ant auth login` profile) and never hardcode keys.

## Working here

- Give each idea/experiment its own clearly named top-level directory. Default to keeping
  its dependencies and configuration scoped to that directory.
- If a new idea naturally builds on or shares functionality with an existing module, it's
  fine to depend on it directly — don't duplicate code across modules just to preserve
  isolation. Prefer an explicit, minimal interface (a small shared package/directory, a
  well-defined import) over deep, implicit coupling.
- Before adding a cross-module dependency, check whether the relationship is inherent to the
  idea or just convenient — if it's not inherent, keep the modules separate instead.
- When adding or changing a module, update the **Modules** section above: language/tooling
  in use, how to run/test it, which modules it depends on, and any shared/common code
  location that emerges.
