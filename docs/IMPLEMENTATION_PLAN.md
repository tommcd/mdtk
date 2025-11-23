# Implementation Plan: Core Improvements and Document Graph Feature

This document translates the earlier critique and ideation into concrete, trackable work items. It has two tracks:

1. **Core API improvements** for the existing bookmarks-to-Markdown tool.
2. **New document graph feature** enabling splitting/combining with transclusion.

Each work item lists goals, deliverables, suggested sequencing, and quality gates.

---

## Track 1: Core API Improvements (Bookmarks Converter)

### Objectives
- Decouple parsing, selection, and rendering to enable reuse and testing of each step.
- Expose a minimal yet extensible library API and formalize error handling.
- Add documentation and examples that reflect the richer API surface.

### Work Breakdown
1. **Module refactor**
   - Introduce internal layers (proposal):
     - `parse_bookmarks(html_path) -> BookmarkTree`
     - `select_folder(tree, folder_name) -> BookmarkFolder`
     - `render_markdown(folder, *, nested: bool, template: Optional[str]) -> str`
   - Keep `convert_bookmarks` as a thin orchestrator using the new layers.
   - Ensure folder selection handles nested folders and reports ambiguity.

2. **Error taxonomy**
   - Define granular exceptions (e.g., `InputFileError`, `ParseError`, `FolderNotFoundError`, `RenderError`).
   - Map CLI exit codes/messages to these errors; avoid over-broad exception wrapping.

3. **Extensibility hooks**
   - Allow custom renderers via a protocol (e.g., `BookmarkRenderer` with `render(folder) -> str`).
   - Support optional nested output and simple templating (Jinja or format strings) for link lines.

4. **Docs and examples**
   - Add API docs detailing function signatures, error classes, and usage patterns.
   - Provide cookbook-style examples (e.g., render nested lists, custom link formatting).

5. **Testing**
   - Unit tests per layer: parsing fidelity, folder selection (including nested/duplicate names), rendering variations, and CLI integration.
   - Add golden-file tests for Markdown output to guard against regressions.

### Quality Gates
- Public API documented in `docs/` and reflected in README feature section.
- Test coverage for new layers and CLI paths.
- Backward compatibility: `convert_bookmarks` and CLI flags remain functional.

---

## Track 2: Document Graph Feature (Splitting, Combining, Transclusion)

### Objectives
- Introduce a graph-native document model to support splitting large documents, transclusion, and recomposition into unified views.
- Provide a declarative configuration/DSL for authoring and rendering graph-based documents.
- Offer rendering backends (Markdown/HTML) that can materialize slices or unified outputs with provenance.

### Proposed Architecture
1. **Core data structures**
   - Immutable graph representation where nodes are content blocks (sections, paragraphs, snippets) and edges are typed (`contains`, `includes`, `refers`, `variant-of`).
   - Node/edge metadata: stable IDs, tags, source file/offset, provenance (`derived-from`).
   - Optional hyperedge support for multi-source composites (can be modeled as nodes representing groups if libraries are limited).

2. **Parsing and chunking layer**
   - Importers: Markdown (via existing parsers or Pandoc JSON), with pluggable chunking strategies (heading-based, TextTiling-style similarity, fixed-size paragraphs).
   - Deduplication with structural hashing (Merkle-style IDs) to reuse identical blocks across docs.

3. **Transclusion semantics**
   - Edge rules: `contains` is acyclic; `includes` (transclusion) detects cycles with configurable limits; `refers` is unconstrained.
   - Parametric includes: blocks may expose parameters; expansions track a call graph for diagnostics.
   - Hygiene: namespace/label scoping to avoid collisions (e.g., footnotes).

4. **Transformation and validation**
   - Small rewrite DSL: pattern-match subgraphs and replace them (e.g., collapse short paragraphs into a summary node).
   - Validation layer ensures schema compliance (required fields per node type, allowed edge types) and cycle policies.

5. **Query and slicing**
   - Provide a query surface (start simple with filter + traversal combinators; consider Datalog/GraphQL later) to retrieve slices (e.g., all nodes tagged `policy`, or all dependents of snippet X).
   - Slice views feed renderers to produce variant outputs (short read, deep dive).

6. **Rendering**
   - Markdown and HTML renderers that traverse the graph with configurable strategies (topological by `contains`, inclusion expansion rules, optional breadcrumbs).
   - Provenance annotations: ability to emit backlinks to source fragments.

7. **Storage and versioning**
   - Persist graph states as JSON/JSONL with hashes for incremental builds.
   - Optional CRDT-friendly representation if collaborative editing is desired later; start with immutable snapshots plus diffs.

### User-Facing DSL/Config
- A declarative “document map” file (TOML/YAML) defining:
  - Input sources and chunking strategy.
  - Node tags/attributes and explicit inclusion edges.
  - Rendering profiles (which traversal, which renderer, transclusion depth policy).
- Provide starter templates and validation for this config.

### CLI and Library Surface
- CLI entry point (e.g., `mdtk-graph`) with commands:
  - `build`: parse sources into a graph snapshot.
  - `render`: produce outputs per profile or inline profile definition.
  - `query`: run predefined/simple queries and emit JSON/Markdown snippets.
- Library modules:
  - `graph.model` (nodes/edges/types), `graph.parse`, `graph.rewrite`, `graph.render`, `graph.query`.

### Testing and Tooling
- Unit tests for parsing, chunking heuristics, transclusion expansion, cycle detection, and rendering determinism.
- Golden tests for rendering profiles; property tests for cycle-handling and ID stability.
- Fuzz small random graphs to ensure traversals terminate under cycle policies.

### Migration and Documentation
- Narrative docs explaining the graph model, examples of splitting a large doc and recombining views, and tutorials for the DSL config.
- Comparison with prior art (transcluding wikis, Pandoc) to position the feature and clarify interoperability.

### Milestones (Suggested Sequence)
1. **Foundations**: define graph model, storage format, and minimal parser for Markdown → graph (heading-based chunks).
2. **Transclusion & validation**: implement include edges, cycle policies, schema checks.
3. **Rendering v1**: Markdown renderer with basic traversal and provenance breadcrumbs.
4. **Config/DSL v1**: document map to declare sources, edges, and rendering profile; CLI `build` and `render`.
5. **Advanced chunking & rewrites**: add similarity-based chunking and rewrite DSL.
6. **Query layer**: minimal filter/traversal DSL, expand as needed.
7. **Ecosystem bridges**: Pandoc import/export, HTML renderer, deduplication via hashing.

---

## Governance and Tracking
- Treat each milestone as an epic with acceptance criteria tied to the quality gates above.
- Maintain a changelog entry per milestone and update documentation alongside code changes.
- Keep API stability notes: mark experimental modules clearly until stabilized.

