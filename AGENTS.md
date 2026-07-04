# TraceDoc — Agent Rules

> This file is the short rulebook for every implementation task.
> Read it before editing code. The full design is in `README.md`.

## 1. What this project is

TraceDoc is a **local-first, high-reliability document parsing and retrieval system**.

Its central product is not an AI-written answer. Its product is a **traceable piece of textual evidence** that can be checked against the original document.

A successful search result must be able to tell the user:

- which original file it came from;
- which PDF page it came from;
- which page-local text block it came from;
- which parser created the text;
- whether the result was automatically accepted or needs review.

## 2. Non-negotiable data rules

These rules must not be broken by convenience refactors or “cleaning” steps.

1. Keep original source files unchanged.
2. Keep raw native-PDF extraction and raw OCR output unchanged.
3. Never overwrite raw text with normalized, corrected, or manually edited text.
4. A `PageBlock` belongs to exactly one PDF page and never crosses pages.
5. Every searchable text unit must retain provenance back to file, PDF page, parser run, and PageBlock.
6. Parser disagreement is a **risk signal**, not proof that either parser is correct.
7. When a page is uncertain, route it to review instead of silently accepting it.
8. Native-text PDF pages must not be OCRed by default.

## 3. Current MVP boundary

The first MVP supports:

- Windows-native Python execution;
- native-text PDFs and scanned/image PDFs through separate paths;
- mostly single-column body text plus footnotes;
- local batch processing;
- SQLite and SQLite FTS5 for early retrieval;
- keyword, phrase, and later fuzzy search with source locations.

## 4. Explicitly out of scope for the current MVP

Do **not** introduce these unless a later task explicitly asks for them:

- Docker, WSL, Linux-only services, or containers;
- Oracle, PostgreSQL, Redis, Qdrant, or another server database;
- a local LLM runtime, remote LLM API, or agent framework;
- vector retrieval / embeddings;
- complex multi-column layout support;
- full table reconstruction;
- full formula-to-LaTeX reconstruction;
- a polished GUI before the storage and retrieval chain works;
- destructive deletion of footnotes, headers, footers, page numbers, or raw OCR text.

## 5. Dependency policy

This project starts small on purpose.

- Prefer the Python standard library when it is enough.
- Add a dependency only when a concrete accepted task needs it.
- Explain every new dependency in the pull request description.
- Do not install heavy OCR/PDF libraries during the bootstrap task.
- Do not add a dependency merely because it might be useful in a future phase.

## 6. Engineering rules

- Read the task file before coding.
- Change only files needed for the current task.
- Do not implement future phases early.
- Add focused tests for new behavior.
- Keep commands usable on Windows.
- Keep comments and user-facing documentation understandable for a beginner.
- Stop when the stated acceptance criteria are satisfied.
- In the final report, clearly list: changed files, commands run, tests run, dependencies added, and intentionally deferred work.

## 7. Reading order for Codex

For every task:

1. Read this `AGENTS.md`.
2. Read the named task document under `docs/00_project_control/`.
3. Read only the referenced parts of `README.md`.
4. Inspect the current repository tree.
5. Implement no more than the task allows.

If the task conflicts with this file, stop and report the conflict rather than guessing.