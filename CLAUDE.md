# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## What this is

`brain-storm` is a source repo for different development ideas/experiments. Each idea lives
as its own module, developed independently by default — but modules are allowed to depend on
or interoperate with each other when the idea actually calls for it. Isolation is the
default, not a hard rule: don't force artificial independence between modules that are
genuinely related, and don't casually couple modules that aren't.

## Current state

The repository is a bare scaffold: only a `README.md` exists, no source code, build
tooling, or tests have been added yet. There is no established language, framework, or
directory layout to follow.

## Working here

- Give each idea/experiment its own clearly named top-level directory. Default to keeping
  its dependencies and configuration scoped to that directory.
- If a new idea naturally builds on or shares functionality with an existing module, it's
  fine to depend on it directly — don't duplicate code across modules just to preserve
  isolation. Prefer an explicit, minimal interface (a small shared package/directory, a
  well-defined import) over deep, implicit coupling.
- Before adding a cross-module dependency, check whether the relationship is inherent to the
  idea or just convenient — if it's not inherent, keep the modules separate instead.
- Once modules exist, update this file with: the language/tooling actually in use per module,
  how to run/test each one, which modules depend on which, and any shared/common code
  location that emerges.
