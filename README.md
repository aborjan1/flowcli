# flowcli

Static call-graph mapper for Python codebases. Point it at a directory (or a single file) and it
parses every `.py` via `ast`, resolves who-calls-whom, and emits a machine-readable report, a
Markdown report, and a self-contained interactive force-directed graph (Obsidian-style).

v1 is **static analysis only** — zero runtime dependencies, pure stdlib. The data model reserves a
`dynamic` slot per node for the v2 profiler merge (cProfile timings, flame graph).

## Usage

**Two arguments: what to map, and where to start.**

```bash
flowcli src/mypkg                        # map it, and get entry points suggested
flowcli src/mypkg comm/                  # start from everything under a folder
flowcli src/mypkg core.py                # start from every function that file defines
flowcli src/mypkg core.py:process        # start from one function
flowcli src/mypkg mypkg.core:process     # dotted entry works too

# several starting points at once — repeat them, or comma-separate
flowcli src/mypkg comm/client.py:connect comm/event_store.py
flowcli src/mypkg "comm/client.py:connect,comm/event_store.py,core.py:run"
```

The first argument is always the package to parse — so imports and class hierarchies resolve
across the whole tree. What follows says where to start reading, and *scopes the report* to those
call graphs. Each entry can be a **folder** (every function in every module beneath it,
subpackages included), a **file** (every function it defines), a **single function**, or a dotted
module or package name — and you can give **as many as you like**, mixing kinds freely. They all
start at depth 0 and the report covers their combined reach. Leave entries off and flowcli
**suggests entry points** it detected (console scripts, `main()`s, names exported from
`__init__`, functions nothing else calls) — pass some back. Output lands in `./MODEL`.

```
flowcli PATH [ENTRY] [options]

  -o, --out-dir DIR          output directory (default: ./MODEL)
  --depth N                  include at most N call-hops from the entry
  --keep-unreachable         keep out-of-scope functions (depth-annotated) instead of pruning
  --include-external         materialize stdlib/third-party targets as leaf nodes
  --exclude GLOB             skip matching paths (repeatable, fnmatch syntax)
  --no-simulate              skip the inferred data-flow simulation
  --no-classes               skip the class / data-model view
  --runtime FILE             merge a flowcli-run runtime.json
  --formats json,md,html     comma-separated subset (default: all three)
  -q, --quiet                suppress the terminal summary

flowcli run [options] prog...      trace a real execution, then map it

  prog...                    script.py [args...]  or  -- -m module [args...]
  --root PATH                code root to trace (default: the script's package)
  --no-samples               record observed types only, no value snapshots
  --no-map                   only write runtime.json, skip building the map
```

Outputs:

- `report.json` — full node list + meta + unresolved calls (`schema_version: 1`, `dynamic: null` on
  every node, reserved for profiler data)
- `report.md` — call-graph table sorted by out-degree, top-10 most-called, unreachable list (with
  `--entry`), unresolved-call breakdown
- `graph.html` — offline single-file interactive explorer with two separated views:
  - **Call-graph explorer** (left, force layout): modules start **collapsed** as super-nodes
    (size ∝ function count) with aggregated cross-module call edges — a module dependency view.
    Opening a function is **call-scoped**: it reveals only that function plus the functions it
    directly uses, wherever they live — never whole modules. Calls into still-hidden code point
    at the module bubble (labeled with the hidden count); follow a revealed callee to surface the
    next hop. Clicking a module bubble (or its legend row) expands all of it, explicitly.
    "Expand all" / "Collapse all" switch between the flat graph and a clean reset. Drag nodes,
    scroll to zoom, drag background to pan, hover for details, double-click to reheat. Module
    labels fade in with zoom. With `--entry`, the entry function and its callees start revealed.
  - **Flow panel** (right, opens on function click): a **deterministic flowchart** of the
    function's control flow — statements as boxes, `if`/`match`/`try` as branching diamonds with
    per-branch labels, loops with back-edges, returns as terminators. Resolved call sites appear
    as clickable `↳ target` chips: clicking one **inlines the callee's flowchart right at the
    call site** (a dashed sub-diagram; click its header or the chip again to collapse), and
    inlined diagrams have their own chips for going deeper. Recursion and inlining beyond 6
    levels render as a marker instead of nesting forever. The revealed functions stay synced
    into the graph view. Esc closes. The layout is computed, not simulated — the same function
    with the same expansions always renders the same diagram.

Examples:

```bash
flowcli src/mypkg                                # full package map + suggested entries
flowcli src/mypkg cli.py:main                    # just main()'s call graph
flowcli src/mypkg cli.py --formats json,html     # the whole file's ecosystem
flowcli src/mypkg core.py:process --depth 3      # three call-hops deep
```

Packages don't need `__init__.py` — namespace packages and plain source trees are rooted by
walking up to the nearest `pyproject.toml`/`setup.py`/`src`, so relative imports still resolve.

## Data flow

Three layers, in increasing order of truthfulness — the first two need no execution at all,
which matters when the code only runs on a device:

- **Static inference** (always on): parameters come from annotations; return types come from the
  annotation when present, otherwise they're inferred from return statements — literals,
  constructor calls (`return Engine()` → `Engine`), typed locals, and calls to other functions
  whose return type is known, chained through a bounded fixpoint (recursion and cycles are safe).
  Inferred types are marked `~`. Every function's signature lands in `report.json`, a
  `## Signatures` table in `report.md`, and the diagram's header box (params in, `returns:` out;
  each `return` box shows what that branch yields).
- **Simulation** (on by default): a static stand-in for a debugger session. Every call site's
  arguments are bound to the callee's parameters and propagated across the graph — literals carry
  their actual value (`fact(5)` → `n = 5`), names carry their declared type, nested calls carry the
  callee's return type — iterated to a fixpoint so values travel several hops from the entry.
  Diagrams show `n: int ~ 5` (the `~` marks simulated, never observed), and the replay animation
  walks a **simulated call order** (depth-first from the entry, in source-line order), so you can
  step through code that can never run locally. Turn it off with `--no-simulate`.
- **Runtime tracing** (`flowcli run`): executes your script/module under a `sys.setprofile` hook
  filtered to files under `--root`, recording per function: call count, observed argument and
  return types on every call, truncated `repr()` snapshots of the first 5 calls, and a bounded
  call-event log (2000 events). `runtime.json` merges into the map via `--runtime` (or `run
  --map`), filling each node's `dynamic` field — diagrams then show `declared | seen` types,
  call-count badges, and sample values on hover; the graph gains a **▶ Replay** button that
  animates the recorded call sequence. Caveats: main thread only; an exception unwind is recorded
  as a `None` return; C functions and `lru_cache` hits produce no frames; classes defined in the
  traced `__main__` script report `__main__.X` type names.

```bash
flowcli run --root src/mypkg script.py --arg value
flowcli run --root src/mypkg -- -m mypkg
```

### Views

The tabs in the top bar switch between two graphs built from the same parse:

- **Call graph** — what runs what (everything described above).
- **Classes** — what *holds* what: the data model. Each class is a card with its properties
  (`value: float`, `unit: Unit`) and public methods, tagged with a stereotype where one applies
  (`«enum»`, `«dataclass»`, `«struct»`, `«abstract»`). Solid edges are **has-a** relations, labelled
  with the property name — a `Measurement` whose `unit` is a `Unit` draws an edge labelled `unit`.
  Green dashed edges are **inheritance**, so a `Unit(StrEnum)` shows its base (bases outside the
  parsed tree, like `StrEnum` itself, are listed on the card but aren't nodes). Properties come from
  class-level annotations, dataclass fields, and `self.x = …` in `__init__`.
  Clicking a class opens a **structure panel** on the right — the data-model counterpart of the
  flow diagram. It lists the class's properties, and any property whose type is another class
  carries a `▸` you can click to **expand that class inline, nested inside the parent**, as deep as
  the model goes (recursive types are marked instead of unrolled, and nesting stops at 6 levels).
  A `Measurement` opens to reveal `unit: Unit`, which opens in place to reveal `MM`, `CM`.
  Clicking a **method row jumps to that method's flow diagram** in the call view. `--no-classes`
  skips the whole view, and `report.json` gains a `classes` block plus a `## Classes` table in
  `report.md`.

- **Trace focus**: opening any function's diagram reduces the left graph to just the traced
  system — the function, its callers (faded) and callees, growing as you inline deeper calls.
  Esc restores the full explorer. The `☰` button brings the module tree back while focused.
- **Top-down**: a deterministic layered layout — entry points (nothing visible calls them) on
  top, calls flowing downward — for reading start-to-end paths. Toggles with the force layout.
- **Step debugger**: the bar at the bottom walks the call sequence one call at a time — play at
  an adjustable pace, or step with the arrows (`←`/`→`, space to play/pause). Each step names the
  call being made and the arguments flowing into it (`main → helper(n=5)`) and reveals nodes as
  they're first reached. The **last five calls stay lit**, brightest for the most recent and
  fading with age, on both the graph edges and the cards, with the same trail listed above the
  bar — so you can see the path that got you here, not just the current hop. Stepping backward
  re-derives the trail, so it is always correct. The sequence is the traced call order when
  runtime data exists, the simulated one otherwise.
- **Animations**: `⇉` in the panel head marches the flow-diagram edges in call direction.
  Respects `prefers-reduced-motion`.

## Development

```bash
uv sync           # create venv + install (editable) + dev deps
uv run pytest     # test suite
uv run ruff check && uv run ruff format --check
uv run mypy
uv run flowcli map src/flowcli -o /tmp/self --entry src/flowcli/cli.py:main   # dogfood
```

## How it works

Two passes, no AST re-walks:

1. **Parse** (`parser.py`) — one visitor walk per file builds a `ModuleInfo`: functions/classes with
   qualified names, a module-wide import table (relative imports resolved to absolute dotted paths),
   and raw call records classified as `NAME` / `DOTTED` / `SELF_ATTR` / `CLS_ATTR` / `SUPER_ATTR` /
   `OPAQUE`. Each function also gets a nested **control-flow tree** (`flow` in report.json) —
   statements, branches, loops, try/except, match — capped at 200 nodes per function; the resolver's
   per-line call targets are attached to flow nodes so diagrams can link to callees.
2. **Resolve** (`resolver.py`) — each raw call is resolved against the project-wide index:
   enclosing function scopes → module functions/classes → import table (with re-export chasing
   through `__init__.py`) → star imports → builtins. `ClassName()` targets the *defining* class's
   `__init__` (walking parsed bases); `self.x()` / `cls.x()` / `super().x()` resolve through an
   MRO-lite hierarchy walk (depth-first left-to-right, cycle-guarded — not full C3, so diamond
   hierarchies follow DFS order). Method calls on typed locals resolve too: parameter annotations
   (`gen: Generator`), annotated assignments (`x: Foo = ...`), and direct constructor assignments
   (`engine = Engine()`) give the variable a class — `gen.build()` then resolves through that
   class's parsed hierarchy. The same works one level into instance attributes:
   `self.db = DBLayer(...)` in `__init__` (or `db: DBLayer` on the class / a parsed base) makes
   `self.db.update()` resolve to `DBLayer.update`. Types that were never parsed (`p: Path`,
   `self.conn = sqlite3.connect(...)`) resolve to nothing, so the scope never leaks into
   stdlib/third-party internals.

Everything that can't be resolved is kept, with a reason: `external` (stdlib/third-party),
`instance-attr` (calls on values, e.g. `obj.run()` — no type inference in v1), `unknown-name`,
`opaque` (calls on call results, subscripts, lambdas), `not-found-in-hierarchy`.

### Naming scheme

- Node ids: `dotted.module:qualname` (e.g. `pkg.models:Engine.start`). External targets are plain
  dotted paths (`os.path.join`) — the missing `:` is the internal/external discriminator.
- Nested functions: `outer.inner` (no `<locals>`). Name collisions get a `#<lineno>` suffix.
- Import-time code (top-level calls, decorator applications, class-body statements) is attributed
  to a synthetic `module:<module>` node, created only when needed — so scripts work as `--entry`
  targets and decorator edges live where they actually execute.

### Known v1 limitations (by design)

- No assignment aliasing (`f = g; f()`), `getattr`, containers of callables, or dynamic dispatch
  beyond the parsed class hierarchy. Type inference covers annotations and direct constructor
  assignments only — not function return types (`x = get_engine(); x.run()` stays unresolved
  unless `x` is annotated).
- Function-local imports are treated module-wide (last write wins).
- `self.x()` resolves only within the *enclosing* class's own hierarchy — never downward to
  subclasses (that's dynamic dispatch; flagged `not-found-in-hierarchy` instead of guessing).
- The HTML layout is O(n²) per frame; a warning is printed above 3000 nodes.
