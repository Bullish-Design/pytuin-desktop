# Pytuin-Desktop v3 — Developer Guide

This guide explains the internal architecture and conventions so you can extend or modify the library with confidence.

## Architecture Overview

```
pytuin_desktop/
├── __init__.py          # Public API exports and version
├── models.py            # Pydantic models for AtrbDocument and block structures
├── enums.py             # Enums for tokens (e.g., TextAlignment, ColorToken)
├── parser.py            # YAML (safe) parsing: file/stream -> AtrbDocument
├── validator.py         # Schema validation of AtrbDocument
├── builders.py          # BlockBuilder and related helpers
├── discovery.py         # Template discovery & caching
├── editor.py            # DocumentEditor with streaming I/O and logging
├── repository.py        # DocumentRepository protocol + in-memory impl
├── logger.py            # get_logger() and logging utilities
├── errors.py            # Exception hierarchy
└── content.py           # Template loader glue
```

### Data Model (`models.py`)

- `AtrbDocument` is the canonical representation of an `.atrb` file.
- Blocks inherit from `BaseBlock` with common fields (`id`, `type`, `props`, `content`, `children`).
- Models are strict; unknown fields should be rejected or normalized in the parser/validator layer, not silently accepted in models.

### Parser (`parser.py`)

- `AtrbParser.parse_file(path)` and `AtrbParser.parse_stream(stream)` convert YAML into `AtrbDocument`.
- Uses a safe loader; do not enable arbitrary object construction.
- Responsibility: shape translation + helpful parse errors (`AtrbParseError`).

### Validator (`validator.py`)

- `AtrbValidator.validate(doc)` applies structural and semantic checks, raising `AtrbValidationError` or `AtrbSchemaError` on violations.
- Validation is called internally by the editor before writes to ensure on-disk fidelity.

### Templates & Builders (`discovery.py`, `content.py`, `builders.py`)

- Templates: deterministic block emission via `templateer.TemplateModel` subclasses.
- `load_atrb_templates(...)` and `clear_template_cache()` manage discovery and caching.
- `BlockBuilder` is a thin, testable facade for turning templates into block dicts that fit the schema exactly.

### Editor (`editor.py`)

- `DocumentEditor.create(...)` builds a new document in memory.
- `DocumentEditor.from_file(...)` constructs from an existing `.atrb`.
- `DocumentEditor.from_file_with_blocks(...)` hydrates an editor with parsed blocks to support append/edit workflows.
- `add_block(template_model)` appends a rendered, schema-conformant block.
- `write_to_stream(stream, ensure_trailing_newline=True)` renders the full YAML and validates before emitting.
- `save(path, ensure_trailing_newline=True)` wraps `write_to_stream` and guarantees a single trailing newline for deterministic diffs.
- Logging emits structured breadcrumbs for observability.

#### Repository seam (`repository.py`)

- `DocumentRepository` is a `typing.Protocol` with `get`, `save`, `list` methods.
- `InMemoryDocumentRepository` is a simple implementation for tests and examples.
- `DocumentEditor` accepts `repository=`. On successful write, it saves the validated `AtrbDocument` into the repository and logs `editor.repo_saved`.
- The seam enables future SQLModel-backed stores without coupling the core editor to persistence concerns.

### Errors (`errors.py`)

- `AtrbError` base class.
- Specifics include `AtrbParseError`, `AtrbSchemaError`, `AtrbValidationError`, `TemplateDiscoveryError`.
- Editor and parser surface precise failure reasons; avoid hiding exceptions—wrap them into the domain-specific types.

### Logging (`logger.py`)

- `get_logger()` returns a configured logger.
- Prefer structured `extra` payloads for actionable telemetry in tests and integrations.

## Public API (`__init__.py`)

- Exported symbols form the stable surface area. Adding new public names requires tests.
- `__version__` is maintained for downstream pinning and diagnostics.

## Testing Strategy

- Tests live under `src/tests/`.
- Use inline minimal templates in tests to avoid relying on external template folders.
- Key suites:
  - **Block type & builder tests:** ensure every emitted block is schema-valid and deterministic.
  - **Parser & validator tests:** parse failures are descriptive; valid docs round-trip.
  - **Editor tests:** streaming I/O, trailing newline guarantees, append flows.
  - **Repository tests:** save→list→get cycle; editor integration with repositories.
  - **Public API tests:** smoke test for top-level exports and version string.
  - **Integration flows:** end-to-end scenarios mirroring CLI-like workflows.

### Writing New Tests

- Favor `tmp_path` for filesystem interactions.
- Use `StringIO` for stream tests.
- Always assert ordering of blocks when round-tripping; `.atrb` content is ordered.

## Extending the Library

### New block types

1. Define a `TemplateModel` (inline for tests, or in template files for real usage).
2. Emit a block dict with the required shape: `type`, `props`, `content`, `children`.
3. Add builder helpers if the block is broadly used.
4. Validate with `AtrbValidator` and write tests covering construction and round-tripping.

### New repositories

1. Implement the `DocumentRepository` protocol (`get`, `save`, `list`).
2. Ensure idempotent `save` semantics by `doc.id`.
3. Add tests that use `DocumentEditor(..., repository=impl)` and verify `editor.repo_saved` behavior.

## Conventions

- Keep YAML emission deterministic:
  - Stable key order.
  - Single trailing newline on write.
- Do not rely on process CWD in tests.
- Use explicit imports that match established style in the repo.

## Release Notes (v3 focus)

- Added repository seam and in-memory repo.
- Editor persists to repository on successful write.
- Public API updated to re-export repository symbols.
- Integration tests added for core flows.
- Version updated to `0.3.0-dev9`.
