# Pytuin-Desktop — Library Specification (Refactor Track)

## 1. Purpose
Provide a deterministic, testable library for generating, editing, validating, and parsing `.atrb` (Atuin Runbook) documents. The refactor introduces CLI-friendly seams (configurable discovery, streaming I/O, structured error taxonomy, logging hooks) without breaking the core data model.

## 2. Scope
- In scope: template discovery, block builders, editor, parser, validators, I/O helpers, logging, error taxonomy, type safety, and an optional storage seam.
- Out of scope (for this track): a full Typer CLI, DB persistence implementations (define protocols only), GUI.

## 3. Core Concepts
- **Templates**: Jinja-based `.templateer` content that renders blocks and documents with strict undefined behavior and trailing newline guarantees.
- **Blocks**: Typed representations of content fragments (e.g., paragraph, heading, hr) with validated props and optional inline styles.
- **Document**: Top-level composed structure including metadata (`id`, `name`, `version`) and an ordered list of blocks.
- **Parser**: Robust `.atrb` -> in-memory model with validation. Also provides schema checks.
- **Editor**: High-level API to compose and persist documents from templates and existing files.
- **Discovery**: Resolves the active template directory and loads templates.
- **Repository seam (optional)**: Protocol for persistence; concrete implementations may use SQLModel later.

## 4. Non-Functional Requirements
- **Determinism**: Stable rendering/formatting. Writes end with a final newline.
- **Configurability**: No reliance on CWD; accept an explicit `template_dir` everywhere reasonable. Environment var fallback supported.
- **Observability**: Structured logging; verbosity level controllable by caller.
- **Type Safety**: Enums/Literals for constrained props; Pydantic models for data validation where applicable.
- **Compatibility**: Backwards compatible serialized form unless explicitly version-bumped.
- **Testability**: Pure functions where feasible, seam injection for I/O, mocks/fakes for repositories and logging.

## 5. Public API (stabilized)
### Discovery
- `load_atrb_templates(template_dir: Path | str | None = None, *, cache: bool = True) -> TemplateRegistry`  
  - `template_dir` precedence: explicit arg > env `PYTUIN_TEMPLATE_DIR` > default `.templateer` adjacent to project root.
  - Optional in-process cache keyed by absolute path.

### Builders
- `BlockBuilder` factories accept `template_dir` (threaded to discovery). All public factory methods remain, but gain enums for constrained props where present.

### Editor
- `DocumentEditor.create(name: str, version: int, *, template_dir: PathLike | None = None, logger: Logger | None = None) -> DocumentEditor`
- `DocumentEditor.from_file(path: PathLike, *, logger: Logger | None = None) -> DocumentEditor` (metadata-only)
- `DocumentEditor.from_file_with_blocks(path: PathLike, *, logger: Logger | None = None) -> DocumentEditor` (preserve parsed blocks)
- `DocumentEditor.write(path: PathLike, *, ensure_trailing_newline: bool = True) -> None`
- `DocumentEditor.write_to_stream(stream: io.TextIOBase, *, ensure_trailing_newline: bool = True) -> None`

### Parser & Validation
- `AtrbParser.parse(path: PathLike) -> Document`
- `AtrbParser.parse_stream(stream: io.TextIOBase) -> Document`
- `AtrbValidator.validate(doc: Document) -> None` (raises specific errors)
- Exceptions taxonomy:
  - `AtrbError` (base)
  - `AtrbParseError`
  - `AtrbSchemaError`
  - `AtrbValidationError`
  - `TemplateDiscoveryError`

### Logging
- Module-level `logger` with `NullHandler` by default; components accept an optional `Logger` to override.
- Log events: discovery (dir, counts), parse (start, success/fail), render/write (path, bytes), validation outcomes.

### Repository Protocol (optional)
- `class DocumentRepository(Protocol):`
  - `get(doc_id: str) -> Document | None`
  - `save(doc: Document) -> None`
  - `list(limit: int = 50, offset: int = 0) -> list[Document]`
- Not required by core flows; used by future CLI subcommands.

## 6. Data & Types
- **Enums** (examples):
  - `TextAlignment = Enum("left", "center", "right", "justify")`
  - `ColorToken = Enum("default", "muted", "accent", ...)`
  - `HeadingLevel = Literal[1, 2, 3, 4, 5, 6]`
- **Models**: Pydantic (v2) for public data classes / inputs; internal templates remain lightweight dataclasses if already present.

## 7. I/O Guarantees
- All text I/O is UTF-8.
- Every write ends with `\n` when `ensure_trailing_newline=True`.
- Streaming helpers read/write without BOM.

## 8. Caching
- Template registry may cache per absolute directory. Include `cache=False` to bypass.
- Cache invalidation is manual (call `clear_template_cache()`), and automatic if mtime changes (best-effort).

## 9. Environment Variables
- `PYTUIN_TEMPLATE_DIR` — default discovery directory when no explicit argument is provided.
- `PYTUIN_LOG_LEVEL` — fallback level if no logger provided.

## 10. Backwards Compatibility
- Parsers accept existing `.atrb` generated by earlier versions.
- New enums accept the previous string values where applicable (case-insensitive parse if safe).

## 11. Testing Strategy
- Unit tests for each component with fixtures that simulate different template dirs.
- Integration tests: round-trip parse → edit → write → re-parse consistency; stdin/stdout streaming cycles.
- Property-based tests for normalization (e.g., trailing newline).

## 12. Versioning
- Semantic versioning. Minor version bump for the new API surface; patch releases for bugfixes.
