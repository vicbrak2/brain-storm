# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## What this is

`brain-storm` is a development environment for working with Claude, intended to be
structured as a **modular architecture that isolates and develops multiple ideas
independently** (each idea/experiment as its own self-contained module, rather than one
shared, entangled codebase).

## Current state

The repository is a bare scaffold: only a `README.md` exists, no source code, build
tooling, or tests have been added yet. There is no established language, framework, or
directory layout to follow.

## Working here

- Since there is no existing structure to match, when adding the first real work here,
  favor creating a clearly named top-level directory per idea/experiment (matching the
  "isolate multiple ideas independently" goal from the README) rather than mixing unrelated
  experiments into shared files.
- Keep each idea's dependencies and configuration scoped to its own directory so ideas stay
  independent and one experiment's setup doesn't leak into another's.
- Once the first module/idea is added, update this file with: the language/tooling actually
  in use, how to run/test each module, and any cross-module conventions that emerge (naming,
  directory shape, shared utilities if any).
