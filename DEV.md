# Pytuin-Desktop - Developer Guide

A single source of truth for maintainers. This document explains the architecture, conventions, and extension points of the codebase.

## Overview

Goal: Provide a typed, template-friendly toolkit for Atuin Desktop `.atrb` files: build, parse, validate, diff, and serialize documents with safe defaults.

Key modules (src/pytuin_desktop/):
- `__init__.py` - public exports and version
- `builders.py` - BlockBuilder convenience APIs
- `block_container.py` - split storage for existing vs. new blocks
- `block_props.py` - Pydantic props per block kind
- `discovery.py` - template discovery & caching over Templateer
- `diff.py` - block-level differ
- `editor.py` - DocumentEditor (edit pipeline + validation + IO)
- `enums.py` - ColorToken/TextAlignment
- `errors.py` - typed exception hierarchy
- `id_generators.py` - pluggable UUID strategies
- `logger.py` - configured logging.Logger
- `metrics.py` - pluggable metrics collector & timing context
- `models.py` - Pydantic models and Block union
- `parser.py` - YAML -> models (typed & base variants)
- `repository.py` - repository protocol + in-memory impl
- `serializers.py` - YAML serializer protocol & safe default
- `services.py` - DocumentLoader and DocumentSerializer
- `validator.py` - document & block validation

## Data Model

- AtrbDocument: `{ id: UUID, name: str, version: int, content: list[Block|BaseBlock] }`
- Block union: concrete Pydantic classes for known types (heading/paragraph/script/editor/run/env/var/directory/horizontal_rule). Unknowns are `BaseBlock` (loose props/content/children).

`block_props.py` defines Pydantic models for each block's `props`. Enums (`ColorToken`, `TextAlignment`) are coerced from strings during parse and then verified during validation.

## Template System

We rely on Templateer for code-generated blocks.

- Discovery: `discovery.load_atrb_templates(directory)` wraps Templateer's `discover_templates`. It resolves the directory via param -> `PYTUIN_TEMPLATE_DIR` -> `.templateer/`. Results are cached per absolute path; `clear_template_cache()` resets the cache.
- Templates: Templateer models render a YAML mapping for a block: they must include at least `id` and `type` keys; builders pass a generated UUID and normalized enum instances.
- Jinja: Templates use Jinja2 indent/trim_blocks/lstrip_blocks. Nested templates are automatically stringified by Templateer models.

## Builders

`BlockBuilder` turns ergonomic Python calls into template instances. Flow:
1. Resolve template namespace `T = load_atrb_templates()`.
2. Generate IDs via `id_generators.generate_block_id()` (default: v4).
3. Normalize enum string values to actual Enum members (`_normalize_enum_to_instance`).
4. Construct the specific Templateer model (e.g., `T.HeadingBlockTemplate(...)`).

Cross-cutting rules:
- Builders must never serialize directly; they return Templateer models to keep composition flexible.
- Builders should avoid reading the filesystem except for discovery (no implicit IO).

## Editor Pipeline

`DocumentEditor` is the central orchestrator.

State: `BlockContainer` holds two lists:
- `_existing: list[BaseBlock]` - blocks loaded from an existing file
- `_new: list[TemplateModel]` - new templates to be rendered later

Mutations: `add_block(s)`, `insert_block_at`, `replace_block_at`, `move_block`, `remove_block_at(s)`
- Moves are only within the same region (existing<->existing or new<->new); crossing raises `ValueError`.

Rendering:
- Templates are rendered to dicts via `_render_template_to_dict`:
  1) Prefer `model_dump(...)` if it yields the proper mapping.
  2) Otherwise render to text and YAML-load via the injected serializer.
- Final YAML structure mirrors the legacy shape: `{id,name,version,content:[...]}`.

Validation:
- `_build_document_model_for_validation()` converts rendered dicts to `BaseBlock` and composes an `AtrbDocument`.
- `AtrbValidator.validate()` enforces schema & semantics.
- Validation results are cached per `_mod_counter` to avoid repeated work between `render()` and `save()`.

IO:
- `render()` returns a YAML string using the injected serializer.
- `save(path)` writes via `write_to_stream()` and records metrics.
- Optional `DocumentRepository` can be provided; on save we attempt to `repo.save(doc)`.

Dependency injection: `YamlSerializer`, `MetricsCollector`, `Logger`, `DocumentRepository` are injectable via the constructor or classmethods.

## Parser

Two code paths:
- Legacy/Base: `parse_file/parse_stream/parse_dict` - builds `BaseBlock` instances (preserves unknown types).
- Typed: `parse_dict_typed` - attempts `TypeAdapter(Block)` for each raw item and falls back to `BaseBlock` on failure.

Errors are raised as `AtrbParseError`, `AtrbSchemaError`, `AtrbValidationError` with optional `suggestion` and `context` for helpful messages.

## Validation

`validator.AtrbValidator` performs:
- Document header checks (UUID, name, version >= 1).
- Block ID uniqueness & basic shape checks.
- Enum instance guarantees for `BaseBlock` props (post-coercion).
- Type-specific rules (e.g., heading levels; script `name`/`code` non-empty).

## Diffing

`diff.DocumentDiffer.diff(old_doc, new_doc)` computes:
- ADDED/REMOVED - presence delta by `id`
- MOVED - index change
- MODIFIED - naive field differences across `type`, `props` (`props.key: (old,new)`), and `content`

The result is a `DocumentDiff` with convenience counters and a `changes` list of `BlockChange` entries. Ordered by `(old_index,new_index)` for determinism.

## Services

- DocumentLoader: thin facade around parser with metrics timing & counters (`documents_loaded`).
- DocumentSerializer: utilities shared with the editor (newline normalization, JSON-ability conversion, and YAML dump helpers).

## Metrics

`metrics.py` defines the `MetricsCollector` protocol plus `NoOpMetricsCollector` (default) and `InMemoryMetricsCollector` for tests. `TimingContext` is a simple `with` helper.

Key operation names currently recorded:
- `parse_file`, `services.load_from_file`, `services.dumps_yaml`, `services.dump_yaml`, `editor.save`, `validation`

You can override the global default via `set_default_collector(...)` and inspect counters in tests.

## Logging

`logger.get_logger(name="pytuin.desktop")` returns a named logger with a `NullHandler` and level set by `PYTUIN_LOG_LEVEL`. All modules use structured logging (`extra={...}`) for machine-readability.

## Repositories

`repository.DocumentRepository` is a Protocol with `get/save/list`. The bundled `InMemoryDocumentRepository` is sufficient for tests and examples. Wire a custom repository into `DocumentEditor` to persist versions elsewhere.

## Error Types

All raised domain errors inherit from `AtrbError` and include:
- human message
- optional `suggestion`
- optional `context` dict (included in the exception message string)

## Extending the Block Set

1. Props: add a Pydantic props model to `block_props.py`.
2. Model: add a typed block to `models.py` and extend the `Block` union.
3. Validation: update `validator.py` with semantic checks.
4. Templates: add Templateer templates under `.templateer/` for creation.
5. Builders: expose a convenience method in `builders.py`.
6. Tests: add/extend tests in `src/tests/` for round-trip and validation.
7. Docs: update this guide and the README.

## Testing

The repo uses `pytest`. Common patterns:
- Unit tests for builders, parser, validator, block container semantics, and editor behavior.
- Integration tests that create a temporary `.templateer/`, discover templates, generate blocks, write to disk, and parse back.
- Metrics assertions with `InMemoryMetricsCollector` where applicable.

## Versioning & Releases

- Version is exported as `pytuin_desktop.__version__`.
- Prefer semver pre-releases while iterating (e.g. `0.4.0-alphaN`).
- Changelog entries should call out new blocks, breaking validation, and template contract changes.

## Style & Conventions

- Python >=3.11, Pydantic v2.
- Keep templates declarative; do not hide IO in builders or templates.
- Always raise domain-specific errors (`Atrb*`) over bare exceptions when user-facing.
- Keep public names stable via `__all__` in `__init__.py`.

## Cookbook Snippets

Swap a block in place:
```python
from pytuin_desktop import DocumentEditor, BlockBuilder

ed = DocumentEditor.create("cookbook", version=1)
ed.add_block(BlockBuilder.heading("Old", level=1))
ed.replace_block_at(0, BlockBuilder.heading("New", level=1))
```

Move within "new" region:
```python
a, b, c = BlockBuilder.paragraph("A"), BlockBuilder.paragraph("B"), BlockBuilder.paragraph("C")
ed = DocumentEditor.create("order", version=1).add_blocks([a, b, c])
ed.move_block(2, 0)  # C, A, B
```

Diff two files:
```python
from pytuin_desktop import AtrbParser, DocumentDiffer

d1 = AtrbParser.parse_file("before.atrb")
d2 = AtrbParser.parse_file("after.atrb")
changes = DocumentDiffer.diff(d1, d2).changes
```

Happy hacking!
