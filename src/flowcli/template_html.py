"""Self-contained HTML template for the interactive graph explorer.

Kept as a Python string (not package data) so packaging never drops it.
Zero external requests: all CSS/JS inline, data embedded as JSON.

Two separated views:
- Call-graph explorer (canvas, force layout): modules start collapsed as
  super-nodes; clicking a module expands it into its functions.
- Flow panel (SVG, deterministic layered flowchart): clicking a function
  opens its control-flow diagram; call sites are clickable chips that
  navigate to the callee's diagram (breadcrumbs track the path) and expand
  the callee's module in the graph behind.
"""

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>flowcli graph</title>
<style>
  :root {
    --plane: #0d0f13;         /* page behind everything */
    --surface: #14171d;       /* panels */
    --raised: #1b1f27;        /* cards, controls */
    --raised-hi: #232833;
    --line: rgba(255,255,255,0.09);
    --line-strong: rgba(255,255,255,0.16);
    --ink: #e9edf4;
    --ink-2: #a3adbf;
    --ink-3: #6d7789;
    --accent: #3987e5;
    --accent-soft: rgba(57,135,229,0.16);
    --focus: #e0b341;         /* replay / active-step highlight */
    --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    --sans: system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; overflow: hidden; background: var(--plane); color: var(--ink);
               font-family: var(--sans); }
  canvas { display: block; cursor: grab; }
  canvas.dragging { cursor: grabbing; }

  /* ---- top bar ---- */
  #topbar { position: fixed; top: 0; left: 0; right: 0; height: 48px; z-index: 6; display: flex;
            align-items: center; gap: 14px; padding: 0 14px; background: rgba(13,15,19,0.92);
            border-bottom: 1px solid var(--line); backdrop-filter: blur(8px); }
  #brand { font-size: 13px; font-weight: 650; letter-spacing: 0.02em; color: var(--ink); }
  #brand span { color: var(--accent); }
  #views { display: flex; gap: 2px; background: var(--raised); border: 1px solid var(--line);
           border-radius: 8px; padding: 2px; }
  .vtab { font: 11.5px var(--sans); color: var(--ink-3); background: none; border: none; cursor: pointer;
          padding: 4px 11px; border-radius: 6px; }
  .vtab:hover { color: var(--ink-2); }
  .vtab.on { background: var(--raised-hi); color: var(--ink); font-weight: 600; }
  #scope { font: 11px/1.4 var(--mono); color: var(--ink-3); white-space: nowrap; overflow: hidden;
           text-overflow: ellipsis; max-width: 40vw; }
  #stats { margin-left: auto; display: flex; gap: 14px; font-size: 11px; color: var(--ink-3); }
  #stats b { color: var(--ink-2); font-weight: 600; font-variant-numeric: tabular-nums; }
  #search { width: 190px; font: 12px var(--sans); color: var(--ink); background: var(--raised);
            border: 1px solid var(--line); border-radius: 7px; padding: 5px 9px; outline: none; }
  #search:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
  #search::placeholder { color: var(--ink-3); }

  /* ---- side panel ---- */
  #legend { position: fixed; top: 60px; left: 12px; width: 262px; max-height: calc(100% - 132px);
            overflow-y: auto; font-size: 12px; color: var(--ink-2); background: rgba(20,23,29,0.94);
            border: 1px solid var(--line); border-radius: 12px; padding: 10px; user-select: none;
            z-index: 4; box-shadow: 0 12px 32px rgba(0,0,0,0.42); scrollbar-width: thin; }
  #legend::-webkit-scrollbar { width: 8px; }
  #legend::-webkit-scrollbar-thumb { background: var(--raised-hi); border-radius: 4px; }
  #legend .buttons { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px; }
  #legend button { font: 11px var(--sans); color: var(--ink-2); background: var(--raised);
                   border: 1px solid var(--line); border-radius: 6px; padding: 4px 9px; cursor: pointer;
                   transition: background 0.12s, color 0.12s, border-color 0.12s; }
  #legend button:hover { background: var(--raised-hi); color: var(--ink); }
  #legend button.on { color: #ffdd9e; border-color: rgba(224,179,65,0.45); background: rgba(224,179,65,0.12); }
  #legend.hidden { display: none; }
  #legend-restore { position: fixed; top: 60px; left: 12px; z-index: 4; font: 14px var(--sans);
                    color: var(--ink-2); background: var(--surface); border: 1px solid var(--line);
                    border-radius: 8px; padding: 5px 10px; cursor: pointer; }
  .sect { font-size: 10px; letter-spacing: 0.09em; text-transform: uppercase; color: var(--ink-3);
          margin: 12px 2px 6px; font-weight: 600; }
  .sect:first-of-type { margin-top: 4px; }
  #legend .entry { display: flex; align-items: center; gap: 8px; cursor: pointer; white-space: nowrap;
                   padding: 3px 6px; border-radius: 6px; line-height: 1.5; }
  #legend .entry:hover { background: var(--raised); }
  #legend .entry.collapsed { color: var(--ink-3); }
  #legend .swatch { width: 9px; height: 9px; border-radius: 3px; flex: none; }
  #legend .modname { overflow: hidden; text-overflow: ellipsis; flex: 1; }
  #legend .count { font-size: 10px; color: var(--ink-3); font-variant-numeric: tabular-nums; }
  #legend .fnrow { padding: 3px 6px 3px 25px; cursor: pointer; color: var(--ink-2); font: 11px var(--mono);
                   white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border-radius: 6px; }
  #legend .fnrow:hover { color: var(--ink); background: var(--raised); }
  .eprow { display: flex; flex-direction: column; gap: 1px; padding: 5px 7px; border-radius: 7px;
           cursor: pointer; border: 1px solid transparent; }
  .eprow:hover { background: var(--raised); border-color: var(--line); }
  .eprow .ename { font: 11px var(--mono); color: var(--ink); overflow: hidden; text-overflow: ellipsis; }
  .eprow .ewhy { font-size: 10px; color: var(--ink-3); }
  .badge { display: inline-block; font-size: 9px; letter-spacing: 0.05em; text-transform: uppercase;
           padding: 1px 5px; border-radius: 4px; margin-right: 5px; font-weight: 600; }
  .badge.script { background: rgba(57,135,229,0.18); color: #8bbdf5; }
  .badge.main { background: rgba(25,158,112,0.18); color: #57c79b; }
  .badge.public { background: rgba(201,133,0,0.18); color: #dcae4d; }
  .badge.root { background: rgba(255,255,255,0.07); color: var(--ink-3); }

  #tooltip { position: fixed; pointer-events: none; font: 12px/1.55 var(--mono); color: var(--ink);
             background: rgba(20,23,29,0.97); border: 1px solid var(--line-strong); border-radius: 9px;
             padding: 8px 11px; max-width: 480px; white-space: pre-line; z-index: 10;
             box-shadow: 0 10px 28px rgba(0,0,0,0.5); }
  #hud { position: fixed; left: 12px; bottom: 10px; font-size: 11px; color: var(--ink-3);
         user-select: none; z-index: 4; }

  /* ---- step debugger ---- */
  #stepper { position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%); z-index: 7;
             display: none; align-items: center; gap: 10px; padding: 9px 13px; background: rgba(20,23,29,0.96);
             border: 1px solid var(--line); border-radius: 12px; box-shadow: 0 14px 36px rgba(0,0,0,0.5); }
  #stepper.on { display: flex; }
  #stepper button { font: 12px var(--sans); color: var(--ink-2); background: var(--raised);
                    border: 1px solid var(--line); border-radius: 7px; padding: 5px 10px; cursor: pointer; }
  #stepper button:hover { background: var(--raised-hi); color: var(--ink); }
  #stepper button.primary { background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }
  #stepper button.primary:hover { background: #4b95ea; }
  #stepper .callnow { font: 11px var(--mono); color: var(--ink-2); min-width: 300px; max-width: 46vw;
                      white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  #stepper .callnow b { color: var(--focus); font-weight: 600; }
  #stepper .pos { font: 10px var(--mono); color: var(--ink-3); font-variant-numeric: tabular-nums; }
  #stepper input[type=range] { width: 92px; accent-color: var(--accent); }
  #st-hist { position: fixed; bottom: 68px; left: 50%; transform: translateX(-50%); z-index: 6;
             display: none; text-align: center; pointer-events: none; user-select: none; }
  #st-hist .hrow { font: 10.5px/1.65 var(--mono); color: var(--focus); white-space: nowrap;
                   overflow: hidden; text-overflow: ellipsis; max-width: 46vw; }
  #panel { position: fixed; top: 48px; right: 0; width: 56%; height: calc(100% - 48px); z-index: 5;
           display: flex; flex-direction: column; background: var(--surface);
           border-left: 1px solid var(--line); box-shadow: -18px 0 44px rgba(0,0,0,0.4); }
  #panel[hidden] { display: none; }
  #panel-head { display: flex; align-items: center; gap: 8px; padding: 9px 12px;
                border-bottom: 1px solid var(--line); background: rgba(13,15,19,0.5); }
  #crumbs { flex: 1; font: 12px var(--mono); color: var(--ink-2); overflow-x: auto; white-space: nowrap;
            scrollbar-width: none; }
  #crumbs::-webkit-scrollbar { display: none; }
  #crumbs .crumb { cursor: pointer; color: #7cb4f0; padding: 2px 4px; border-radius: 4px; }
  #crumbs .crumb:hover { background: var(--raised); }
  #crumbs .crumb.here { cursor: default; color: var(--ink); font-weight: 600; }
  #crumbs .sep { margin: 0 3px; color: var(--ink-3); }
  #panel-close { font: 15px/1 var(--sans); color: var(--ink-2); background: none; border: none;
                 cursor: pointer; padding: 3px 7px; border-radius: 6px; }
  #panel-close:hover { color: var(--ink); background: var(--raised); }
  #panel-scroll { flex: 1; overflow: auto; cursor: grab; scrollbar-width: none;
                  background: radial-gradient(circle at 50% 0%, rgba(57,135,229,0.05), transparent 60%); }
  #panel-scroll::-webkit-scrollbar { display: none; }
  #panel-scroll.grabbing { cursor: grabbing; }
  .fempty { padding: 24px; font-size: 13px; color: var(--ink-3); }
  svg text { font: 12px var(--mono); fill: var(--ink); }
  svg text.mid { text-anchor: middle; }
  svg .elab { font-size: 10px; fill: var(--ink-3); }
  svg .fbox { fill: #1a1f28; stroke: #333a47; }
  svg .fbox.ret { fill: #24191c; stroke: #b0565e; }
  svg .fdia { fill: #241f19; stroke: #c98500; }
  svg .fhead { fill: #171d27; stroke: var(--accent); }
  svg .fhead.loop { fill: #16211d; stroke: #199e70; }
  svg .fstart { fill: #1a2634; stroke: var(--accent); }
  svg .fend { fill: #b0565e; }
  svg .fdot { fill: var(--ink-3); }
  svg .fedge { fill: none; stroke: #59637a; stroke-width: 1.3; }
  svg .fedge.dash { stroke-dasharray: 4 3; }
  svg .chip { fill: #7cc4ff; cursor: pointer; }
  svg .chip:hover { fill: #b3ddff; }
  svg .chip.open { fill: #ffd28a; }
  svg .chip.open:hover { fill: #ffe4b8; }
  svg .finline { fill: rgba(35,40,52,0.45); stroke: #4a5568; stroke-dasharray: 5 4; }
  svg .fsig { fill: #171e2a; stroke: var(--accent); stroke-width: 1.3; }
  svg .fsigt { font-weight: 600; fill: var(--ink); }
  svg .cpbox { fill: #171b23; stroke-width: 1.2; }
  svg .cphead { font: 600 13.5px system-ui, sans-serif; fill: #f0f4fa; }
  svg .cpst { font: 10.5px system-ui, sans-serif; text-anchor: end; }
  svg .cprow { font: 12.5px var(--mono); fill: #d5dce8; }
  svg .cprow.base, svg .chip.base { fill: #93b8a8; }
  svg .cptype { font: 12.5px var(--mono); fill: #8c95a8; text-anchor: end; }
  svg .cptype.ref { fill: #8fd0b4; }
  svg .cpnote { font: 11px var(--mono); fill: #6d7789; }
  svg.anim .fedge { stroke-dasharray: 7 4; animation: fmarch 0.9s linear infinite; }
  @keyframes fmarch { to { stroke-dashoffset: -11; } }
  @media (prefers-reduced-motion: reduce) { svg.anim .fedge { animation: none; } }
  #anim-toggle { font: 14px/1 system-ui, sans-serif; color: #cbd2dc; background: none; border: none;
                 cursor: pointer; padding: 2px 6px; }
  #anim-toggle.on { color: #ffd28a; }
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="topbar">
  <div id="brand">flow<span>cli</span></div>
  <div id="views">
    <button class="vtab on" data-view="calls">Call graph</button>
    <button class="vtab" data-view="classes">Classes</button>
  </div>
  <div id="scope"></div>
  <input id="search" type="search" placeholder="Find a function…" autocomplete="off" spellcheck="false">
  <div id="stats"></div>
</div>
<div id="legend"></div>
<button id="legend-restore" hidden title="show/hide explorer">☰</button>
<div id="tooltip" hidden></div>
<div id="hud"></div>
<div id="st-hist"></div>
<div id="stepper">
  <button id="st-back" title="previous call">◀</button>
  <button id="st-play" class="primary" title="play / pause">▶ Play</button>
  <button id="st-fwd" title="next call">▶|</button>
  <span class="pos" id="st-pos">0 / 0</span>
  <input id="st-speed" type="range" min="1" max="10" value="4" title="speed">
  <span class="callnow" id="st-now">ready to step through the call sequence</span>
  <button id="st-reset" title="back to start">⟲</button>
</div>
<div id="panel" hidden>
  <div id="panel-head">
    <div id="crumbs"></div>
    <button id="anim-toggle" title="animate flow direction">⇉</button>
    <button id="panel-close" title="close (Esc)">✕</button>
  </div>
  <div id="panel-scroll"><div id="flow-box"></div></div>
</div>
<script id="flowcli-data" type="application/json">__FLOWCLI_DATA__</script>
<script>
"use strict";
const data = JSON.parse(document.getElementById("flowcli-data").textContent);
const N = data.nodes.length;
const M = data.modules.length;
const links = data.links;

// ---------------------------------------------------------------- entities
const ents = [];
const fnsOf = [];
for (let m = 0; m < M; m++) { fnsOf.push([]); }
data.nodes.forEach(function (n, i) {
  fnsOf[n.m].push(i);
  ents.push({ type: "fn", idx: i, id: n.id, m: n.m, kind: n.kind, file: n.file, line: n.line,
              din: n.in, dout: n.out, depth: n.depth,
              r: Math.min(20, Math.max(4, 4 + 2 * Math.sqrt(n.in + n.out))),
              x: 0, y: 0, vx: 0, vy: 0 });
});
const CLASSES = (data.classes && data.classes.nodes) ? data.classes.nodes : [];
const CLINKS = (data.classes && data.classes.links) ? data.classes.links : [];
const C = CLASSES.length;
let viewMode = "calls";   // "calls" | "classes"
let classesSeeded = false;

function superOf(m) { return N + m; }
function classOf(k) { return N + M + k; }
data.modules.forEach(function (name, m) {
  ents.push({ type: "mod", idx: N + m, id: name, m: m, count: fnsOf[m].length, hcount: fnsOf[m].length,
              r: Math.min(30, 10 + 2.5 * Math.sqrt(fnsOf[m].length)),
              x: 0, y: 0, vx: 0, vy: 0 });
});
CLASSES.forEach(function (c, k) {
  ents.push({ type: "cls", idx: k, id: c.id, m: c.m, name: c.name, st: c.st, file: c.file, line: c.line,
              bases: c.bases, ext: c.ext || [], fields: c.f, meth: c.meth, r: 16, x: 0, y: 0, vx: 0, vy: 0 });
});

const idToIdx = new Map();
data.nodes.forEach(function (n, i) { idToIdx.set(n.id, i); });
const classModules = [];
CLASSES.forEach(function (c) { if (classModules.indexOf(c.m) < 0) { classModules.push(c.m); } });
classModules.sort();

const rawOut = [];            // fn index -> Set of direct callee fn indices
const rawIn = [];             // fn index -> Set of direct caller fn indices
for (let i = 0; i < N; i++) { rawOut.push(new Set()); rawIn.push(new Set()); }
links.forEach(function (l) { rawOut[l.s].add(l.t); rawIn[l.t].add(l.s); });

const expanded = new Set();   // whole modules opened via their bubble
const revealed = new Set();   // individual functions surfaced by following calls
let focusSet = null;          // trace-focus: only these fn entities are shown (null = normal explorer)
let focusDim = new Set();     // pure callers of the focused root, drawn faded
let savedView = null;         // explorer state to restore when focus exits
let layoutMode = "force";     // "force" | "layers" (deterministic top-down)
let autoFit = true;           // frame the graph once the layout settles
let vis = [];
let shown = [];
let dispNbr = new Map();
let topVis = new Set();

const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");
const tooltip = document.getElementById("tooltip");
const dpr = window.devicePixelRatio || 1;
let W = 0, H = 0;
let tx = 0, ty = 0, scale = 1;
let alpha = 1, needsDraw = true;
let hover = -1, selected = -1, dragNode = null, panning = false, lastX = 0, lastY = 0;
let downX = 0, downY = 0, downT = 0, downHit = -1;

// ------------------------------------------------------- graph visibility
function fnVisible(i) { return expanded.has(ents[i].m) || revealed.has(i); }
function place(fnId) { return fnVisible(fnId) ? fnId : superOf(ents[fnId].m); }

function rebuild() {
  if (viewMode === "classes") {
    vis = [];
    for (let k = 0; k < C; k++) { vis.push(classOf(k)); }
    shown = [];
    dispNbr = new Map();
    vis.forEach(function (e) { dispNbr.set(e, new Set()); });
    CLINKS.forEach(function (l) {
      const s = classOf(l.s), t = classOf(l.t);
      if (s === t) { return; }
      shown.push({ s: s, t: t, c: 1, k: l.k, l: l.l });
      dispNbr.get(s).add(t);
      dispNbr.get(t).add(s);
    });
    topVis = new Set(vis);
    hover = -1;
    tooltip.hidden = true;
    vis.forEach(function (e) { measureNode(ents[e]); });
    if (layoutMode === "layers") { layoutLayers(); }
    autoFit = true;
    needsDraw = true;
    return;
  }
  if (focusSet !== null) {
    vis = Array.from(focusSet).sort(function (a, b) { return a - b; });
    shown = [];
    dispNbr = new Map();
    vis.forEach(function (e) { dispNbr.set(e, new Set()); });
    links.forEach(function (l) {
      if (l.s !== l.t && focusSet.has(l.s) && focusSet.has(l.t)) {
        shown.push({ s: l.s, t: l.t, c: l.c });
        dispNbr.get(l.s).add(l.t);
        dispNbr.get(l.t).add(l.s);
      }
    });
    topVis = new Set(vis);
    hover = -1;
    tooltip.hidden = true;
    vis.forEach(function (e) { measureNode(ents[e]); });
    if (layoutMode === "layers") { layoutLayers(); }
    rebuildTrail();   // entity mapping changed — re-derive which cards the trail lights up
    autoFit = true;
    needsDraw = true;
    return;
  }
  vis = [];
  for (let m = 0; m < M; m++) {
    const fns = fnsOf[m];
    if (!fns.length) { continue; }
    if (expanded.has(m)) {
      Array.prototype.push.apply(vis, fns);
      ents[superOf(m)].hcount = 0;
      continue;
    }
    let hidden = 0;
    fns.forEach(function (i) {
      if (revealed.has(i)) { vis.push(i); } else { hidden++; }
    });
    ents[superOf(m)].hcount = hidden;
    if (hidden) { vis.push(superOf(m)); }
  }
  const agg = new Map();
  links.forEach(function (l) {
    const s = place(l.s), t = place(l.t);
    if (s === t) { return; }
    agg.set(s * (N + M) + t, (agg.get(s * (N + M) + t) || 0) + l.c);
  });
  shown = [];
  dispNbr = new Map();
  vis.forEach(function (e) { dispNbr.set(e, new Set()); });
  agg.forEach(function (c, key) {
    const t = key % (N + M);
    const s = (key - t) / (N + M);
    shown.push({ s: s, t: t, c: c });
    dispNbr.get(s).add(t);
    dispNbr.get(t).add(s);
  });
  const fns = vis.filter(function (e) { return ents[e].type === "fn"; });
  fns.sort(function (a, b) { return (ents[b].din + ents[b].dout) - (ents[a].din + ents[a].dout); });
  topVis = new Set(fns.slice(0, 15));
  hover = -1;
  tooltip.hidden = true;
  vis.forEach(function (e) { measureNode(ents[e]); });
  refreshLegend();
  if (layoutMode === "layers") { layoutLayers(); }
  rebuildTrail();
  needsDraw = true;
}

// deterministic top-down view: roots (no visible callers) on top, calls flow downward
function layoutLayers() {
  if (!vis.length) { return; }
  const idxOf = new Map();
  vis.forEach(function (e, k) { idxOf.set(e, k); });
  const outs = vis.map(function () { return []; });
  const indeg = vis.map(function () { return 0; });
  shown.forEach(function (l) {
    const a = idxOf.get(l.s), b = idxOf.get(l.t);
    if (a === undefined || b === undefined || a === b) { return; }
    outs[a].push(b);
    indeg[b]++;
  });
  const layer = new Array(vis.length).fill(0);
  const queue = [];
  indeg.forEach(function (d, k) { if (d === 0) { queue.push(k); } });
  let qi = 0;
  const seen = new Array(vis.length).fill(false);
  while (qi < queue.length) {
    const k = queue[qi++];
    seen[k] = true;
    outs[k].forEach(function (b) {
      layer[b] = Math.max(layer[b], layer[k] + 1);
      if (--indeg[b] === 0) { queue.push(b); }
    });
  }
  for (let k = 0; k < vis.length; k++) {
    if (!seen[k] && layer[k] === 0) { layer[k] = 1; }  // cycle members: below the roots at least
  }
  const byLayer = new Map();
  vis.forEach(function (e, k) {
    if (!byLayer.has(layer[k])) { byLayer.set(layer[k], []); }
    byLayer.get(layer[k]).push(e);
  });
  Array.from(byLayer.keys()).sort(function (a, b) { return a - b; }).forEach(function (level) {
    const row = byLayer.get(level);
    row.sort(function (a, b) { return ents[a].id < ents[b].id ? -1 : 1; });
    let width = 0;                                   // pack each row by real card widths
    row.forEach(function (e) { measureNode(ents[e]); width += ents[e]._w + PAD_X; });
    let cursor = -width / 2;
    row.forEach(function (e) {
      const n = ents[e];
      n.x = cursor + n._w / 2;
      cursor += n._w + PAD_X;
      n.y = level * 128;
      n.vx = 0; n.vy = 0;
    });
  });
  autoFit = true;
  needsDraw = true;
}

function expandModule(m, deferRebuild) {
  if (expanded.has(m) || !fnsOf[m].length) { return; }
  const sup = ents[superOf(m)];
  const ring = 90 + 34 * Math.sqrt(fnsOf[m].length);  // cards need a wide ring, not a tight one
  fnsOf[m].forEach(function (i, k) {
    const e = ents[i];
    const ang = 2 * Math.PI * k / fnsOf[m].length;
    e.x = sup.x + ring * 1.5 * Math.cos(ang);
    e.y = sup.y + ring * 0.7 * Math.sin(ang);
    e.vx = 0; e.vy = 0;
  });
  expanded.add(m);
  if (!deferRebuild) { alpha = Math.max(alpha, 0.5); rebuild(); }
}
function collapseCore(m) {
  const list = fnsOf[m];
  const sup = ents[superOf(m)];
  let sx = 0, sy = 0;
  list.forEach(function (i) { sx += ents[i].x; sy += ents[i].y; });
  sup.x = sx / list.length;
  sup.y = sy / list.length;
  sup.vx = 0; sup.vy = 0;
  expanded.delete(m);
}
function collapseModule(m) {
  if (!expanded.has(m)) { return; }
  collapseCore(m);
  alpha = Math.max(alpha, 0.5);
  rebuild();
}
function expandAll() {
  for (let m = 0; m < M; m++) { expandModule(m, true); }
  alpha = 1;
  rebuild();
}
function collapseAll() {
  for (let m = 0; m < M; m++) { if (expanded.has(m)) { collapseCore(m); } }
  revealed.clear();
  alpha = 1;
  rebuild();
}

function ensureVisible(i) {
  if (fnVisible(i)) { return; }
  const sup = ents[superOf(ents[i].m)];
  ents[i].x = sup.x + 120;
  ents[i].y = sup.y + 50;
  ents[i].vx = 0; ents[i].vy = 0;
  revealed.add(i);
}
function revealCallees(i) {
  const src = ents[i];
  const targets = [];
  rawOut[i].forEach(function (t) { if (!fnVisible(t)) { targets.push(t); } });
  targets.sort(function (a, b) { return a - b; });
  targets.forEach(function (t, k) {
    const ang = 2 * Math.PI * k / targets.length;
    ents[t].x = src.x + 300 * Math.cos(ang);   // callees land in a wide ellipse: no instant pile-up
    ents[t].y = src.y + 150 * Math.sin(ang);
    ents[t].vx = 0; ents[t].vy = 0;
    revealed.add(t);
  });
}

function clickEntity(e, mx, my) {
  const ent = ents[e];
  if (ent.type === "cls") { clickClassRow(ent, e, my); return; }
  if (ent.type === "mod") { expandModule(ent.m); return; }
  if (ent.kind === "external") { return; }
  openFlow(ent.idx);
}

// Clicking a method row jumps to its flow diagram; a property whose type is another
// class jumps to that class. This is what ties the two views together.
function clickClassRow(n, e, my) {
  selected = e;
  const w = worldOf(0, my);
  const row = Math.floor((w.y - (n.y - n._h / 2) - n._head) / CLS_ROW);
  const hit = row >= 0 && row < n._rows.length ? n._rows[row] : null;
  openClassPanel(n.idx);                       // the card opens its expandable structure
  if (hit && hit.kind === "method" && idToIdx.has(hit.id)) {
    openMethodFlow(idToIdx.get(hit.id));       // ...or straight to that method, class kept as a crumb
  } else if (hit && hit.kind === "field" && hit.ref >= 0) {
    clsOpen.add("/" + row);                    // card rows start at the fields, matching the panel's keys
    renderClassPanel();
  }
  needsDraw = true;
}
function centerOn(e) {
  const n = ents[e];
  const availW = panel.hidden ? W : W * 0.43;
  tx = availW / 2 - n.x * scale;
  ty = H / 2 - n.y * scale;
  needsDraw = true;
}
function syncTabs() {
  document.querySelectorAll(".vtab").forEach(function (b) {
    b.classList.toggle("on", b.getAttribute("data-view") === viewMode);
  });
  legend.classList.toggle("hidden", viewMode === "classes");
  legendRestore.hidden = viewMode !== "classes";
  stepper.classList.toggle("on", viewMode === "calls" && !!(data.events && data.events.length));
}

// ------------------------------------------------------- trace-focus mode
function addFocus(e, near) {
  if (focusSet.has(e)) { return; }
  const n = ents[e];
  const k = focusSet.size + 1;
  n.x = near.x + 300 * Math.cos(k * 2.4);
  n.y = near.y + 160 * Math.sin(k * 2.4);
  focusSet.add(e);
}
function enterFocus(i) {
  if (focusSet === null) {
    savedView = { expanded: new Set(expanded), revealed: new Set(revealed) };
    focusSet = new Set();
    legend.classList.add("hidden");
    legendRestore.hidden = false;
  }
  addFocus(i, ents[i]);
  rawOut[i].forEach(function (t) { addFocus(t, ents[i]); });
  rawIn[i].forEach(function (t) { addFocus(t, ents[i]); });
  focusDim = new Set();
  rawIn[i].forEach(function (t) {
    if (!rawOut[i].has(t) && t !== i) { focusDim.add(t); }  // pure callers: context, drawn faded
  });
}
function recomputeFocus() {
  // rebuild the focus from the root plus whatever is still inlined, so collapsing
  // a call retracts the nodes it brought in
  if (focusSet === null || curRoot < 0) { return; }
  focusSet = new Set();
  focusDim = new Set();
  const roots = [curRoot];
  inlineOpen.forEach(function (key) {
    const idx = parseInt(key.slice(key.lastIndexOf("@") + 1), 10);
    if (!isNaN(idx)) { roots.push(idx); }
  });
  roots.forEach(function (r) {
    addFocus(r, ents[r]);
    rawOut[r].forEach(function (t) { addFocus(t, ents[r]); });
  });
  rawIn[curRoot].forEach(function (t) {
    addFocus(t, ents[curRoot]);
    if (!rawOut[curRoot].has(t) && t !== curRoot) { focusDim.add(t); }
  });
}
function exitFocus() {
  if (focusSet === null) { return; }
  focusSet = null;
  focusDim = new Set();
  expanded.clear();
  savedView.expanded.forEach(function (m) { expanded.add(m); });
  revealed.clear();
  savedView.revealed.forEach(function (i) { revealed.add(i); });
  savedView = null;
  legend.classList.remove("hidden");
  legendRestore.hidden = true;
  alpha = Math.max(alpha, 0.5);
  rebuild();
}
function fitView() {
  if (!vis.length) { return; }
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  vis.forEach(function (e) {
    const n = ents[e];
    minX = Math.min(minX, n.x); maxX = Math.max(maxX, n.x);
    minY = Math.min(minY, n.y); maxY = Math.max(maxY, n.y);
  });
  vis.forEach(function (e) {                       // include the cards, not just their centres
    const n = ents[e];
    minX = Math.min(minX, n.x - n._w / 2); maxX = Math.max(maxX, n.x + n._w / 2);
    minY = Math.min(minY, n.y - n._h / 2); maxY = Math.max(maxY, n.y + n._h / 2);
  });
  const availW = panel.hidden ? W : W * 0.43;
  const availH = H - 110;                          // top bar + stepper
  const bw = maxX - minX + 90;
  const bh = maxY - minY + 90;
  scale = Math.max(0.12, Math.min(1.25, Math.min(availW / bw, availH / bh)));
  tx = availW / 2 - ((minX + maxX) / 2) * scale;
  ty = 48 + availH / 2 - ((minY + maxY) / 2) * scale;
  needsDraw = true;
}

// ------------------------------------------------------------ force layout
function resize() {
  W = window.innerWidth; H = window.innerHeight;
  canvas.width = W * dpr; canvas.height = H * dpr;
  canvas.style.width = W + "px"; canvas.style.height = H + "px";
  needsDraw = true;
}

// The layout works on card rectangles, not points: repulsion is scaled by how much
// room a card actually occupies, and a hard collision pass guarantees no two cards
// ever overlap — so every label stays readable no matter how dense the graph is.
const REP = 260, SPRING = 0.055, GRAV = 0.006, DAMP = 0.86;
const PAD_X = 26, PAD_Y = 16;

function tick() {
  const a = alpha, K = vis.length;
  for (let ii = 0; ii < K; ii++) {
    const ni = ents[vis[ii]];
    for (let jj = ii + 1; jj < K; jj++) {
      const nj = ents[vis[jj]];
      let dx = ni.x - nj.x, dy = ni.y - nj.y;
      let d2 = dx * dx + dy * dy;
      if (d2 < 1) { dx = Math.random() - 0.5; dy = Math.random() - 0.5; d2 = dx * dx + dy * dy + 0.01; }
      const d = Math.sqrt(d2);
      const span = (ni._w + nj._w) / 2 + PAD_X;      // how far apart these two need to be
      const f = (REP * a * span) / Math.max(d2, 400);
      // wide, short cards: push sideways harder than vertically, so rows form naturally
      ni.vx += (dx / d) * f; ni.vy += (dy / d) * f * 0.55;
      nj.vx -= (dx / d) * f; nj.vy -= (dy / d) * f * 0.55;
    }
  }
  for (let k = 0; k < shown.length; k++) {
    const s = ents[shown[k].s], t = ents[shown[k].t];
    const dx = t.x - s.x, dy = t.y - s.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const rest = (s._w + t._w) / 2 + (s._h + t._h) / 4 + (viewMode === "classes" ? 90 : 70);
    const f = SPRING * (d - rest) * a;
    const fx = (dx / d) * f, fy = (dy / d) * f;
    s.vx += fx; s.vy += fy; t.vx -= fx; t.vy -= fy;
  }
  for (let ii = 0; ii < K; ii++) {
    const n = ents[vis[ii]];
    n.vx -= n.x * GRAV * a; n.vy -= n.y * GRAV * a * 1.6;  // keep the field wide, not tall
    if (n === dragNode) { n.vx = 0; n.vy = 0; continue; }
    n.vx *= DAMP; n.vy *= DAMP;
    n.x += n.vx; n.y += n.vy;
  }
  separate(2);
}

function separate(passes) {
  const padX = viewMode === "classes" ? 56 : PAD_X;   // ER cards need breathing room for edge labels
  const padY = viewMode === "classes" ? 40 : PAD_Y;
  for (let p = 0; p < passes; p++) {
    let moved = false;
    for (let ii = 0; ii < vis.length; ii++) {
      const a = ents[vis[ii]];
      for (let jj = ii + 1; jj < vis.length; jj++) {
        const b = ents[vis[jj]];
        const dx = b.x - a.x, dy = b.y - a.y;
        const ox = (a._w + b._w) / 2 + padX - Math.abs(dx);
        const oy = (a._h + b._h) / 2 + padY - Math.abs(dy);
        if (ox <= 0 || oy <= 0) { continue; }
        moved = true;
        if (ox / (a._w + b._w) < oy / (a._h + b._h)) {   // separate along the shallower overlap
          const s = (dx < 0 ? -1 : 1) * ox / 2;
          if (a !== dragNode) { a.x -= s; }
          if (b !== dragNode) { b.x += s; }
        } else {
          const s = (dy < 0 ? -1 : 1) * oy / 2;
          if (a !== dragNode) { a.y -= s; }
          if (b !== dragNode) { b.y += s; }
        }
      }
    }
    if (!moved) { return; }
  }
}

// Categorical slots in fixed documented order (dark steps), never generated or cycled:
// past the 8th module everything folds into one neutral "other" — color is a grouping
// aid here, the always-visible label carries identity.
const SLOTS = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"];
const OTHER = "#7c8598";
const MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace';
const STEREO = { enum: "#c98500", dataclass: "#199e70", struct: "#9085e9", abstract: "#d55181" };
const moduleRank = new Map();
data.modules
  .map(function (name, m) { return { m: m, n: fnsOf[m] ? fnsOf[m].length : 0, name: name }; })
  .filter(function (r) { return r.name !== "(external)"; })
  .sort(function (a, b) { return b.n - a.n || (a.name < b.name ? -1 : 1); })
  .forEach(function (r, k) { if (k < SLOTS.length) { moduleRank.set(r.m, k); } });

function colorOf(m) {
  if (typeof m === "string") {                     // class nodes carry a module NAME, not an index
    const k = classModules.indexOf(m);
    return k < 0 ? OTHER : SLOTS[k % SLOTS.length];
  }
  const slot = moduleRank.get(m);
  return slot === undefined ? OTHER : SLOTS[slot];
}
function dimf(e) { return hover >= 0 && e !== hover && !dispNbr.get(hover).has(e); }

// "pkg.comm.client:connect" -> "connect"; the module pseudo-node -> "client (module)",
// so import-time nodes never render as a bare, identical "<module>".
function prettyId(id) {
  const cut = id.indexOf(":");
  if (cut < 0) { return id; }
  const qual = id.slice(cut + 1);
  if (qual === "<module>") { return id.slice(0, cut).split(".").pop() + " (module)"; }
  return qual;
}
function labelOf(n) {
  if (n.type === "mod") { return n.id.split(".").pop(); }
  return prettyId(n.id);
}
const CLS_ROW = 24, CLS_HEAD = 38, CLS_SUB = 16, CLS_MAX_ROWS = 30, CLS_PADX = 17;

function measureNode(n) {
  if (n._w) { return; }
  if (n.type === "cls") { return measureClass(n); }
  const label = labelOf(n);
  ctx.font = n.type === "mod" ? "600 12px system-ui, sans-serif" : "12px system-ui, sans-serif";
  const text = ctx.measureText(label).width;
  n._label = label;
  n._w = Math.max(58, Math.min(230, text + (n.type === "mod" ? 46 : 26)));
  n._h = n.type === "mod" ? 30 : 24;
}

function clipText(text, maxW) {
  if (!text || ctx.measureText(text).width <= maxW) { return text; }
  let lo = 1, hi = text.length;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (ctx.measureText(text.slice(0, mid) + "…").width <= maxW) { lo = mid; } else { hi = mid - 1; }
  }
  return text.slice(0, lo) + "…";
}

// An ER-style entity card: header (name + stereotype), then one row per property with
// the name on the left and its type right-aligned, then the methods below a divider.
function measureClass(n) {
  const rows = [];
  n.fields.forEach(function (f) {
    rows.push({ left: f[0], right: f[1] || (f[3] ? "= " + f[3] : ""), ref: f[2], kind: "field" });
  });
  n.meth.forEach(function (m) { rows.push({ left: m[0] + "()", right: "", id: m[1], kind: "method" }); });
  n._rows = rows.slice(0, CLS_MAX_ROWS);
  n._more = rows.length - n._rows.length;
  n._fields = Math.min(n.fields.length, n._rows.length);  // where the divider goes
  n._label = n.name;

  ctx.font = "600 13.5px system-ui, sans-serif";
  let headW = ctx.measureText(n.name).width + CLS_PADX * 2 + 8;
  if (n.st) {
    ctx.font = "10.5px system-ui, sans-serif";
    headW += ctx.measureText("«" + n.st + "»").width + 18;
  }
  n._sub = n.bases && n.bases.length ? ": " + n.bases.join(", ") : "";   // what it inherits
  if (n._sub) {
    ctx.font = "11px " + MONO;
    headW = Math.max(headW, ctx.measureText(n._sub).width + CLS_PADX * 2);
  }
  ctx.font = "12.5px " + MONO;
  let lw = 0, rw = 0;
  n._rows.forEach(function (r) {
    lw = Math.max(lw, ctx.measureText(r.left).width);
    rw = Math.max(rw, ctx.measureText(r.right).width);
  });
  n._rw = rw;
  n._head = CLS_HEAD + (n._sub ? CLS_SUB : 0);
  n._w = Math.max(210, Math.min(520, Math.max(headW, lw + rw + (rw ? 34 : 0) + CLS_PADX * 2)));
  n._h = n._head + n._rows.length * CLS_ROW + (n._more > 0 ? CLS_ROW : 0) + 14;
}
function roundRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
function edgePoint(n, tx2, ty2) {
  // where a line toward (tx2,ty2) leaves this node's card
  const hw = n._w / 2 + 2, hh = n._h / 2 + 2;
  const dx = tx2 - n.x, dy = ty2 - n.y;
  if (!dx && !dy) { return { x: n.x, y: n.y }; }
  const sx = dx === 0 ? Infinity : hw / Math.abs(dx);
  const sy = dy === 0 ? Infinity : hh / Math.abs(dy);
  const s = Math.min(sx, sy);
  return { x: n.x + dx * s, y: n.y + dy * s };
}

function drawEdge(s, t, color, width, dashed) {
  const a = edgePoint(s, t.x, t.y);
  const b = edgePoint(t, s.x, s.y);
  const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
  const dx = b.x - a.x, dy = b.y - a.y;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;
  const bow = Math.min(26, len * 0.14);            // gentle arc: parallel edges stay distinguishable
  const cx = mx - (dy / len) * bow, cy = my + (dx / len) * bow;
  ctx.strokeStyle = color;
  ctx.lineWidth = width / scale;
  if (dashed) { ctx.setLineDash([5 / scale, 4 / scale]); }
  ctx.beginPath();
  ctx.moveTo(a.x, a.y);
  ctx.quadraticCurveTo(cx, cy, b.x, b.y);
  ctx.stroke();
  ctx.setLineDash([]);
  const ang = Math.atan2(b.y - cy, b.x - cx);      // arrowhead follows the curve's final tangent
  const size = Math.min(9, 5 + width) / scale;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(b.x, b.y);
  ctx.lineTo(b.x - size * Math.cos(ang - 0.42), b.y - size * Math.sin(ang - 0.42));
  ctx.lineTo(b.x - size * Math.cos(ang + 0.42), b.y - size * Math.sin(ang + 0.42));
  ctx.closePath();
  ctx.fill();
}

function drawClass(n, e) {
  const x = n.x - n._w / 2, y = n.y - n._h / 2;
  const accent = n.st ? (STEREO[n.st] || colorOf(n.m)) : colorOf(n.m);
  ctx.globalAlpha = dimf(e) ? 0.16 : 1;

  if (e === selected) { ctx.shadowColor = "rgba(57,135,229,0.5)"; ctx.shadowBlur = 18; }
  roundRect(x, y, n._w, n._h, 9);
  ctx.fillStyle = "#171b23";
  ctx.fill();
  ctx.shadowBlur = 0;

  ctx.save();                                   // header band in the class's accent colour
  roundRect(x, y, n._w, n._h, 9);
  ctx.clip();
  ctx.fillStyle = accent;
  ctx.globalAlpha = ctx.globalAlpha * 0.2;
  ctx.fillRect(x, y, n._w, n._head);
  ctx.restore();

  roundRect(x, y, n._w, n._h, 9);
  ctx.strokeStyle = e === selected ? "#5aa0ee" : (e === hover ? "rgba(255,255,255,0.7)" : accent);
  ctx.lineWidth = (e === selected || e === hover ? 2 : 1.1) / scale;
  ctx.stroke();

  ctx.beginPath();                              // rule under the header
  ctx.moveTo(x, y + n._head);
  ctx.lineTo(x + n._w, y + n._head);
  ctx.strokeStyle = "rgba(255,255,255,0.12)";
  ctx.lineWidth = 1 / scale;
  ctx.stroke();

  ctx.font = "600 13.5px system-ui, sans-serif";
  ctx.fillStyle = "#f0f4fa";
  ctx.fillText(n.name, x + CLS_PADX, y + CLS_HEAD / 2);
  if (n.st) {
    ctx.font = "10.5px system-ui, sans-serif";
    ctx.fillStyle = accent;
    const tag = "«" + n.st + "»";
    ctx.fillText(tag, x + n._w - ctx.measureText(tag).width - CLS_PADX, y + CLS_HEAD / 2);
  }
  if (n._sub) {                                 // inherited types, right under the name
    ctx.font = "11px " + MONO;
    ctx.fillStyle = "#93b8a8";
    ctx.fillText(clipText(n._sub, n._w - CLS_PADX * 2), x + CLS_PADX, y + CLS_HEAD + CLS_SUB / 2 - 4);
  }

  let ry = y + n._head + CLS_ROW / 2 + 5;
  ctx.font = "12.5px " + MONO;
  const rightX = x + n._w - CLS_PADX;
  const leftMax = n._w - CLS_PADX * 2 - (n._rw ? n._rw + 34 : 0);
  n._rows.forEach(function (r, k) {
    if (k === n._fields && k > 0 && n._more <= 0) {   // divider between properties and methods
      ctx.beginPath();
      ctx.moveTo(x + 8, ry - CLS_ROW / 2 - 1);
      ctx.lineTo(x + n._w - 8, ry - CLS_ROW / 2 - 1);
      ctx.strokeStyle = "rgba(255,255,255,0.08)";
      ctx.lineWidth = 1 / scale;
      ctx.stroke();
    }
    ctx.fillStyle = r.kind === "method" ? "#7cb4f0" : "#d5dce8";
    ctx.fillText(clipText(r.left, leftMax), x + CLS_PADX, ry);
    if (r.right) {
      ctx.fillStyle = r.ref >= 0 ? "#8fd0b4" : "#8c95a8";   // a type that is itself a class stands out
      const t = clipText(r.right, n._rw);
      ctx.fillText(t, rightX - ctx.measureText(t).width, ry);
    }
    ry += CLS_ROW;
  });
  if (n._more > 0) {
    ctx.fillStyle = "#6d7789";
    ctx.fillText("+" + n._more + " more", x + CLS_PADX, ry);
  }
  ctx.globalAlpha = 1;
}

function draw() {
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = "#0d0f13";
  ctx.fillRect(0, 0, W, H);
  ctx.translate(tx, ty);
  ctx.scale(scale, scale);
  vis.forEach(function (e) { measureNode(ents[e]); });

  for (let k = 0; k < shown.length; k++) {
    const l = shown[k];
    const lit = hover >= 0 && (l.s === hover || l.t === hover);
    const dim = dimf(l.s) || dimf(l.t);
    let color = lit ? "rgba(190,214,255,0.72)" : (dim ? "rgba(150,163,190,0.05)" : "rgba(150,163,190,0.2)");
    if (l.k === "inherits") { color = lit ? "#8fd0b4" : (dim ? "rgba(25,158,112,0.12)" : "rgba(25,158,112,0.55)"); }
    drawEdge(ents[l.s], ents[l.t], color, lit ? 1.8 : 1 + Math.min(1.4, Math.log(l.c + 1) * 0.4),
             l.k === "inherits");
    if (l.l && !dim && scale > 0.5) {              // property name on the "has" edge
      const s = ents[l.s], t = ents[l.t];
      ctx.font = (10 / scale) + "px " + MONO;
      ctx.fillStyle = lit ? "#dfe6f2" : "rgba(163,173,191,0.75)";
      ctx.textAlign = "center";
      ctx.fillText(l.l, (s.x + t.x) / 2, (s.y + t.y) / 2 - 4 / scale);
      ctx.textAlign = "left";
    }
  }

  for (let k = 0; k < trailEdges.length; k++) {   // history: oldest first, newest paints on top
    const tr = trailEdges[k];
    if (!dispNbr.has(tr.s) || !dispNbr.has(tr.t)) { continue; }
    ctx.globalAlpha = tr.a;
    drawEdge(ents[tr.s], ents[tr.t], "#e0b341", 1.2 + 1.4 * tr.a, false);
    ctx.globalAlpha = 1;
  }

  ctx.textBaseline = "middle";
  for (let ii = 0; ii < vis.length; ii++) {
    const e = vis[ii];
    const n = ents[e];
    if (n.type === "cls") { drawClass(n, e); continue; }
    const isMod = n.type === "mod";
    const color = colorOf(n.m);
    const x = n.x - n._w / 2, y = n.y - n._h / 2;
    ctx.globalAlpha = dimf(e) ? 0.16 : (focusSet !== null && focusDim.has(e) ? 0.45 : 1);

    const heat = pulses.get(e) || 0;                // 1 = most recent call, fading with age
    if (e === selected || heat > 0.6) {             // soft glow only on the newest / selected card
      ctx.shadowColor = heat > 0.6 ? "rgba(224,179,65,0.6)" : "rgba(57,135,229,0.55)";
      ctx.shadowBlur = 18;
    }
    roundRect(x, y, n._w, n._h, isMod ? 9 : 7);
    ctx.fillStyle = isMod ? "#1c212b" : "#191d25";
    ctx.fill();
    ctx.shadowBlur = 0;

    ctx.save();                                      // module color: a left accent, not the whole fill
    roundRect(x, y, n._w, n._h, isMod ? 9 : 7);
    ctx.clip();
    ctx.fillStyle = color;
    ctx.globalAlpha = ctx.globalAlpha * (isMod ? 0.24 : 1);
    ctx.fillRect(x, y, isMod ? n._w : 3.5, n._h);
    ctx.restore();

    roundRect(x, y, n._w, n._h, isMod ? 9 : 7);
    if (e === selected) { ctx.strokeStyle = "#5aa0ee"; ctx.lineWidth = 2 / scale; }
    else if (e === hover) { ctx.strokeStyle = "rgba(255,255,255,0.75)"; ctx.lineWidth = 1.5 / scale; }
    else if (isMod) { ctx.strokeStyle = color; ctx.lineWidth = 1.2 / scale; }
    else { ctx.strokeStyle = "rgba(255,255,255,0.12)"; ctx.lineWidth = 1 / scale; }
    ctx.stroke();

    if (heat > 0) {
      ctx.globalAlpha = heat;
      roundRect(x - 4, y - 4, n._w + 8, n._h + 8, isMod ? 12 : 10);
      ctx.strokeStyle = "#e0b341";
      ctx.lineWidth = (1 + 1.4 * heat) / scale;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    if (scale > 0.34 || isMod || e === hover || e === selected) {
      ctx.font = isMod ? "600 12px system-ui, sans-serif" : "12px system-ui, sans-serif";
      ctx.fillStyle = isMod ? "#f0f4fa" : "#e9edf4";
      ctx.fillText(n._label, x + (isMod ? 11 : 11), n.y);
      if (isMod) {
        ctx.font = "11px system-ui, sans-serif";
        ctx.fillStyle = "rgba(255,255,255,0.55)";
        const badge = String(n.hcount);
        ctx.fillText(badge, x + n._w - ctx.measureText(badge).width - 10, n.y);
      }
    }
  }
  ctx.globalAlpha = 1;
}

// -------------------------------------------------- step-through debugger
// Walks the call sequence one call at a time: play at a readable pace, or
// step manually. Each step names the call and holds the highlight until the
// next one, so you can actually read where you are.
const replay = { on: false, i: 0, last: 0, revealed: 0, delay: 900 };
// History trail: the last TRAIL_MAX calls stay lit, brightest = most recent.
const TRAIL_MAX = 5;
const TRAIL_ALPHA = [1, 0.66, 0.44, 0.28, 0.17];
let trailEdges = [];          // [{s, t, a}] oldest first, so the newest draws on top
let pulses = new Map();       // entity -> alpha (max over the trail)
const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function rebuildTrail() {
  trailEdges = [];
  pulses = new Map();
  if (!data.events || !data.events.length) { return; }
  const place2 = function (e) { return (focusSet !== null || fnVisible(e)) ? e : superOf(ents[e].m); };
  const entries = [];
  for (let k = 0; k < TRAIL_MAX; k++) {
    const idx = replay.i - 1 - k;                 // derived from position, so stepping back works
    if (idx < 0) { break; }
    const ev = data.events[idx];
    const s = place2(ev[0]), t = place2(ev[1]);
    const a = TRAIL_ALPHA[k];
    entries.push({ s: s, t: t, a: a });
    pulses.set(t, Math.max(pulses.get(t) || 0, a));
    pulses.set(s, Math.max(pulses.get(s) || 0, a * 0.55));
  }
  trailEdges = entries.reverse();
}
const stepper = document.getElementById("stepper");
const stNow = document.getElementById("st-now");
const stPos = document.getElementById("st-pos");
const stPlay = document.getElementById("st-play");

function argHint(idx) {
  const n = data.nodes[idx];
  const src = (n.dyn && n.dyn.s && n.dyn.s.length) ? n.dyn.s[0].args : null;
  if (src) {
    return "(" + Object.keys(src).map(function (k) { return k + "=" + src[k]; }).join(", ") + ")";
  }
  if (n.sim && n.sim.a) {
    const bits = Object.keys(n.sim.a).map(function (k) {
      const s = n.sim.a[k];
      if (s.v && s.v.length) { return k + "=" + s.v[0]; }
      return s.t && s.t.length ? k + ": " + s.t[0] : k;
    });
    if (bits.length) { return "(" + bits.join(", ") + ")"; }
  }
  return "()";
}
function shortId(idx) {
  return prettyId(data.nodes[idx].id);
}
function describeStep(ev) {
  return shortId(ev[0]) + "  →  " + shortId(ev[1]) + argHint(ev[1]);
}
function refreshStepper() {
  if (!data.events || !data.events.length) { return; }
  stPos.textContent = replay.i + " / " + data.events.length;
  stPlay.textContent = replay.on ? "⏸ Pause" : "▶ Play";
}
function applyStep(delta) {
  const events = data.events;
  if (!events.length) { return; }
  const next = replay.i + delta;
  if (next < 0 || next > events.length) { return; }
  replay.i = next;
  if (next === 0) {
    rebuildTrail();
    stNow.textContent = "at the start of the call sequence";
    renderHistory();
    refreshStepper();
    needsDraw = true;
    return;
  }
  const ev = events[next - 1];
  let changed = false;
  [ev[0], ev[1]].forEach(function (e) {
    if (focusSet !== null) {
      if (!focusSet.has(e)) { addFocus(e, ents[selected >= 0 ? selected : e]); changed = true; }
    } else if (!fnVisible(e) && replay.revealed < 200) {
      ensureVisible(e);
      replay.revealed++;
      changed = true;
    }
  });
  if (changed) { alpha = Math.max(alpha, 0.3); rebuild(); }
  rebuildTrail();
  stNow.innerHTML = "";
  stNow.appendChild(document.createTextNode(shortId(ev[0]) + "  →  "));
  const strong = document.createElement("b");
  strong.textContent = shortId(ev[1]) + argHint(ev[1]);
  stNow.appendChild(strong);
  renderHistory();
  refreshStepper();
  needsDraw = true;
}

function renderHistory() {
  const box = document.getElementById("st-hist");
  box.innerHTML = "";
  for (let k = TRAIL_MAX - 1; k >= 1; k--) {   // older calls above, fading upward
    const idx = replay.i - 1 - k;
    if (idx < 0) { continue; }
    const ev = data.events[idx];
    const row = document.createElement("div");
    row.className = "hrow";
    row.style.opacity = String(TRAIL_ALPHA[k]);
    row.textContent = shortId(ev[0]) + " → " + shortId(ev[1]);
    row.title = "step " + (idx + 1);
    box.appendChild(row);
  }
  box.style.display = box.childElementCount ? "block" : "none";
}
function replayTick() {
  const now = performance.now();
  if (now - replay.last < replay.delay) { return; }
  replay.last = now;
  if (replay.i >= data.events.length) {
    replay.on = false;
    refreshStepper();
    return;
  }
  applyStep(1);
}
function frame() {
  if (replay.on) { replayTick(); }
  if (layoutMode === "layers") { alpha = 0; }
  if (alpha > 0.005) {
    tick();
    alpha *= 0.988;
    needsDraw = true;
  } else if (autoFit && !replay.on) {   // settled: frame the result so it fills the space
    autoFit = false;
    fitView();
  }
  if (needsDraw) { draw(); needsDraw = false; }
  requestAnimationFrame(frame);
}

function worldOf(mx, my) { return { x: (mx - tx) / scale, y: (my - ty) / scale }; }
function hitTest(mx, my) {
  const w = worldOf(mx, my);
  let best = -1, bestD = Infinity;
  for (let ii = vis.length - 1; ii >= 0; ii--) {
    const n = ents[vis[ii]];
    if (!n._w) { measureNode(n); }
    const dx = Math.abs(n.x - w.x), dy = Math.abs(n.y - w.y);
    if (dx <= n._w / 2 + 3 && dy <= n._h / 2 + 3 && dx + dy < bestD) { best = vis[ii]; bestD = dx + dy; }
  }
  return best;
}

canvas.addEventListener("mousedown", function (e) {
  downX = e.clientX; downY = e.clientY; downT = Date.now();
  downHit = hitTest(e.clientX, e.clientY);
  if (downHit >= 0) { dragNode = ents[downHit]; alpha = Math.max(alpha, 0.3); }
  else { panning = true; }
  lastX = e.clientX; lastY = e.clientY;
  canvas.classList.add("dragging");
});
window.addEventListener("mousemove", function (e) {
  if (dragNode) {
    const w = worldOf(e.clientX, e.clientY);
    dragNode.x = w.x; dragNode.y = w.y;
    alpha = Math.max(alpha, 0.3);
    needsDraw = true;
  } else if (panning) {
    tx += e.clientX - lastX; ty += e.clientY - lastY;
    lastX = e.clientX; lastY = e.clientY;
    needsDraw = true;
  } else if (e.target === canvas) {
    const hit = hitTest(e.clientX, e.clientY);
    if (hit !== hover) { hover = hit; needsDraw = true; }
    if (hover >= 0) {
      const n = ents[hover];
      let text;
      if (n.type === "cls") {
        text = n.id + "\n" + (n.file ? n.file + ":" + n.line : "");
        if (n.bases && n.bases.length) { text += "\ninherits " + n.bases.join(", "); }
        text += "\n" + n.fields.length + " propert" + (n.fields.length === 1 ? "y" : "ies") +
                " · " + n.meth.length + " method(s)";
        text += "\nclick a method to open its flow, a typed property to follow it";
      } else if (n.type === "mod") {
        const part = n.hcount < n.count ? n.hcount + " more function(s)" : n.count + " function(s)";
        text = n.id + "\n" + part + " · click to expand all of them";
      } else {
        text = n.id + "\n";
        text += (n.file ? n.file + ":" + n.line : "(external)") + "\n";
        text += n.kind + " · in " + n.din + " · out " + n.dout;
        if (n.depth !== null && n.depth !== undefined) { text += " · depth " + n.depth; }
        if (n.kind !== "external") { text += "\nclick for flow diagram"; }
      }
      tooltip.textContent = text;
      tooltip.hidden = false;
      tooltip.style.left = Math.min(e.clientX + 14, W - 300) + "px";
      tooltip.style.top = (e.clientY + 14) + "px";
    } else {
      tooltip.hidden = true;
    }
  }
});
window.addEventListener("mouseup", function (e) {
  const wasClick = downHit >= 0 && !panning
    && Math.abs(e.clientX - downX) < 5 && Math.abs(e.clientY - downY) < 5
    && Date.now() - downT < 500;
  dragNode = null; panning = false;
  canvas.classList.remove("dragging");
  if (wasClick) { clickEntity(downHit, e.clientX, e.clientY); }
  downHit = -1;
});
canvas.addEventListener("wheel", function (e) {
  e.preventDefault();
  const factor = Math.exp(-e.deltaY * 0.0015);
  const next = Math.min(8, Math.max(0.05, scale * factor));
  const wx = (e.clientX - tx) / scale, wy = (e.clientY - ty) / scale;
  scale = next;
  tx = e.clientX - wx * scale;
  ty = e.clientY - wy * scale;
  needsDraw = true;
}, { passive: false });
canvas.addEventListener("dblclick", function () { alpha = 1; });
window.addEventListener("keydown", function (e) { if (e.key === "Escape") { closePanel(); } });

// ----------------------------------------------------------------- legend
const legend = document.getElementById("legend");
const buttons = document.createElement("div");
buttons.className = "buttons";
const btnExpand = document.createElement("button");
btnExpand.textContent = "Expand all";
btnExpand.addEventListener("click", expandAll);
const btnCollapse = document.createElement("button");
btnCollapse.textContent = "Collapse all";
btnCollapse.addEventListener("click", collapseAll);
buttons.appendChild(btnExpand);
buttons.appendChild(btnCollapse);
const btnLayout = document.createElement("button");
btnLayout.textContent = "Top-down";
btnLayout.addEventListener("click", function () {
  layoutMode = layoutMode === "force" ? "layers" : "force";
  btnLayout.classList.toggle("on", layoutMode === "layers");
  btnLayout.textContent = layoutMode === "layers" ? "Force" : "Top-down";
  if (layoutMode === "layers") { layoutLayers(); fitView(); }
  else { alpha = 1; }
  needsDraw = true;
});
buttons.appendChild(btnLayout);
legend.appendChild(buttons);

if (data.events && data.events.length) {
  stepper.classList.add("on");
  stPlay.addEventListener("click", function () {
    replay.on = !replay.on;
    if (replay.on && replay.i >= data.events.length) { applyStep(-replay.i); }
    replay.last = 0;
    refreshStepper();
  });
  document.getElementById("st-fwd").addEventListener("click", function () {
    replay.on = false;
    applyStep(1);
  });
  document.getElementById("st-back").addEventListener("click", function () {
    replay.on = false;
    applyStep(-1);
  });
  document.getElementById("st-reset").addEventListener("click", function () {
    replay.on = false;
    replay.revealed = 0;
    applyStep(-replay.i);
  });
  document.getElementById("st-speed").addEventListener("input", function (e) {
    replay.delay = 1900 - parseInt(e.target.value, 10) * 180;  // 1720ms (slow) .. 100ms (fast)
  });
  window.addEventListener("keydown", function (e) {
    if (e.target && e.target.tagName === "INPUT") { return; }
    if (e.key === "ArrowRight") { replay.on = false; applyStep(1); }
    else if (e.key === "ArrowLeft") { replay.on = false; applyStep(-1); }
    else if (e.key === " ") { e.preventDefault(); stPlay.click(); }
  });
  refreshStepper();
}
const legendRestore = document.getElementById("legend-restore");
legendRestore.addEventListener("click", function () { legend.classList.toggle("hidden"); });

document.querySelectorAll(".vtab").forEach(function (btn) {
  btn.addEventListener("click", function () {
    const next = btn.getAttribute("data-view");
    if (next === viewMode) { return; }
    if (next === "classes" && !C) {
      document.getElementById("hud").textContent = "no classes found in this scope";
      return;
    }
    viewMode = next;
    if (viewMode === "classes" && !classesSeeded) {
      classesSeeded = true;                       // seed once; switching back keeps the layout
      CLASSES.forEach(function (c, k) {
        const n = ents[classOf(k)];
        const ang = 2 * Math.PI * k / Math.max(C, 1);
        n.x = 620 * Math.cos(ang); n.y = 340 * Math.sin(ang); n.vx = 0; n.vy = 0;
      });
      alpha = 1;
    }
    syncTabs();
    rebuild();
    refreshHud();
    if (viewMode === "calls" && curRoot >= 0) { openFlow(curRoot); }  // carry the open function over
  });
});

const entryPoints = (data.meta && data.meta.entry_points) || [];
if (entryPoints.length) {
  const head = document.createElement("div");
  head.className = "sect";
  head.textContent = "Entry points";
  legend.appendChild(head);
  entryPoints.slice(0, 8).forEach(function (ep) {
    const idx = idToIdx.get(ep.id);
    if (idx === undefined) { return; }
    const row = document.createElement("div");
    row.className = "eprow";
    const name = document.createElement("div");
    name.className = "ename";
    const badge = document.createElement("span");
    badge.className = "badge " + ep.kind;
    badge.textContent = ep.kind;
    name.appendChild(badge);
    name.appendChild(document.createTextNode(shortId(idx)));
    const why = document.createElement("div");
    why.className = "ewhy";
    why.textContent = ep.why;
    row.appendChild(name);
    row.appendChild(why);
    row.title = ep.id;
    row.addEventListener("click", function () { openFlow(idx); });
    legend.appendChild(row);
  });
}

const modHead = document.createElement("div");
modHead.className = "sect";
modHead.textContent = "Modules";
legend.appendChild(modHead);

const legendLabels = [];
data.modules.forEach(function (name, m) {
  const entry = document.createElement("div");
  entry.className = "entry collapsed";
  const sw = document.createElement("span");
  sw.className = "swatch";
  sw.style.background = colorOf(m);
  const label = document.createElement("span");
  label.className = "modname";
  const count = document.createElement("span");
  count.className = "count";
  count.textContent = fnsOf[m] ? fnsOf[m].length : 0;
  entry.appendChild(sw);
  entry.appendChild(label);
  entry.appendChild(count);
  entry.addEventListener("click", function () {
    if (expanded.has(m)) { collapseModule(m); } else { expandModule(m); }
  });
  const kids = document.createElement("div");
  kids.className = "kids";
  legend.appendChild(entry);
  legend.appendChild(kids);
  legendLabels.push({ entry: entry, label: label, kids: kids, name: name });
});
function refreshLegend() {
  legendLabels.forEach(function (item, m) {
    const open = expanded.has(m);
    item.label.textContent = (open ? "▾ " : "▸ ") + item.name;
    item.entry.classList.toggle("collapsed", !open);
    item.kids.innerHTML = "";
    const rows = open ? fnsOf[m] : fnsOf[m].filter(function (i) { return revealed.has(i); });
    rows.forEach(function (i) {
      const row = document.createElement("div");
      row.className = "fnrow";
      const id = ents[i].id;
      row.textContent = id.indexOf(":") >= 0 ? id.slice(id.indexOf(":") + 1) : id;
      row.title = id;
      row.addEventListener("click", function () { openFlow(i); });
      item.kids.appendChild(row);
    });
  });
}

// ------------------------------------------------------------- flow panel
const panel = document.getElementById("panel");
const crumbs = document.getElementById("crumbs");
const flowBox = document.getElementById("flow-box");
let flowStack = [];
let curModule = "";
let animOn = false;

document.getElementById("panel-close").addEventListener("click", closePanel);
const btnAnim = document.getElementById("anim-toggle");
btnAnim.addEventListener("click", function () {
  animOn = !animOn;
  btnAnim.classList.toggle("on", animOn);
  const svg = flowBox.querySelector("svg");
  if (svg) { svg.classList.toggle("anim", animOn); }
});

// drag-to-pan the diagram (a genuine click on a chip still toggles it)
const panelScroll = document.getElementById("panel-scroll");
let fDrag = null, fDragMoved = false;
panelScroll.addEventListener("mousedown", function (e) {
  fDrag = { x: e.clientX, y: e.clientY, sl: panelScroll.scrollLeft, st: panelScroll.scrollTop };
  fDragMoved = false;
  panelScroll.classList.add("grabbing");
  e.preventDefault();  // no text selection while panning
});
window.addEventListener("mousemove", function (e) {
  if (!fDrag) { return; }
  const dx = e.clientX - fDrag.x, dy = e.clientY - fDrag.y;
  if (Math.abs(dx) > 4 || Math.abs(dy) > 4) { fDragMoved = true; }
  panelScroll.scrollLeft = fDrag.sl - dx;
  panelScroll.scrollTop = fDrag.st - dy;
});
window.addEventListener("mouseup", function () {
  if (fDrag) { fDrag = null; panelScroll.classList.remove("grabbing"); }
});

// wheel zooms the diagram (anchored at the cursor); panning is drag-only
let fZoom = 1, fNatW = 0, fNatH = 0;
function applyFlowZoom() {
  const svg = flowBox.querySelector("svg");
  if (!svg) { return; }
  svg.setAttribute("width", fNatW * fZoom);
  svg.setAttribute("height", fNatH * fZoom);
}
panelScroll.addEventListener("wheel", function (e) {
  e.preventDefault();
  const prev = fZoom;
  fZoom = Math.min(3, Math.max(0.25, fZoom * Math.exp(-e.deltaY * 0.0015)));
  if (fZoom === prev) { return; }
  const rect = panelScroll.getBoundingClientRect();
  const k = fZoom / prev;
  const px = panelScroll.scrollLeft + (e.clientX - rect.left);
  const py = panelScroll.scrollTop + (e.clientY - rect.top);
  applyFlowZoom();
  panelScroll.scrollLeft = px * k - (e.clientX - rect.left);
  panelScroll.scrollTop = py * k - (e.clientY - rect.top);
}, { passive: false });

flowBox.addEventListener("click", function (e) {
  if (fDragMoved) { fDragMoved = false; return; }  // that was a pan, not a click
  if (!e.target.closest) { return; }

  const cls = e.target.closest("[data-ckey]");     // class panel: expand a nested class in place
  if (cls) {
    const key = cls.getAttribute("data-ckey");
    if (clsOpen.has(key)) { clsOpen.delete(key); } else { clsOpen.add(key); }
    renderClassPanel();
    return;
  }
  const fn = e.target.closest("[data-fn]");        // class panel: show a method's flow, in place
  const fnId = fn && fn.getAttribute("data-fn");
  if (fnId && idToIdx.has(fnId)) {
    openMethodFlow(idToIdx.get(fnId));
    return;
  }

  const chip = e.target.closest("[data-key]");
  if (!chip) { return; }
  const key = chip.getAttribute("data-key");
  const idx = parseInt(chip.getAttribute("data-target"), 10);
  if (inlineOpen.has(key)) {
    inlineOpen.delete(key);  // collapse the inlined implementation
    if (focusSet !== null) { recomputeFocus(); }  // ...and retract what it had revealed
    alpha = Math.max(alpha, 0.4);
    rebuild();
  } else {
    inlineOpen.add(key);
    if (focusSet !== null) { enterFocus(idx); }  // the trace on the left grows with the drill-down
    else { ensureVisible(idx); revealCallees(idx); }
    alpha = Math.max(alpha, 0.5);
    rebuild();
  }
  renderFlow(curRoot);
  needsDraw = true;
});

function openFlow(i) {
  flowStack = [i];  // each open starts a fresh trace — no stale crumb trails
  selected = i;
  enterFocus(i);    // left side shows only the system being traced
  alpha = Math.max(alpha, 0.5);
  rebuild();
  panel.hidden = false;
  fitView();
  renderCrumbs();
  renderFlow(i);
  needsDraw = true;
}
function closePanel() {
  flowStack = [];
  panel.hidden = true;
  selected = -1;
  curClass = -1;
  classOrigin = -1;
  exitFocus();
  needsDraw = true;
}
function jumpTo(k) {
  flowStack = flowStack.slice(0, k + 1);
  const i = flowStack[k];
  selected = i;
  renderCrumbs();
  renderFlow(i);
  needsDraw = true;
}
function renderCrumbs() {
  crumbs.innerHTML = "";
  if (classOrigin >= 0) {                    // came from a class card — offer the way back
    const back = document.createElement("span");
    back.className = "crumb";
    back.textContent = CLASSES[classOrigin].name;
    back.title = CLASSES[classOrigin].id;
    back.addEventListener("click", function () { openClassPanel(classOrigin); });
    crumbs.appendChild(back);
    const sep = document.createElement("span");
    sep.className = "sep";
    sep.textContent = "›";
    crumbs.appendChild(sep);
  }
  flowStack.forEach(function (i, k) {
    if (k) {
      const sep = document.createElement("span");
      sep.className = "sep";
      sep.textContent = "›";
      crumbs.appendChild(sep);
    }
    const s = document.createElement("span");
    s.className = "crumb" + (k === flowStack.length - 1 ? " here" : "");
    const id = data.nodes[i].id;
    s.textContent = prettyId(id);
    s.title = id;
    if (k < flowStack.length - 1) { s.addEventListener("click", function () { jumpTo(k); }); }
    crumbs.appendChild(s);
  });
}

// --- deterministic flowchart layout: normalize -> measure -> draw (SVG) ---
// Chips expand INLINE: clicking a call site splices the callee's flowchart into
// the current diagram (keyed by tree path, so re-renders are deterministic).
// FCW: measured width of one 12px ui-monospace char (slightly generous so text never overflows)
const FLH = 18, FVGAP = 26, FHGAP = 40, FMAXW = 1200, FCW = 7.4, ELCW = 6.4, INLINE_MAX_DEPTH = 6;
const BR_GAP = 46;   // diamond -> branch tops: room for a branch label above each elbow
let curRoot = -1;
let inlineOpen = new Set();

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function fit(label, w) {
  const max = Math.max(4, Math.floor((w - 20) / FCW));
  return label.length <= max ? label : label.slice(0, max - 1) + "…";
}
function callChips(ids, path) {
  const out = [];
  (ids || []).forEach(function (id) {
    if (idToIdx.has(id)) {
      const idx = idToIdx.get(id);
      out.push({ id: id, idx: idx, key: path + "@" + idx });
    }
  });
  return out;
}
function chipLabel(c) {
  const cut = c.id.indexOf(":");
  return c.id.slice(0, cut) === curModule ? c.id.slice(cut + 1) : c.id;
}

function normSeq(seq, path, ancestors, depth) {
  const out = [];
  (seq || []).forEach(function (it, k) {
    const p = path + "/" + k;
    const item = normItem(it, p, ancestors, depth);
    if (item.kind === "box") {
      out.push(item);
      pushInlines(out, item, ancestors, depth);  // implementation right after the call site
    } else {
      pushInlines(out, item, ancestors, depth);  // head calls run before the construct branches
      out.push(item);
    }
    if (it.t === "try" && it.final && it.final.length) {
      normSeq(it.final, p + "/f", ancestors, depth).forEach(function (x) { out.push(x); });
    }
  });
  return out;
}
function pushInlines(out, item, ancestors, depth) {
  item.calls.forEach(function (c) {
    if (!inlineOpen.has(c.key)) { return; }
    if (ancestors.has(c.idx) || depth >= INLINE_MAX_DEPTH) {
      out.push({ kind: "box", ret: false, label: "↻ " + c.id + " — recursive or too deep to inline", calls: [] });
      return;
    }
    const sub = new Set(ancestors);
    sub.add(c.idx);
    out.push({ kind: "inline", id: c.id, idx: c.idx, key: c.key,
               seq: normSeq(data.nodes[c.idx].flow || [], c.key, sub, depth + 1) });
  });
}
function normItem(it, p, ancestors, depth) {
  const calls = callChips(it.calls, p);
  if (it.t === "if") {
    return { kind: "branch", label: it.label, calls: calls,
             branches: [{ lab: "yes", seq: normSeq(it.then, p + "/t", ancestors, depth) },
                        { lab: "no", seq: normSeq(it["else"], p + "/e", ancestors, depth) }] };
  }
  if (it.t === "switch") {
    return { kind: "branch", label: it.label, calls: calls,
             branches: it.cases.map(function (c, j) {
               return { lab: c.label, seq: normSeq(c.body, p + "/c" + j, ancestors, depth) };
             }) };
  }
  if (it.t === "try") {
    const br = [{ lab: "", seq: normSeq(it.body, p + "/b", ancestors, depth) }];
    it.handlers.forEach(function (h, j) {
      br.push({ lab: h.label, seq: normSeq(h.body, p + "/h" + j, ancestors, depth) });
    });
    return { kind: "branch", label: "try", calls: calls, branches: br };
  }
  if (it.t === "loop" || it.t === "with") {
    return { kind: "wrap", back: it.t === "loop", label: it.label, calls: calls,
             seq: normSeq(it.body, p + "/b", ancestors, depth) };
  }
  return { kind: "box", ret: it.t === "ret", label: it.label, calls: calls, rt: it.rt || null };
}

// -- signature header (function inputs at the top, return type at the bottom) --
function measureHeader(n) {
  if (!n.sig) { return null; }
  const name = prettyId(n.id);
  const dyn = n.dyn;
  const sim = n.sim;
  const rows = [];
  n.sig.p.forEach(function (pr) {
    let line = pr[0] + (pr[1] ? ": " + pr[1] : "");
    if (dyn && dyn.a && dyn.a[pr[0]] && dyn.a[pr[0]].length) {
      line += "  · seen: " + dyn.a[pr[0]].join(", ");
    } else if (sim && sim.a && sim.a[pr[0]]) {
      const s = sim.a[pr[0]];
      const bits = [];
      if (s.t && s.t.length) { bits.push(s.t.join(", ")); }
      if (s.v && s.v.length) { bits.push("= " + s.v.join(" | ")); }
      if (bits.length) { line += "  ~ " + bits.join(" "); }
    }
    rows.push(line);
  });
  let rline = "returns: " + (n.sig.r.length ? (n.sig.inf ? "~" : "") + n.sig.r.join(" | ") : "?");
  if (dyn && dyn.r && dyn.r.length) { rline += "  · seen: " + dyn.r.join(", "); }
  rows.push(rline);
  let title = name + "(…)";
  if (dyn) { title += "   · called " + dyn.n + "× (observed)"; }
  else if (sim && sim.n) { title += "   · " + sim.n + " call site" + (sim.n === 1 ? "" : "s") + " (simulated)"; }
  let w = title.length * FCW + 26;
  rows.forEach(function (r) { w = Math.max(w, r.length * FCW + 26); });
  w = Math.min(FMAXW + 200, Math.max(200, w));
  let tip = "";
  if (dyn && dyn.s && dyn.s.length) {
    const bits = dyn.s.map(function (s) {
      const args = Object.keys(s.args || {}).map(function (k) { return k + "=" + s.args[k]; }).join(", ");
      return name + "(" + args + ") → " + (s.ret === undefined ? "?" : s.ret);
    });
    tip = bits.join("\n");
  }
  return { rows: rows, title: title, w: w, h: 16 + FLH * (1 + rows.length), tip: tip };
}
function dHeader(n, hd, cx) {
  if (!hd) {
    S.push('<rect class="fstart" x="' + (cx - 40) + '" y="16" width="80" height="28" rx="14"/>');
    S.push('<text class="mid" x="' + cx + '" y="34">start</text>');
    return 44;
  }
  const x = cx - hd.w / 2;
  S.push('<rect class="fsig" x="' + x + '" y="16" width="' + hd.w + '" height="' + hd.h + '" rx="10"/>');
  const tip = hd.tip ? "<title>" + esc(hd.tip) + "</title>" : "";
  S.push('<text class="fsigt" x="' + (x + 12) + '" y="36">' + esc(fit(hd.title, hd.w)) + tip + "</text>");
  hd.rows.forEach(function (r, k) {
    S.push('<text class="elab" x="' + (x + 12) + '" y="' + (36 + FLH * (k + 1)) + '">' + esc(fit(r, hd.w)) + "</text>");
  });
  return 16 + hd.h;
}

function mSeq(seq) {
  let w = 24, h = 0;
  seq.forEach(function (it, k) {
    const m = mItem(it);
    it._m = m;
    w = Math.max(w, m.w);
    h += m.h + (k ? FVGAP : 0);
  });
  return { w: w, h: h };
}
function mItem(it) {
  if (it.kind === "box") {
    let w = Math.min(FMAXW, Math.max(100, it.label.length * FCW + 26));
    it.calls.forEach(function (c) { w = Math.max(w, Math.min(FMAXW, chipLabel(c).length * FCW + 46)); });
    if (it.rt) { w = Math.max(w, Math.min(FMAXW, it.rt.length * FCW + 46)); }
    return { w: w, h: 14 + FLH * (1 + it.calls.length + (it.rt ? 1 : 0)) };
  }
  if (it.kind === "wrap") {
    const b = mSeq(it.seq);
    it._bm = b;
    it._hw = Math.min(700, Math.max(120, it.label.length * FCW + 44));
    return { w: Math.max(it._hw, b.w) + 36, h: 36 + FVGAP + b.h + FVGAP };
  }
  if (it.kind === "inline") {
    const b = mSeq(it.seq);
    it._bm = b;
    const hw = Math.min(FMAXW, Math.max(180, it.id.length * FCW + 64));
    if (!it.seq.length) { return { w: hw, h: 52 }; }
    return { w: Math.max(hw, b.w + 28), h: 30 + FVGAP + b.h + 18 };
  }
  let bw = 0, bh = 0;
  it.branches.forEach(function (br) {
    const m = mSeq(br.seq);
    br._m = m;
    // column reserves room for its own branch label (except ..., case ...) so labels never collide
    br._cw = Math.max(m.w, 24, br.lab ? br.lab.length * ELCW + 12 : 0);
    bw += br._cw + FHGAP;
    bh = Math.max(bh, m.h);
  });
  bw -= FHGAP;
  it._dw = Math.min(560, Math.max(150, it.label.length * FCW + 64));
  return { w: Math.max(it._dw, bw), h: 44 + BR_GAP + bh + FVGAP + 12 };
}

let S = [];
function edge(a, b, lab, dash) {
  let d;
  if (Math.abs(a.x - b.x) < 0.5) {
    d = "M" + a.x + " " + a.y + " L" + b.x + " " + (b.y - 2);
  } else {
    const my = (a.y + b.y) / 2;
    const dir = b.x > a.x ? 1 : -1;
    // rounded elbows read better than hard corners, but never larger than the segments allow
    const R = Math.max(2, Math.min(7, Math.abs(b.x - a.x) / 2 - 1, Math.abs(b.y - a.y) / 4));
    d = "M" + a.x + " " + a.y +
        " L" + a.x + " " + (my - R) +
        " Q" + a.x + " " + my + " " + (a.x + dir * R) + " " + my +
        " L" + (b.x - dir * R) + " " + my +
        " Q" + b.x + " " + my + " " + b.x + " " + (my + R) +
        " L" + b.x + " " + (b.y - 2);
  }
  S.push('<path class="fedge' + (dash ? " dash" : "") + '" d="' + d + '" marker-end="url(#arr)"/>');
  if (lab) {
    const lx = (a.x + b.x) / 2 + 5, ly = (a.y + b.y) / 2 - 5;
    S.push('<text class="elab" x="' + lx + '" y="' + ly + '">' + esc(lab) + "</text>");
  }
}
function chipsAt(it, x, y) {
  it.calls.forEach(function (c, k) {
    const open = inlineOpen.has(c.key);
    S.push('<text class="chip' + (open ? " open" : "") + '" data-key="' + esc(c.key) + '" data-target="' + c.idx +
           '" x="' + x + '" y="' + (y + k * FLH) + '">' + (open ? "▾ " : "↳ ") + esc(chipLabel(c)) + "</text>");
  });
}

function dSeq(seq, cx, y, from, lab) {
  let prev = from, prevLab = lab || "";
  seq.forEach(function (it, k) {
    if (k) { y += FVGAP; }
    if (prev) { edge(prev, { x: cx, y: y }, prevLab); prevLab = ""; }
    let res;
    if (it.kind === "box") { res = dBox(it, cx, y); }
    else if (it.kind === "wrap") { res = dWrap(it, cx, y); }
    else if (it.kind === "inline") { res = dInline(it, cx, y); }
    else { res = dBranch(it, cx, y); }
    y += it._m.h;
    prev = res.exit;
  });
  return { exit: prev };
}

function dBox(it, cx, y) {
  const w = it._m.w, h = it._m.h;
  const x = cx - w / 2;
  S.push('<rect class="fbox' + (it.ret ? " ret" : "") + '" x="' + x + '" y="' + y +
         '" width="' + w + '" height="' + h + '" rx="6"/>');
  S.push('<text x="' + (x + 10) + '" y="' + (y + 20) + '">' + esc(fit(it.label, w)) +
         "<title>" + esc(it.label) + "</title></text>");
  chipsAt(it, x + 10, y + 20 + FLH);
  if (it.rt) {
    S.push('<text class="elab" x="' + (x + 10) + '" y="' + (y + 20 + FLH * (1 + it.calls.length)) +
           '">→ ' + esc(it.rt) + "</text>");
  }
  return { exit: it.ret ? null : { x: cx, y: y + h } };
}

function dInline(it, cx, y) {
  const w = it._m.w, h = it._m.h;
  const x = cx - w / 2;
  S.push('<rect class="finline" x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="8"/>');
  S.push('<text class="chip open" data-key="' + esc(it.key) + '" data-target="' + it.idx + '" x="' + (x + 10) +
         '" y="' + (y + 17) + '">▾ ' + esc(it.id) + "</text>");
  if (!it.seq.length) {
    S.push('<text class="elab" x="' + (x + 10) + '" y="' + (y + 38) + '">(no flow available)</text>');
  } else {
    dSeq(it.seq, cx, y + 30 + FVGAP, { x: cx, y: y + 28 });
  }
  return { exit: { x: cx, y: y + h } };
}

function dWrap(it, cx, y) {
  const w = it._m.w, hw = it._hw;
  const hx = cx - hw / 2;
  S.push('<rect class="fhead' + (it.back ? " loop" : "") + '" x="' + hx + '" y="' + y +
         '" width="' + hw + '" height="36" rx="18"/>');
  S.push('<text class="mid" x="' + cx + '" y="' + (y + 22) + '">' + esc(fit(it.label, hw)) +
         "<title>" + esc(it.label) + "</title></text>");
  chipsAt(it, cx + hw / 2 + 10, y + 22);
  const res = dSeq(it.seq, cx, y + 36 + FVGAP, { x: cx, y: y + 36 });
  const bottom = y + it._m.h;
  if (it.back && res.exit) {
    const lx = cx - w / 2;
    const d = "M" + res.exit.x + " " + res.exit.y + " L" + res.exit.x + " " + (res.exit.y + 10) +
              " L" + lx + " " + (res.exit.y + 10) + " L" + lx + " " + (y + 18) + " L" + (hx - 3) + " " + (y + 18);
    S.push('<path class="fedge dash" d="' + d + '" marker-end="url(#arr)"/>');
  }
  if (it.back) {
    const rx = cx + w / 2;
    const d2 = "M" + (hx + hw) + " " + (y + 18) + " L" + rx + " " + (y + 18) +
               " L" + rx + " " + (bottom - 6) + " L" + cx + " " + (bottom - 6);
    S.push('<path class="fedge" d="' + d2 + '"/>');
    return { exit: { x: cx, y: bottom - 6 } };
  }
  return { exit: res.exit };
}

function dBranch(it, cx, y) {
  const dw = it._dw, dh = 44;
  const bot = { x: cx, y: y + dh };
  S.push('<path class="fdia" d="M' + cx + " " + y + " L" + (cx + dw / 2) + " " + (y + dh / 2) +
         " L" + cx + " " + (y + dh) + " L" + (cx - dw / 2) + " " + (y + dh / 2) + ' Z"/>');
  S.push('<text class="mid" x="' + cx + '" y="' + (y + dh / 2 + 4) + '">' + esc(fit(it.label, dw - 30)) +
         "<title>" + esc(it.label) + "</title></text>");
  chipsAt(it, cx + dw / 2 + 10, y + dh / 2 - 4);
  let bw = 0;
  it.branches.forEach(function (br) { bw += Math.max(br._m.w, 24) + FHGAP; });
  bw -= FHGAP;
  let bx = cx - bw / 2;
  const topY = y + dh + BR_GAP;
  const elbowY = (bot.y + topY) / 2;   // the horizontal run of each elbow
  const mergeY = y + it._m.h - 6;
  const exits = [];
  it.branches.forEach(function (br) {
    const colW = br._cw;
    const c = bx + colW / 2;
    bx += colW + FHGAP;
    if (br.lab) {
      // sits just above its own elbow, far from the arrowhead at the column top
      const straight = Math.abs(c - cx) < 0.5;
      const lx = straight ? c + 8 : c;
      S.push('<text class="elab' + (straight ? "" : " mid") + '" x="' + lx + '" y="' + (elbowY - 8) + '">' +
             esc(br.lab) + "</text>");
    }
    if (!br.seq.length) {
      edge(bot, { x: c, y: topY });
      S.push('<path class="fedge" d="M' + c + " " + topY + " L" + c + " " + mergeY + '"/>');
      exits.push({ x: c, y: mergeY });
    } else {
      const res = dSeq(br.seq, c, topY, bot);
      if (res.exit) { exits.push(res.exit); }
    }
  });
  if (!exits.length) { return { exit: null }; }
  exits.forEach(function (p) {
    S.push('<path class="fedge" d="M' + p.x + " " + p.y + " L" + p.x + " " + mergeY +
           " L" + cx + " " + mergeY + '"/>');
  });
  S.push('<circle class="fdot" cx="' + cx + '" cy="' + mergeY + '" r="3"/>');
  return { exit: { x: cx, y: mergeY } };
}

// ---------------------------------------------------------- class panel
// The data-model equivalent of the flow diagram: a class, its properties, and
// any property whose type is another class expandable inline, recursively.
const CP_ROW = 26, CP_HEAD = 40, CP_PAD = 16, CP_INDENT = 24, CP_MAXDEPTH = 6;
let clsOpen = new Set();
let curClass = -1;
let classOrigin = -1;   // the class a method flow was opened from, for the breadcrumb back

function buildClassTree(k, path, ancestors, depth) {
  const c = CLASSES[k];
  const node = { k: k, id: c.id, name: c.name, st: c.st, rows: [] };
  (c.ext || []).forEach(function (b, i) {          // inherited types, expandable when parsed
    const key = path + "/x" + i;
    const row = { left: "extends " + b[0], right: "", ref: b[1], key: key, kind: "base" };
    if (b[1] >= 0 && clsOpen.has(key)) {
      if (ancestors.has(b[1]) || depth >= CP_MAXDEPTH) {
        row.cycle = true;
      } else {
        const sub = new Set(ancestors);
        sub.add(b[1]);
        row.child = buildClassTree(b[1], key, sub, depth + 1);
      }
    }
    node.rows.push(row);
  });
  c.f.forEach(function (f, i) {
    const key = path + "/" + i;
    const row = { left: f[0], right: f[1] || (f[3] ? "= " + f[3] : ""), ref: f[2], key: key, kind: "field" };
    if (f[2] >= 0 && clsOpen.has(key)) {
      if (ancestors.has(f[2]) || depth >= CP_MAXDEPTH) {
        row.cycle = true;
      } else {
        const sub = new Set(ancestors);
        sub.add(f[2]);
        row.child = buildClassTree(f[2], key, sub, depth + 1);
      }
    }
    node.rows.push(row);
  });
  c.meth.forEach(function (m, i) {
    node.rows.push({ left: m[0] + "()", right: "", ref: -1, key: path + "/m" + i, kind: "method", id: m[1] });
  });
  return node;
}

function measureClassTree(node) {
  ctx.font = "12.5px " + MONO;
  let lw = 0, rw = 0;
  node.rows.forEach(function (r) {
    lw = Math.max(lw, ctx.measureText((r.ref >= 0 ? "▸ " : "") + r.left).width);
    rw = Math.max(rw, ctx.measureText(r.right).width);
    if (r.child) { measureClassTree(r.child); }
  });
  ctx.font = "600 13.5px system-ui, sans-serif";
  const head = ctx.measureText(node.name + (node.st ? "  «" + node.st + "»" : "")).width + CP_PAD * 2;
  let w = Math.max(head, lw + rw + 34 + CP_PAD * 2, 240);
  let h = CP_HEAD;
  node.rows.forEach(function (r) {
    h += CP_ROW;
    if (r.cycle) { h += CP_ROW; }
    if (r.child) {
      h += r.child._h + 12;
      w = Math.max(w, r.child._w + CP_INDENT + CP_PAD * 2);
    }
  });
  node._w = w;
  node._h = h + CP_PAD;
  node._lw = lw;
  node._rw = rw;
}

function drawClassTree(node, x, y, depth) {
  const accent = node.st ? (STEREO[node.st] || "#3987e5") : "#3987e5";
  S.push('<rect class="cpbox" x="' + x + '" y="' + y + '" width="' + node._w + '" height="' + node._h +
         '" rx="10" style="stroke:' + accent + '"/>');
  S.push('<rect x="' + x + '" y="' + y + '" width="' + node._w + '" height="' + CP_HEAD +
         '" rx="10" style="fill:' + accent + ';opacity:0.16"/>');
  S.push('<text class="cphead" x="' + (x + CP_PAD) + '" y="' + (y + CP_HEAD / 2 + 5) + '">' +
         esc(node.name) + "</text>");
  if (node.st) {
    S.push('<text class="cpst" x="' + (x + node._w - CP_PAD) + '" y="' + (y + CP_HEAD / 2 + 4) +
           '" style="fill:' + accent + '">«' + esc(node.st) + "»</text>");
  }

  let ry = y + CP_HEAD + CP_ROW / 2 + 5;
  node.rows.forEach(function (r) {
    const open = r.child || r.cycle;
    const expandable = r.ref >= 0;
    const label = (expandable ? (open ? "▾ " : "▸ ") : "") + r.left;
    const base = r.kind === "base";
    const attrs = expandable
      ? ' class="chip' + (open ? " open" : "") + (base ? " base" : "") + '" data-ckey="' + esc(r.key) + '"'
      : (r.kind === "method"
          ? ' class="chip" data-fn="' + esc(r.id || "") + '"'
          : ' class="cprow' + (base ? " base" : "") + '"');
    S.push("<text" + attrs + ' x="' + (x + CP_PAD) + '" y="' + ry + '">' + esc(label) + "</text>");
    if (r.right) {
      S.push('<text class="cptype' + (expandable ? " ref" : "") + '" x="' + (x + node._w - CP_PAD) +
             '" y="' + ry + '">' + esc(r.right) + "</text>");
    }
    ry += CP_ROW;
    if (r.cycle) {
      S.push('<text class="cpnote" x="' + (x + CP_PAD + CP_INDENT) + '" y="' + ry + '">' +
             "↻ already shown above (recursive)</text>");
      ry += CP_ROW;
    } else if (r.child) {
      drawClassTree(r.child, x + CP_INDENT, ry - CP_ROW / 2 + 2, depth + 1);
      ry += r.child._h + 12;
    }
  });
}

function openClassPanel(k) {
  if (curClass !== k) { clsOpen = new Set(); }
  curClass = k;
  classOrigin = -1;
  curRoot = -1;
  renderClassPanel();
  panel.hidden = false;
  needsDraw = true;
}

// A method opened from a class card renders its flow in the same panel, without
// switching views or disturbing the graph — the class stays as a breadcrumb.
function openMethodFlow(i) {
  classOrigin = curClass >= 0 ? curClass : classOrigin;
  flowStack = [i];
  selected = -1;
  renderFlow(i);
  renderCrumbs();
  panel.hidden = false;
  needsDraw = true;
}

function renderClassPanel() {
  const tree = buildClassTree(curClass, "", new Set([curClass]), 0);
  S = [];
  measureClassTree(tree);
  const width = tree._w + 90;
  const height = tree._h + 80;
  drawClassTree(tree, 40, 34, 0);
  flowBox.innerHTML =
    '<svg width="' + width * fZoom + '" height="' + height * fZoom + '" viewBox="0 0 ' + width + " " + height +
    '">' + S.join("") + "</svg>";
  fNatW = width;
  fNatH = height;
  crumbs.innerHTML = "";
  const s = document.createElement("span");
  s.className = "crumb here";
  s.textContent = CLASSES[curClass].name;
  s.title = CLASSES[curClass].id;
  crumbs.appendChild(s);
}

function renderFlow(i) {
  curClass = -1;
  if (curRoot !== i) { inlineOpen = new Set(); }
  curRoot = i;
  const n = data.nodes[i];
  curModule = data.modules[n.m];
  const seq = normSeq(n.flow || [], "", new Set([i]), 0);
  if (!seq.length) {
    flowBox.innerHTML = '<div class="fempty">no flow available for this node</div>';
    return;
  }
  S = [];
  const m = mSeq(seq);
  const hd = measureHeader(n);
  const width = Math.max(480, m.w + 260, hd ? hd.w + 140 : 0);
  const cx = width / 2;
  const startY = dHeader(n, hd, cx);
  const height = m.h + startY + 140;
  const res = dSeq(seq, cx, startY + FVGAP, { x: cx, y: startY });
  if (res.exit) {
    S.push('<path class="fedge" d="M' + res.exit.x + " " + res.exit.y +
           " L" + res.exit.x + " " + (res.exit.y + 12) + '"/>');
    S.push('<circle class="fend" cx="' + res.exit.x + '" cy="' + (res.exit.y + 18) + '" r="6"/>');
    let rets = "";
    if (n.dyn && n.dyn.r && n.dyn.r.length) { rets = n.dyn.r.join(", "); }
    else if (n.sig && n.sig.r.length) { rets = n.sig.r.join(" | "); }
    if (rets) {
      S.push('<text class="elab" x="' + (res.exit.x + 14) + '" y="' + (res.exit.y + 22) + '">returns ' +
             esc(rets) + "</text>");
    }
  }
  flowBox.innerHTML =
    '<svg' + (animOn ? ' class="anim"' : '') +
    ' width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + " " + height + '">' +
    '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5"' +
    ' orient="auto-start-reverse"><path d="M 1 1 L 9 5 L 1 9 z" fill="#59637a"/></marker></defs>' +
    S.join("") + "</svg>";
  fNatW = width;
  fNatH = height;
  applyFlowZoom();  // keep the user's zoom level across expansions and navigation
}

// ------------------------------------------------------------------- init
const scopeEl = document.getElementById("scope");
scopeEl.textContent = (data.meta && data.meta.entry) ? "entry · " + data.meta.entry : (data.meta.root || "");
scopeEl.title = (data.meta && data.meta.root) || "";
document.getElementById("stats").innerHTML =
  "<span><b>" + N + "</b> functions</span><span><b>" + M + "</b> modules</span><span><b>" +
  links.length + "</b> calls</span>" + (C ? "<span><b>" + C + "</b> classes</span>" : "") +
  (data.meta && data.meta.has_runtime ? "<span><b>traced</b></span>" : "");
function refreshHud() {
  document.getElementById("hud").textContent = viewMode === "classes"
    ? "solid = has-a (property) · green dashed = inherits · click a method row to open its flow"
    : "click a function for its flow · click a module for all of it · drag to pan · scroll to zoom";
}
refreshHud();

// ---- search: jump straight to a function by name ----
const searchEl = document.getElementById("search");
searchEl.addEventListener("keydown", function (e) {
  if (e.key !== "Enter") { return; }
  const q = searchEl.value.trim().toLowerCase();
  if (!q) { return; }
  let best = -1;
  for (let i = 0; i < N; i++) {
    const id = data.nodes[i].id.toLowerCase();
    if (id.indexOf(q) >= 0) {
      const exact = id.slice(id.indexOf(":") + 1) === q;
      if (exact) { best = i; break; }
      if (best < 0) { best = i; }
    }
  }
  if (best >= 0) { openFlow(best); searchEl.blur(); }
});

window.addEventListener("resize", resize);
resize();
const R0 = Math.max(240, 110 * Math.sqrt(M));   // room for cards, not dots
data.modules.forEach(function (name, m) {
  const ang = 2 * Math.PI * m / Math.max(M, 1);
  const sup = ents[superOf(m)];
  sup.x = R0 * 1.4 * Math.cos(ang);
  sup.y = R0 * 0.75 * Math.sin(ang);
});
scale = Math.min(1.2, (0.42 * Math.min(W, H)) / R0);
tx = W / 2; ty = H / 2;
((data.meta && data.meta.entry_nodes) || []).forEach(function (id) {
  const i = idToIdx.get(id);
  if (i !== undefined) { ensureVisible(i); revealCallees(i); }
});
rebuild();
requestAnimationFrame(frame);
</script>
</body>
</html>
"""
