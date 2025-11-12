# Pytuin-Desktop — Developer Plan (Refactor Track)

This plan is a sequence of incremental, testable steps. Each step defines objectives, development tasks, and tests with clear exit criteria.

> Conventions: keep imports consistent with current modules (discovery, builders, editor, parser, models). Prefer Pydantic v2 models for new public surfaces. Avoid global state except for optional template cache guarded by functions.

## Step 1 — Introduce explicit template discovery parameter
**Objective:** Decouple from CWD; enable deterministic tests.  
**Dev:**
- Update `load_atrb_templates` to accept `template_dir: Path | str | None` and `cache: bool = True`.
- Resolve directory: explicit arg > `PYTUIN_TEMPLATE_DIR` > default `.templateer` (project root).
- Add internal per-path cache and `clear_template_cache()`.
- Thread `template_dir` through `BlockBuilder` factories and `DocumentEditor.create(...)`.
**Tests:**
- Discovery with explicit dir finds expected templates.
- Env fallback works when arg is None.
- Cache hit path (spy loader called once); `clear_template_cache()` invalidates.
**Exit:** All discovery and builder tests pass with new argument signatures.

## Step 2 — Logger hooks
**Objective:** Make actions observable under a caller-provided logger.  
**Dev:**
- Create `get_logger(name="pytuin.desktop")` returning a logger with `NullHandler`.
- Accept `logger: Logger | None` in discovery/editor/parser; default to module logger.
- Emit structured messages (counts, paths, durations where trivial).
**Tests:**
- Use a `caplog` fixture to assert messages at `INFO/DEBUG` when provided.
- Ensure silence by default (no handlers, no output).  
**Exit:** Caplog assertions pass; no stdout/stderr noise by default.

## Step 3 — Error taxonomy
**Objective:** Replace generic exceptions with a clear hierarchy.  
**Dev:**
- Define `AtrbError` base and the specific subclasses: `AtrbParseError`, `AtrbSchemaError`, `AtrbValidationError`, `TemplateDiscoveryError`.
- Update parser/validator/discovery to raise these.
**Tests:**
- Force parse failures and assert raised types.
- Validate schema mismatch paths.  
**Exit:** All exception mapping tests pass.

## Step 4 — Deterministic formatting
**Objective:** Normalize write behavior.  
**Dev:**
- Ensure a single trailing newline on `write*` when flag is True.
- Jinja env remains strict and preserves trailing newlines on templates.
**Tests:**
- Parametrized tests verifying: exactly one trailing newline; idempotent writes produce identical bytes.  
**Exit:** Formatting tests pass.

## Step 5 — Round-trip editor (preserve blocks)
**Objective:** Enable append/edit flows on existing files without losing content.  
**Dev:**
- Implement `DocumentEditor.from_file_with_blocks(path, logger=None)` that attaches parsed blocks to the editor instance.
- Editor’s `render()` iterates existing `BaseBlock` instances alongside new blocks.
**Tests:**
- Given an existing `.atrb`, load with blocks, append a heading via builder, write, and re-parse; assert old + new blocks present and order preserved.
**Exit:** Round-trip edit tests pass.

## Step 6 — Stream I/O
**Objective:** Support UNIX pipelines and in-memory testing.  
**Dev:**
- Add `AtrbParser.parse_stream(stream)` and `DocumentEditor.write_to_stream(stream, ensure_trailing_newline=True)`.
- Factor core logic to work on strings/streams, file wrappers call into stream versions.
**Tests:**
- Round-trip via `io.StringIO`: parse → edit → write_to_stream → parse_stream.
- Trailing newline guaranteed when flag is True.  
**Exit:** Streaming cycle tests pass.

## Step 7 — Enums and typed props
**Objective:** Strengthen type guarantees for CLI surfaces.  
**Dev:**
- Introduce enums: `TextAlignment`, `ColorToken`, etc.
- Update builders and models to accept enums (and serialize to canonical strings).
- Back-compat: parser accepts previous string values (case-insensitive) and maps to enums.
**Tests:**
- Enum round-trip: set enum → serialize → parse → same enum.
- Invalid value raises `AtrbValidationError` with a clear message.  
**Exit:** Prop typing tests pass.

## Step 8 — Validator service
**Objective:** Separate schema/semantic checks and expose a clean API.  
**Dev:**
- Implement `AtrbValidator.validate(doc)` with specialized checks (structure, required props, enum domains).
- Parser calls validator optionally (flag), editor uses validator before write.
**Tests:**
- Valid documents pass silently.
- Invalid inputs raise specific error class per violation (schema vs semantic).  
**Exit:** Validator tests green.

## Step 9 — Repository protocol (optional seam)
**Objective:** Future-proof persistence integration.  
**Dev:**
- Define `DocumentRepository` protocol and `InMemoryDocumentRepository` for tests.
- Provide adapters in editor to optionally `save()` after writes when a repo is supplied.
**Tests:**
- Save → list → get cycles with in-memory implementation.
- Editor integration test: write with repo, assert repo contains updated doc.  
**Exit:** Repo seam tests pass; feature is optional.

## Step 10 — Public API review and module exports
**Objective:** Stabilize import paths for future CLI.  
**Dev:**
- Re-export key symbols from `pytuin_desktop.__init__` (builders, editor, parser, enums, exceptions).
- Add `__version__` bump.
**Tests:**
- Import smoke tests from top-level package path.
- Backwards-compat tests for previously public names.  
**Exit:** Import matrix passes.

## Step 11 — Integration tests mirroring CLI flows
**Objective:** Validate end-to-end user scenarios.  
**Dev:**
- Add tests that simulate:
  1. create → add blocks → write → parse → validate.
  2. parse existing → append → write → re-parse.
  3. stdin → stdout streaming transform (StringIO).
- Use temporary directories and explicit `template_dir` to avoid CWD dependence.
**Tests:** As described; assert logs, outputs, exit-like statuses via raised exceptions mapping.  
**Exit:** All integration tests pass.

## Step 12 — Documentation & examples
**Objective:** Ensure developers understand the new seams.  
**Dev:**
- Update `USER.md` and `DEV_GUIDE.md` with examples for: discovery parameter, logging, streaming, error classes, enums.
- Provide small code examples for each surface.  
**Tests:**
- Doctest minimal examples (if enabled) or import/code-snippet smoke tests.  
**Exit:** Docs build/tests pass.

---

## Testing Notes
- Prefer `pytest` with `tmp_path` fixtures and `caplog` for logging checks.
- Avoid network/filesystem flakiness; use `StringIO` for streaming tests.
- For cache tests, use a monotonic counter or spy to observe load calls.
- Maintain high coverage for newly added code paths (≥90% for refactor track).

## Definition of Done
- All steps completed with tests and docs green.
- Public API documented and re-exported.
- Deterministic I/O and explicit discovery confirmed by integration tests.
