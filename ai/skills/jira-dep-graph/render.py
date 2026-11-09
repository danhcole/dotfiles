#!/usr/bin/env python3
"""Render a Jira dependency graph from JSON to .dot, .svg/.png, HTML, or ASCII.

Usage: render.py graph.json OUTPUT_PREFIX [--output html,svg,png,dot,ascii]
                 [--layout LR|TB] [--dense | --no-dense]

--output takes a comma-separated list (default: html). html is a self-contained
page with the SVG inline, zoom controls, a light/dark/auto theme toggle, and a
Download SVG button. ascii is printed to stdout; the others are written to
OUTPUT_PREFIX.<ext>.

Input JSON:
  {"title": "SRE-1 Epic name",
   "nodes": [{"key", "summary", "status", "assignee"?, "priority"?, "group"?, "external"?}],
   "edges": [{"from": "A", "to": "B", "type": "blocks" | "related", "relation"?: "..."}]}
"blocks" edges mean `from` must finish before `to`. "relation" is Jira's wording
for how `from` relates to `to` (e.g. "blocks", "is depended on by", "is related
to"); it is shown when hovering the edge. "group" clusters nodes
(e.g. by epic). "external" marks issues outside the epic/program.

The image highlights the critical path (longest chain of unfinished work),
marks open issues as Ready (all blockers done) or Waiting, and shows progress
stats in the header. Dense mode (auto above 20 nodes) shrinks text.

Colors are Via design tokens (--via-color-*). The svg and html outputs resolve
them with light-dark(), so they follow the viewer's color scheme. The dot and
png outputs use the light values.
"""
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from collections import defaultdict

DONE = {"resolved", "closed", "done", "complete", "completed"}
ACTIVE = {"in progress", "in review", "in development", "code review"}
BLOCKED = {"blocked", "on hold"}

# Via tokens, @via-ds/tokens 0.3.4 (values checked against dist/tokens.css).
PRIMITIVES = {
    "neutral-000": "#ffffff", "neutral-100": "#f9fbfa", "neutral-200": "#e8edeb",
    "neutral-300": "#c1c7c6", "neutral-400": "#889397", "neutral-500": "#5c6c75",
    "neutral-600": "#3d4f58", "neutral-700": "#1c2d38", "neutral-800": "#112733",
    "neutral-900": "#001e2b",
    "green-100": "#e3fcf7", "green-400": "#00ed64", "green-500": "#00a35c",
    "green-600": "#00684a", "green-700": "#023430",
    "yellow-100": "#fef7db", "yellow-400": "#ffc010", "yellow-600": "#944f01",
    "yellow-700": "#4c2100",
    "red-100": "#ffeae5", "red-300": "#ff6960", "red-400": "#db3030", "red-700": "#5b0000",
    "blue-300": "#0498ec", "blue-500": "#1254b7",
}
# semantic token -> (light, dark); each side is a primitive name or a literal color
SEMANTIC = {
    "background-primary": ("neutral-000", "neutral-900"),
    "background-secondary": ("neutral-100", "neutral-800"),
    "background-success": ("green-100", "green-700"),
    "background-warning": ("yellow-100", "yellow-700"),
    "background-error": ("red-100", "red-700"),
    "background-brand-enabled": ("green-600", "green-600"),
    "background-danger-enabled": ("red-400", "red-400"),
    "background-inverse-secondary": ("neutral-500", "neutral-300"),
    "background-accent-neutral-2": ("neutral-200", "neutral-500"),
    "border-primary": ("neutral-400", "neutral-400"),
    "border-secondary": ("neutral-300", "neutral-500"),
    "border-tertiary": ("neutral-200", "neutral-600"),
    "border-success": ("green-500", "green-500"),
    "border-warning": ("yellow-400", "yellow-600"),
    "border-error": ("red-400", "red-300"),
    "border-focus": ("blue-500", "blue-300"),
    "text-primary": ("neutral-900", "neutral-100"),
    "text-secondary": ("neutral-600", "neutral-300"),
    "text-onbrand": ("neutral-000", "neutral-000"),
    "text-ondanger": ("neutral-000", "neutral-000"),
    "text-inverse-primary": ("neutral-000", "neutral-900"),
    "text-accent-neutral-1": ("neutral-700", "neutral-200"),
    "text-accent-neutral-2": ("neutral-600", "neutral-200"),
    "text-link": ("#0163e4", "#04a1fb"),
}

# status category -> token names for card header, header text, body, border
STATUS_TOKENS = {
    "done": dict(head="background-brand-enabled", fg="text-onbrand", body="background-success", border="border-success"),
    "active": dict(head="yellow-400", fg="neutral-900", body="background-warning", border="border-warning"),
    "blocked": dict(head="background-danger-enabled", fg="text-ondanger", body="background-error", border="border-error"),
    "todo": dict(head="background-inverse-secondary", fg="text-inverse-primary", body="background-primary", border="border-primary"),
}
EXTERNAL_TOKENS = dict(head="background-accent-neutral-2", fg="text-accent-neutral-1", body="background-primary", border="border-secondary")
EXTERNAL_OPACITY = 0.6  # svg/html only; lower = dimmer, but text contrast drops below WCAG AA near 0.6
DONE_OPACITY = 0.75  # svg/html only
FONT = "Helvetica Neue,Helvetica,Arial,sans-serif"
LABELS = {"done": "Done", "active": "In progress", "blocked": "Blocked", "todo": "Not started"}


def light_hex(name):
    v = SEMANTIC[name][0] if name in SEMANTIC else name
    return PRIMITIVES.get(v, v)


class Colors:
    """Maps a token name to a color string for dot.

    themed=False: the light hex value (for .dot and .png).
    themed=True: a unique sentinel hex per token, later rewritten to
    var(--via-color-<token>) by themeize() so the SVG can follow light/dark.
    """

    def __init__(self, themed):
        self.themed = themed
        self.used = []

    def __call__(self, name):
        if not self.themed:
            return light_hex(name)
        if name not in self.used:
            self.used.append(name)
        return "#fd%04x" % self.used.index(name)

    def sentinels(self):
        return {"#fd%04x" % i: n for i, n in enumerate(self.used)}


def themeize(svg, colors):
    """Rewrite sentinel fill/stroke attributes into style="fill:var(--via-color-...)"."""
    var = {s: f"var(--via-color-{n})" for s, n in colors.sentinels().items()}

    def tag(m):
        name, attrs, slash = m.groups()
        styles = []

        def take(a):
            prop, val = a.group(1), a.group(2).lower()
            if val in var:
                styles.append(f"{prop}:{var[val]}")
                return ""
            return a.group(0)

        attrs = re.sub(r'\b(fill|stroke)="(#[0-9a-fA-F]{6})"', take, attrs)
        if styles:
            attrs += f' style="{";".join(styles)}"'
        return f"<{name}{attrs}{slash}>"

    return re.sub(r"<(polygon|path|ellipse|text|polyline|rect)\b([^>]*?)(/?)>", tag, svg)


def tokens_css():
    def ref(x):
        return f"var(--via-color-{x})" if x in PRIMITIVES else x

    lines = [":root { color-scheme: light dark;"]
    lines += [f"  --via-color-{k}: {v};" for k, v in PRIMITIVES.items()]
    lines += [f"  --via-color-{k}: light-dark({ref(a)}, {ref(b)});" for k, (a, b) in SEMANTIC.items()]
    lines.append("}")
    # de-emphasize issues outside the epic (and edges touching them)
    lines.append(f".external, .external-edge {{ opacity: {EXTERNAL_OPACITY}; }}")
    # finished work recedes slightly so open work stands out
    lines.append(f".done-node {{ opacity: {DONE_OPACITY}; }}")
    # edge hover: highlight the line; the transparent .hit path widens the target
    lines.append(".edge .hit { cursor: help; }")
    lines.append(".edge:hover path:not(.hit) { stroke-width: 3px; }")
    return "\n".join(lines)


def category(status):
    s = (status or "").lower()
    if s in DONE:
        return "done"
    if s in ACTIVE:
        return "active"
    if s in BLOCKED:
        return "blocked"
    return "todo"


def h(s):
    return html.escape(str(s), quote=True)


def q(s):
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def load(path):
    with open(path) as f:
        g = json.load(f)
    keys = {n["key"] for n in g["nodes"]}
    g["edges"] = [e for e in g["edges"] if e["from"] in keys and e["to"] in keys]
    seen, uniq = set(), []
    for e in g["edges"]:
        k = (e["from"], e["to"], e["type"]) if e["type"] == "blocks" else (
            *sorted((e["from"], e["to"])), e["type"])
        if k not in seen:
            seen.add(k)
            uniq.append(e)
    g["edges"] = uniq
    return g


def analyze(g):
    """Return (blockers, critical_nodes, critical_edges, ready, waiting)."""
    nodes = {n["key"]: n for n in g["nodes"]}
    done = {k for k, n in nodes.items() if category(n.get("status")) == "done"}
    blockers = defaultdict(set)
    for e in g["edges"]:
        if e["type"] == "blocks":
            blockers[e["to"]].add(e["from"])

    # Longest chain through unfinished issues. Cycle-safe.
    memo = {}

    def chain(k, stack=()):
        if k in memo:
            return memo[k]
        best = []
        for p in blockers[k]:
            if p in done or p in stack or nodes[p].get("external"):
                continue
            c = chain(p, stack + (k,))
            if len(c) > len(best):
                best = c
        memo[k] = best + [k]
        return memo[k]

    open_internal = [k for k in nodes if k not in done and not nodes[k].get("external")]
    crit = max((chain(k) for k in open_internal), key=len, default=[])
    crit_edges = {(a, b) for a, b in zip(crit, crit[1:])}

    ready, waiting = set(), {}
    for k in open_internal:
        open_blockers = sorted(p for p in blockers[k] if p not in done)
        if open_blockers:
            waiting[k] = open_blockers
        else:
            ready.add(k)
    return blockers, set(crit), crit_edges, ready, waiting


def wrap(s, width, lines):
    parts = textwrap.wrap(s or "", width)
    if len(parts) > lines:
        parts = parts[:lines]
        parts[-1] = parts[-1][: width - 1].rstrip() + "…"
    return parts


def node_label(n, dense, crit, ready, waiting, C):
    cat = category(n.get("status"))
    ext = n.get("external")
    t = EXTERNAL_TOKENS if ext else STATUS_TOKENS[cat]
    head, body, fg, border = C(t["head"]), C(t["body"]), C(t["fg"]), C(t["border"])
    fs, width, lines = (9, 30, 3) if dense else (11, 36, 4)
    if ext:
        fs -= 1
    key = n["key"]
    tag = ""
    if ext:
        tag = "external"
    elif n.get("priority"):
        tag = n["priority"].split(" - ")[-1]
    summary = "<BR ALIGN=\"LEFT\"/>".join(h(p) for p in wrap(n.get("summary", ""), width, lines))
    footer = [h(n.get("status", "?"))]
    if n.get("assignee"):
        footer.append(h(n["assignee"]))
    foot = " · ".join(footer)

    state = ""
    if not ext and cat != "done":
        if key in ready:
            state = (f'<TD BGCOLOR="{C("background-brand-enabled")}"><FONT COLOR="{C("text-onbrand")}" '
                     f'POINT-SIZE="{fs - 1}"><B> Ready </B></FONT></TD>')
        elif key in waiting:
            w = ", ".join(x.split("-")[-1] for x in waiting[key][:4])
            more = "+" if len(waiting[key]) > 4 else ""
            state = (f'<TD BGCOLOR="{C("background-accent-neutral-2")}"><FONT COLOR="{C("text-accent-neutral-2")}" '
                     f'POINT-SIZE="{fs - 1}"> Waiting on {h(w)}{more} </FONT></TD>')
    crit_mark = " &#9679;" if key in crit else ""

    rows = [
        f'<TR><TD ALIGN="LEFT" BGCOLOR="{head}" CELLPADDING="5"><FONT COLOR="{fg}" POINT-SIZE="{fs}">'
        f'<B>{h(key)}</B>{crit_mark}</FONT></TD>'
        f'<TD ALIGN="RIGHT" BGCOLOR="{head}" CELLPADDING="5"><FONT COLOR="{fg}" POINT-SIZE="{fs - 2}">{h(tag) or "&nbsp;"}</FONT></TD></TR>',
        f'<TR><TD COLSPAN="2" ALIGN="LEFT" BGCOLOR="{body}" CELLPADDING="6">'
        f'<FONT POINT-SIZE="{fs}" COLOR="{C("text-primary")}">{summary}<BR ALIGN="LEFT"/></FONT></TD></TR>',
        f'<TR><TD ALIGN="LEFT" BGCOLOR="{body}" CELLPADDING="4"><FONT POINT-SIZE="{fs - 2}" COLOR="{C("text-secondary")}">{foot}</FONT></TD>'
        + (state or f'<TD BGCOLOR="{body}"></TD>') + '</TR>',
    ]
    return ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">'
            + "".join(rows) + '</TABLE>>'), border, ext


def header_label(g, dense, crit, ready, C):
    nodes = [n for n in g["nodes"] if not n.get("external")]
    counts = defaultdict(int)
    for n in nodes:
        counts[category(n.get("status"))] += 1
    total = len(nodes) or 1
    pct = round(100 * counts["done"] / total)
    stats = ", ".join(f"{counts[c]} {LABELS[c].lower()}" for c in LABELS if counts[c])
    muted = C("text-secondary")
    swatches = "".join(
        f'<TD BGCOLOR="{C(STATUS_TOKENS[c]["head"])}" WIDTH="12" HEIGHT="12" FIXEDSIZE="TRUE"></TD>'
        f'<TD ALIGN="LEFT"><FONT POINT-SIZE="9" COLOR="{muted}"> {LABELS[c]}   </FONT></TD>' for c in LABELS)
    legend2 = (f'<TD><FONT POINT-SIZE="9" COLOR="{C("border-error")}"><B>&#9472;&#9472;</B></FONT></TD>'
               f'<TD ALIGN="LEFT"><FONT POINT-SIZE="9" COLOR="{muted}"> Critical path   </FONT></TD>'
               f'<TD><FONT POINT-SIZE="9" COLOR="{C("border-secondary")}">- - -</FONT></TD>'
               f'<TD ALIGN="LEFT"><FONT POINT-SIZE="9" COLOR="{muted}"> Related / external (dashed)</FONT></TD>')
    return ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">'
            f'<TR><TD ALIGN="LEFT" COLSPAN="12"><FONT POINT-SIZE="22" COLOR="{C("text-primary")}"><B>{h(g.get("title", "Dependencies"))}</B></FONT></TD></TR>'
            f'<TR><TD ALIGN="LEFT" COLSPAN="12"><FONT POINT-SIZE="11" COLOR="{muted}">'
            f'{pct}% done  ·  {stats}  ·  {len(ready)} ready to start  ·  critical path: {len(crit)} open</FONT></TD></TR>'
            f'<TR><TD ALIGN="LEFT" COLSPAN="12"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2"><TR>{swatches}{legend2}</TR></TABLE></TD></TR>'
            '</TABLE>>')


def to_dot(g, C, layout="LR", dense=None):
    if dense is None:
        dense = len(g["nodes"]) > 20
    _, crit, crit_edges, ready, waiting = analyze(g)
    nodesep, ranksep = (0.25, 0.7) if dense else (0.4, 0.9)
    out = ["digraph deps {",
           f'  rankdir={layout}; bgcolor="{C("background-primary")}"; pad=0.4; nodesep={nodesep}; ranksep={ranksep}; splines=true;',
           f'  fontname="{FONT}"; labelloc=t; labeljust=l;',
           f'  label={header_label(g, dense, crit, ready, C)};',
           f'  node [shape=box, style="filled", fillcolor="{C("background-primary")}", margin=0, penwidth=1.4, fontname="{FONT}"];',
           f'  edge [fontname="{FONT}", arrowsize=0.8, color="{C("text-secondary")}", penwidth=1.4];']

    def node(n, indent="  "):
        label, border, ext = node_label(n, dense, crit, ready, waiting, C)
        if n["key"] in crit:
            border = C("border-error")
        pw = "2.6" if n["key"] in crit else "1.0" if ext else "1.4"
        style = '"filled,dashed"' if ext else '"filled"'
        cls = (' class="external",' if ext
               else ' class="done-node",' if category(n.get("status")) == "done" else "")
        return (f'{indent}"{q(n["key"])}" [label={label}, color="{border}", penwidth={pw}, style={style},{cls} '
                f'URL="https://jira.mongodb.org/browse/{q(n["key"])}", target="_blank", tooltip="{q(n.get("summary", ""))}"];')

    groups = defaultdict(list)
    for n in g["nodes"]:
        groups[None if n.get("external") else n.get("group")].append(n)
    for i, (grp, nodes) in enumerate(groups.items()):
        if grp is None:
            out += [node(n) for n in nodes]
            continue
        out.append(f'  subgraph cluster_{i} {{ style="rounded,filled"; fillcolor="{C("background-secondary")}"; color="{C("border-tertiary")}"; '
                   f'margin=16; labeljust=l; fontsize=12; fontcolor="{C("text-secondary")}"; label=<<B>{h(grp)}</B>>;')
        out += [node(n, "    ") for n in nodes]
        out.append("  }")

    done = {n["key"] for n in g["nodes"] if category(n.get("status")) == "done"}
    muted = C("border-secondary")
    external = {n["key"] for n in g["nodes"] if n.get("external")}
    for i, e in enumerate(g["edges"]):
        a, b = q(e["from"]), q(e["to"])
        eid = f'id="e{i}", '  # lets edge_tooltips() find this edge in the SVG
        if e["type"] != "blocks":
            out.append(f'  "{a}" -> "{b}" [{eid}dir=none, style=dashed, color="{muted}", penwidth=1, constraint=false];')
        elif e["from"] in external or e["to"] in external:
            out.append(f'  "{a}" -> "{b}" [{eid}class="external-edge", color="{muted}", penwidth=1];')
        elif (e["from"], e["to"]) in crit_edges:
            out.append(f'  "{a}" -> "{b}" [{eid}color="{C("border-error")}", penwidth=2.8, arrowsize=1];')
        elif e["from"] in done:
            out.append(f'  "{a}" -> "{b}" [{eid}color="{muted}", penwidth=1.1];')
        else:
            out.append(f'  "{a}" -> "{b}" [{eid}];')
    out.append("}")
    return "\n".join(out) + "\n"


def edge_tip(e, crit_edges):
    """Hover text for an edge: '<from> <relation> <to>', using Jira's wording when given."""
    rel = e.get("relation") or ("blocks" if e["type"] == "blocks" else "is related to")
    tip = f'{e["from"]} {rel} {e["to"]}'
    if (e["from"], e["to"]) in crit_edges:
        tip += " (critical path)"
    return tip


def edge_tooltips(svg, g):
    """Give each edge a relationship tooltip and a wide invisible hover target.

    Replaces graphviz's default '<from>-><to>' <title>, which browsers show as the
    native tooltip, and adds a transparent 12px stroke so thin lines are easy to hit.
    """
    _, _, crit_edges, _, _ = analyze(g)
    tips = {f"e{i}": edge_tip(e, crit_edges) for i, e in enumerate(g["edges"])}

    def edge(m):
        eid, cls, body = m.groups()
        body = re.sub(r"<title>.*?</title>", lambda _: f"<title>{h(tips[eid])}</title>", body, count=1, flags=re.S)
        path = re.search(r'<path\b[^>]*?\sd="([^"]+)"[^>]*/>', body)
        if path:
            hit = f'<path class="hit" d="{path.group(1)}" fill="none" stroke="transparent" stroke-width="12" pointer-events="stroke"/>'
            body = body.replace(path.group(0), path.group(0) + hit, 1)
        return f'<g id="{eid}" class="{cls}">{body}</g>'

    return re.sub(r'<g id="(e\d+)" class="([^"]*\bedge\b[^"]*)">(.*?)</g>', edge, svg, flags=re.S)


def to_ascii(g):
    nodes = {n["key"]: n for n in g["nodes"]}
    blockers, crit, _, ready, waiting = analyze(g)
    level = {}

    def lvl(k, stack=()):
        if k in level:
            return level[k]
        if k in stack:
            return 0
        level[k] = 1 + max((lvl(p, stack + (k,)) for p in blockers[k]), default=-1)
        return level[k]

    for k in nodes:
        lvl(k)
    mark = {"done": "[x]", "active": "[~]", "blocked": "[!]", "todo": "[ ]"}
    lines = [g.get("title", "Dependencies"),
             "[x] done  [~] in progress  [!] blocked  [ ] not started  * critical path",
             "Each stage can start once all issues pointing at it (below) are done.", ""]
    for L in sorted(set(level.values())):
        lines.append(f"Stage {L + 1}")
        for k in sorted(k for k in nodes if level[k] == L):
            n = nodes[k]
            tag = " (external)" if n.get("external") else ""
            star = "*" if k in crit else " "
            state = " READY" if k in ready else (" WAITING" if k in waiting else "")
            lines.append(f" {star}{mark[category(n.get('status'))]} {k}  {n.get('summary', '')[:70]}  "
                         f"<{n.get('status', '?')}>{tag}{state}")
            for p in sorted(blockers[k]):
                lines.append(f"        <-- blocked by {p}")
        lines.append("")
    rel = [e for e in g["edges"] if e["type"] != "blocks"]
    if rel:
        lines.append("Related (no ordering): " + ", ".join(f"{e['from']}~{e['to']}" for e in rel))
    return "\n".join(lines) + "\n"


HTML_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>__TITLE__</title>
<style id="via-tokens">
__TOKENS__
</style>
<style>
  body { margin: 0; font: 13px/20px "Euclid Circular A", -apple-system, "Helvetica Neue", Arial, sans-serif;
         background: var(--via-color-background-secondary); color: var(--via-color-text-primary); }
  header { display: flex; align-items: center; gap: 8px; padding: 12px 24px; background: var(--via-color-background-primary);
           border-bottom: 1px solid var(--via-color-border-tertiary); position: sticky; top: 0; z-index: 1; }
  header h1 { font-size: 24px; line-height: 32px; font-weight: 500; margin: 0; flex: 1; }
  header small { font-size: 12px; line-height: 16px; font-weight: 400; color: var(--via-color-text-secondary); margin-left: 8px; }
  button { font: 500 13px/20px inherit; font-family: inherit; padding: 6px 12px; border-radius: 6px; cursor: pointer; }
  button.tertiary { background: transparent; border: 1px solid transparent; color: var(--via-color-text-link); }
  button.tertiary:hover { background: var(--via-color-background-secondary); }
  button.primary { background: var(--via-color-background-brand-enabled); border: 1px solid var(--via-color-background-brand-enabled); color: var(--via-color-text-onbrand); }
  button.primary:hover { filter: brightness(1.1); }
  button:focus-visible { outline: 2px solid var(--via-color-border-focus); outline-offset: 2px; }
  #wrap { overflow: auto; padding: 24px; }
  #graph { transform-origin: 0 0; display: inline-block; background: var(--via-color-background-primary);
           border: 1px solid var(--via-color-border-tertiary); border-radius: 8px; }
  svg { display: block; }
</style></head><body>
<header>
  <h1>__TITLE__ <small>Generated __DATE__</small></h1>
  <button class="tertiary" id="theme" aria-label="Color theme">Theme: auto</button>
  <button class="tertiary" id="out" aria-label="Zoom out">&minus;</button>
  <button class="tertiary" id="in" aria-label="Zoom in">+</button>
  <button class="tertiary" id="fit">Fit to width</button>
  <button class="primary" id="dl">Download SVG</button>
</header>
<div id="wrap"><div id="graph">__SVG__</div></div>
<script>
(function () {
  var root = document.documentElement, KEY = "jira-dep-graph-theme", MODES = ["auto", "light", "dark"], mode = "auto";
  var themeBtn = document.getElementById("theme");
  function setMode(m) {
    mode = m;
    root.style.colorScheme = m === "auto" ? "light dark" : m;
    themeBtn.textContent = "Theme: " + m;
    try { localStorage.setItem(KEY, m); } catch (e) {}
  }
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  setMode(MODES.indexOf(saved) >= 0 ? saved : "auto");
  themeBtn.onclick = function () { setMode(MODES[(MODES.indexOf(mode) + 1) % MODES.length]); };

  var g = document.getElementById("graph"), svg = g.querySelector("svg"), z = 1;
  var w0 = svg.viewBox.baseVal.width || svg.getBoundingClientRect().width;
  function zoom(v) { z = Math.max(0.1, Math.min(4, v)); svg.setAttribute("width", w0 * z + "pt"); svg.removeAttribute("height"); }
  document.getElementById("in").onclick = function () { zoom(z * 1.25); };
  document.getElementById("out").onclick = function () { zoom(z / 1.25); };
  document.getElementById("fit").onclick = function () { zoom((document.getElementById("wrap").clientWidth - 40) / (w0 * 4 / 3)); };
  document.getElementById("dl").onclick = function () {
    var c = svg.cloneNode(true);
    c.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    c.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
    c.setAttribute("width", w0 + "pt"); c.setAttribute("height", svg.viewBox.baseVal.height + "pt");
    var st = document.createElementNS("http://www.w3.org/2000/svg", "style");
    st.textContent = document.getElementById("via-tokens").textContent;
    c.insertBefore(st, c.firstChild);
    if (mode !== "auto") c.style.colorScheme = mode;
    var blob = new Blob(['<?xml version="1.0" encoding="UTF-8"?>\\n' + new XMLSerializer().serializeToString(c)], { type: "image/svg+xml" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "__NAME__.svg";
    document.body.appendChild(a); a.click(); a.remove();
  };
  // Open a ticket in a new tab on plain left-click. Modified and middle clicks keep their browser behavior.
  g.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a");
    if (!a || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    var href = a.getAttribute("xlink:href") || a.getAttribute("href");
    if (!href) return;
    e.preventDefault();
    var w = null;
    try { w = window.open(href, "_blank"); } catch (err) {}
    if (w) { try { w.opener = null; } catch (err) {} } else { location.href = href; }
  });
  document.getElementById("fit").click();
})();
</script></body></html>
"""

OUTPUTS = {"html", "svg", "png", "dot", "ascii"}


def run_dot(dot_text, fmt, dpi=None):
    extra = [f"-Gdpi={dpi}"] if dpi else []
    return subprocess.run(["dot", f"-T{fmt}", *extra], input=dot_text.encode(), check=True,
                          capture_output=True).stdout


def standalone_svg(svg_text):
    """Embed the token definitions so the file follows the viewer's color scheme."""
    return re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + f"\n<style>\n{tokens_css()}\n</style>", svg_text, count=1)


def to_html(g, svg_text, name):
    svg = svg_text[svg_text.index("<svg"):]
    return (HTML_PAGE.replace("__TITLE__", h(g.get("title", "Dependencies"))).replace("__NAME__", h(name))
            .replace("__DATE__", datetime.date.today().isoformat()).replace("__TOKENS__", tokens_css())
            .replace("__SVG__", svg))


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)

    def opt(name, default):
        if name in args:
            i = args.index(name)
            v = args[i + 1]
            del args[i:i + 2]
            return v
        return default

    outputs = set(opt("--output", "html").lower().replace(" ", "").split(","))
    if outputs - OUTPUTS:
        sys.exit(f"unknown --output {sorted(outputs - OUTPUTS)}; choose from {sorted(OUTPUTS)}")
    layout = opt("--layout", "LR").upper()
    dense = True if "--dense" in args else False if "--no-dense" in args else None
    args = [a for a in args if a not in ("--dense", "--no-dense")]
    g, prefix = load(args[0]), args[1]
    name = prefix.rsplit("/", 1)[-1]

    if {"dot", "png"} & outputs:
        light_dot = to_dot(g, Colors(False), layout, dense)
    if "dot" in outputs:
        with open(prefix + ".dot", "w") as f:
            f.write(light_dot)
        print(prefix + ".dot")

    if outputs & {"html", "svg", "png"} and not shutil.which("dot"):
        sys.exit("graphviz `dot` not found; install it (brew install graphviz), or use --output ascii")
    if outputs & {"html", "svg"}:
        C = Colors(True)
        svg_text = edge_tooltips(themeize(run_dot(to_dot(g, C, layout, dense), "svg").decode(), C), g)
        if "svg" in outputs:
            with open(prefix + ".svg", "w") as f:
                f.write(standalone_svg(svg_text))
            print(prefix + ".svg")
        if "html" in outputs:
            with open(prefix + ".html", "w") as f:
                f.write(to_html(g, svg_text, name))
            print(prefix + ".html")
    if "png" in outputs:
        with open(prefix + ".png", "wb") as f:
            f.write(run_dot(light_dot, "png", 144))
        print(prefix + ".png")
    if "ascii" in outputs:
        print(to_ascii(g))


if __name__ == "__main__":
    main()
