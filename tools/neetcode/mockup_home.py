"""Builds the DSA mockup: home (the existing catalog design plus swappable filters), problem and pattern pages.

home uses the app's real stylesheets (design.css, app.css, catalog.css), so cards, rail and header are the real ones.
problem.html and pattern.html are the approved screens, sliced out of the earlier single-file mockup.
"""
import json
import re
from pathlib import Path

ROOT = Path('/Users/genuinebasilnt/projects/learn-rust')
SP = Path('/private/tmp/claude-501/-Users-genuinebasilnt-projects-learn-rust/ee7ba911-8d67-4b90-9d0e-68ff6877d299/scratchpad')
OUT = SP / 'artifact'

data = json.load(open(ROOT / 'content/dsa/problems.json'))
groups = list(data['company_groups'].keys())
P = []
for p in data['problems']:
    P.append({
        'i': p['id'], 'n': p['number'], 't': p['title'], 's': p['slug'], 'd': p['difficulty'][0], 'p': p['pattern'],
        'l': p['lists'], 'pr': 1 if p['premium'] else 0, 'tg': p['tags'][:6],
        'co': [[c['name'], groups.index(c['group']), 1 if c['recent'] else 0] for c in p['companies'][:14]],
        'v': p['video'] or '', 'r': 'm' if p['role'] == 'must_learn' else 'p', 'of': p.get('practice_of', ''),
    })
ORDER = ['Arrays & Hashing', 'Two Pointers', 'Sliding Window', 'Stack', 'Binary Search', 'Linked List', 'Trees', 'Tries',
         'Heap / Priority Queue', 'Backtracking', 'Graphs', 'Advanced Graphs', '1-D Dynamic Programming',
         '2-D Dynamic Programming', 'Greedy', 'Intervals', 'Math & Geometry', 'Bit Manipulation']
BLURB = {
    'Arrays & Hashing': 'Trade memory for time: a hash map or set turns a nested scan into one pass.',
    'Two Pointers': 'Two indices walking toward each other, or in step, replace nested loops on sorted or linked data.',
    'Sliding Window': 'A window that grows and shrinks keeps a running answer for every subarray.',
    'Stack': 'Last in, first out fits anything nested, or waiting on a later answer.',
    'Binary Search': "Halve the search space whenever you can answer 'which side?' in O(1).",
    'Linked List': 'Pointer surgery: reverse, merge, find the middle, detect the loop.',
    'Trees': 'Recursion mirrors the shape: solve for the children, combine at the node.',
    'Tries': "A prefix tree makes 'starts with' and word search cheap.",
    'Heap / Priority Queue': 'Always know the best remaining item without sorting everything.',
    'Backtracking': 'Build candidates one choice at a time, undo, and prune the dead ends.',
    'Graphs': 'Model it as nodes and edges, then pick the traversal: DFS, BFS, union-find or topological sort.',
    'Advanced Graphs': 'Weighted edges and spanning structures: Dijkstra, Prim and Kruskal, Bellman-Ford.',
    '1-D Dynamic Programming': 'Define the state, write the recurrence, remember the sub-answers.',
    '2-D Dynamic Programming': 'Two indices as the state: grids, string pairs and knapsacks.',
    'Greedy': 'Make the locally best choice, and prove it never hurts.',
    'Intervals': 'Sort by start, then sweep: merge, insert and count overlaps.',
    'Math & Geometry': 'Matrices, digits and number tricks with no fancy data structure.',
    'Bit Manipulation': 'XOR, shifts and masks for O(1)-space tricks.',
}
TECH = {
    'Arrays & Hashing': ['hash map', 'hash set', 'prefix sums', 'bucket sort'],
    'Two Pointers': ['opposite ends', 'fast & slow', 'dedupe', 'three-sum'],
    'Sliding Window': ['fixed window', 'variable window', 'counts', 'monotonic deque'],
    'Stack': ['matching pairs', 'monotonic stack', 'evaluate'],
    'Binary Search': ['sorted array', 'rotated array', 'search the answer'],
    'Linked List': ['reverse', 'fast & slow', 'dummy head', 'merge'],
    'Trees': ['DFS orders', 'BFS levels', 'BST', 'LCA'],
    'Tries': ['insert & search', 'prefix', 'wildcards', 'grid + trie'],
    'Heap / Priority Queue': ['top-k', 'two heaps', 'merge k', 'scheduling'],
    'Backtracking': ['subsets', 'permutations', 'combinations', 'grids'],
    'Graphs': ['DFS', 'BFS', 'flood fill', 'topo sort', 'union-find'],
    'Advanced Graphs': ['Dijkstra', 'MST', 'Bellman-Ford'],
    '1-D Dynamic Programming': ['memoise', 'tabulate', 'knapsack-ish'],
    '2-D Dynamic Programming': ['grid paths', 'LCS & edit distance', 'knapsack'],
    'Greedy': ['sort + scan', 'exchange argument', 'jump game'],
    'Intervals': ['merge', 'sweep line', 'meeting rooms'],
    'Math & Geometry': ['matrix', 'digits', 'pow & gcd'],
    'Bit Manipulation': ['xor', 'counting bits', 'masks'],
}

root_css = ''.join((ROOT / 'web/src/styles' / f).read_text() + '\n' for f in ('design.css', 'app.css', 'catalog.css'))

css = r'''
/* ---- mockup-only bar ---- */
.mk-bar{display:flex;gap:6px;align-items:center;padding:8px 24px;background:var(--bg);border-bottom:1px dashed var(--line2);font:500 11px var(--mono);color:var(--dim);flex-wrap:wrap}
.mk-bar b{letter-spacing:.14em;margin-right:6px}
.mk-bar a{padding:4px 10px;border:1px solid var(--line2);border-radius:6px;color:var(--mut)}
.mk-bar a.on{border-color:var(--acc);color:var(--fg);background:var(--acc-bg)}
/* ---- goals strip: the three goal cards double as list switches ---- */
.d-goals{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;padding-top:28px}
.d-goal{position:relative;text-align:left;display:flex;flex-direction:column;gap:10px;padding:18px 20px;border:1px solid var(--line2);border-radius:10px;background:var(--panel);min-width:0;transition:border-color .15s}
.d-goal:hover{border-color:var(--line)}
.d-goal.on{border-color:var(--gc)}
.d-goal.on::before{content:"";position:absolute;inset:-1px -1px auto -1px;height:2px;border-radius:10px 10px 0 0;background:var(--gc)}
.d-goal>span{font:500 11px var(--mono);letter-spacing:.2em;color:var(--dim)}
.d-goal b{font:700 30px var(--sans);letter-spacing:-.02em;line-height:1}
.d-goal b small{font:500 13px var(--mono);color:var(--dim);letter-spacing:0;margin-left:6px}
.d-goal .bar{height:5px;border-radius:3px;background:var(--line2);overflow:hidden}
.d-goal .bar i{display:block;height:100%;border-radius:3px}
.d-goal em{font:500 12px var(--mono);color:var(--dim);font-style:normal}
.d-goal em b{font:600 12px var(--mono);color:var(--fg);letter-spacing:0}
/* ---- tools ---- */
.d-fbtn{height:38px;padding:0 14px;display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line2);border-radius:6px;font:500 12px var(--mono);color:var(--mut);background:var(--panel)}
.d-fbtn:hover{color:var(--fg);border-color:var(--line)}
.d-fbtn.on{border-color:var(--ca);color:var(--ca);background:var(--cab)}
.d-fbtn i{font-style:normal;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--ca);color:var(--on-acc);font:600 10.5px/18px var(--mono);text-align:center}
.d-fbtn kbd{font:500 10.5px var(--mono);color:var(--dim);border:1px solid var(--line2);border-radius:4px;padding:1px 5px}
.d-active{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.d-chip{height:28px;padding:0 6px 0 11px;display:inline-flex;align-items:center;gap:8px;border:1px solid var(--ca);border-radius:5px;background:var(--cab);color:var(--ca);font:500 12px var(--mono)}
.d-chip button{color:var(--ca);opacity:.7;font-size:14px;line-height:1}
.d-chip button:hover{opacity:1}
.d-clear{font:500 12px var(--mono);color:var(--dim)}
.d-clear:hover{color:var(--fg)}
/* ---- pattern cards (the real .tcard) ---- */
.tcard{cursor:pointer}
.tcard.dim{opacity:.45}
.tc-hit{font:500 11px var(--mono);color:var(--ca)}
.tc-foot .tc-acts{display:flex;gap:8px;flex:none}
.tc-go.ghost{border-color:var(--line);color:var(--mut)}
.tc-go.ghost:hover{border-color:var(--ca);color:var(--ca)}
/* ---- problem long cards ---- */
.d-plist{display:flex;flex-direction:column;gap:10px}
.d-pcard{position:relative;display:grid;grid-template-columns:38px minmax(0,1fr) auto;gap:6px 16px;align-items:start;padding:16px 18px;border:1px solid var(--line2);border-radius:10px;background:var(--panel);transition:border-color .15s}
.d-pcard:hover{border-color:var(--line)}
.d-pcard.due{border-color:color-mix(in oklab,var(--vio) 55%,var(--line2))}
.d-pcard.due::before{content:"";position:absolute;inset:-1px -1px auto -1px;height:2px;border-radius:10px 10px 0 0;background:var(--vio)}
.d-st{width:28px;height:28px;margin-top:2px;border-radius:50%;border:2px solid var(--line);display:grid;place-items:center;font:700 13px var(--mono);color:transparent}
.d-st.solo{background:var(--grn);border-color:var(--grn);color:var(--on-acc)}
.d-st.help{border-color:var(--grn);color:var(--grn);background:var(--grn-bg)}
.d-st.fail{border-color:var(--bad);color:var(--bad);background:var(--bad-bg)}
.d-pbody{display:flex;flex-direction:column;gap:8px;min-width:0}
.d-ph{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;min-width:0}
.d-pnum{font:500 12px var(--mono);color:var(--dim)}
.d-ptitle{font-size:16px;font-weight:700;letter-spacing:-.005em;color:var(--fg);text-align:left}
.d-ptitle:hover{color:var(--ca)}
.d-lc{font:500 11.5px var(--mono);color:var(--dim)}
.d-lc:hover{color:var(--ca)}
.d-pmeta{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;font:500 11.5px var(--mono);color:var(--dim)}
.d-lv{font:600 11.5px var(--mono)}
.d-bdg{height:20px;padding:0 7px;display:inline-flex;align-items:center;border-radius:4px;border:1px solid var(--line);font:600 9.5px var(--mono);letter-spacing:.1em;color:var(--dim)}
.d-bdg.ml{border-color:transparent;background:var(--cab);color:var(--ca)}
.d-bdg.prem{border-color:color-mix(in oklab,var(--warn) 50%,var(--line));color:var(--warn)}
.d-of{font:500 11.5px var(--mono);color:var(--dim)}
.d-cos{display:flex;flex-wrap:wrap;gap:5px}
.d-co{height:22px;padding:0 8px;display:inline-flex;align-items:center;border-radius:4px;border:1px solid var(--line2);font:500 11px var(--mono);color:var(--mut)}
.d-co.hot{border-color:transparent;background:color-mix(in oklch,var(--fn) 13%,transparent);color:var(--fn)}
.d-co.more{border-style:dashed;color:var(--dim);cursor:pointer}
.d-pside{display:flex;flex-direction:column;align-items:flex-end;gap:10px}
.d-when{font:500 11px var(--mono);color:var(--dim);white-space:nowrap}
.d-when.due{color:var(--vio)}
.d-acts{display:flex;gap:6px;align-items:center}
.d-acts button,.d-acts a{height:28px;min-width:30px;padding:0 9px;display:inline-grid;place-items:center;border:1px solid var(--line);border-radius:6px;font:600 12px var(--mono);color:var(--mut)}
.d-acts button:hover,.d-acts a:hover{color:var(--fg);border-color:var(--ca)}
.d-acts .solo:hover{color:var(--grn);border-color:var(--grn)}
.d-acts .fail:hover{color:var(--bad);border-color:var(--bad)}
.d-prac{grid-column:2/-1;display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding-top:10px;border-top:1px dashed var(--line2)}
.d-prac>span{font:600 10px var(--mono);letter-spacing:.16em;color:var(--dim);margin-right:4px}
.d-pp{height:26px;padding:0 10px 0 8px;display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line2);border-radius:5px;background:var(--bg);font-size:12.5px;color:var(--mut)}
.d-pp:hover{border-color:var(--line);color:var(--fg)}
.d-pp i{width:8px;height:8px;border-radius:50%;border:1.5px solid var(--line);flex:none}
.d-pp i.solo{background:var(--grn);border-color:var(--grn)}
.d-pp i.help{border-color:var(--grn);background:var(--grn-bg)}
.d-pp i.fail{border-color:var(--bad)}
.d-pp small{font:600 10.5px var(--mono)}
.d-more{align-self:center;height:34px;padding:0 16px;border:1px dashed var(--line);border-radius:6px;font:500 12px var(--mono);color:var(--dim)}
.d-more:hover{color:var(--ca);border-color:var(--ca)}
.d-flabel{cursor:default}
.d-flabel a{font:500 11px var(--mono);letter-spacing:.14em;color:var(--ca)}
/* ---- the rail: activity <-> filters ---- */
.d-railtabs{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line2);border-radius:8px;background:var(--panel);padding:3px;gap:3px}
.d-railtabs button{height:34px;border-radius:6px;font:500 12px var(--mono);color:var(--dim);display:flex;align-items:center;justify-content:center;gap:8px}
.d-railtabs button.on{background:var(--raise);color:var(--fg)}
.d-railtabs i{font-style:normal;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--ca);color:var(--on-acc);font:600 10.5px/18px var(--mono);text-align:center}
.d-rail-in{display:flex;flex-direction:column;gap:16px;animation:d-in .18s ease-out}
@keyframes d-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.d-sum{display:flex;flex-direction:column;gap:10px}
.d-sum .big{display:flex;align-items:baseline;gap:8px}
.d-sum .big b{font:700 28px var(--sans);letter-spacing:-.02em;line-height:1}
.d-sum .big span{font:500 12px var(--mono);color:var(--dim)}
.d-sum .bar{height:5px;border-radius:3px;background:var(--line2);overflow:hidden}
.d-sum .bar i{display:block;height:100%;background:var(--ca)}
.d-sum button{align-self:flex-start;font:500 12px var(--mono);color:var(--ca)}
.rbox h4 small{font:500 11px var(--mono);letter-spacing:0;color:var(--dim)}
.d-opts{display:flex;flex-direction:column;gap:2px;margin-inline:-6px}
.d-opt{display:flex;align-items:center;gap:10px;padding:6px;border-radius:6px;font-size:13px;color:var(--mut);text-align:left;width:100%}
.d-opt:hover{background:var(--raise);color:var(--fg)}
.d-opt .bx{width:15px;height:15px;border:1.5px solid var(--line);border-radius:4px;flex:none;display:grid;place-items:center}
.d-opt.on .bx{background:var(--ca);border-color:var(--ca)}
.d-opt.on .bx::after{content:"";width:6px;height:6px;border-radius:1px;background:var(--on-acc)}
.d-opt.on{color:var(--fg)}
.d-opt .sw{width:9px;height:9px;border-radius:2px;flex:none}
.d-opt .c{margin-left:auto;font:500 11px var(--mono);color:var(--dim)}
.d-opt.zero{opacity:.35;pointer-events:none}
.d-opt .d{display:flex;flex-direction:column;gap:1px;min-width:0}
.d-opt .d small{font:400 11px var(--sans);color:var(--dim)}
.d-sub{margin:2px 0 4px 17px;padding-left:8px;border-left:1px dashed var(--line2);display:flex;flex-direction:column;gap:2px}
.d-sub .d-opt{font-size:12.5px;padding:4px 6px}
.d-linkmore{align-self:flex-start;font:500 11.5px var(--mono);color:var(--ca);padding:4px 0}
.d-tsearch{height:32px;border:1px solid var(--line2);border-radius:6px;background:var(--bg);padding:0 10px;font:400 12.5px var(--mono);width:100%;outline:none;margin-bottom:8px}
.d-tsearch:focus{border-color:var(--ca)}
.d-tog{display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:13px;color:var(--mut);padding:5px 0}
.d-tog small{display:block;font:400 11px var(--sans);color:var(--dim)}
.d-sw{width:32px;height:18px;border-radius:9px;background:var(--line);position:relative;flex:none}
.d-sw::after{content:"";position:absolute;top:2px;left:2px;width:14px;height:14px;border-radius:50%;background:var(--fg);transition:left .15s}
.d-sw.on{background:var(--ca)}.d-sw.on::after{left:16px;background:var(--on-acc)}
.d-toast{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);background:var(--raise);border:1px solid var(--line);border-radius:8px;padding:10px 16px;font:500 12.5px var(--mono);color:var(--fg);box-shadow:0 12px 32px var(--shadow);z-index:60}
.d-tip{position:fixed;pointer-events:none;background:var(--raise);border:1px solid var(--line);border-radius:6px;padding:6px 9px;font:500 11px var(--mono);color:var(--fg);box-shadow:0 8px 20px var(--shadow);z-index:50;max-width:320px}
.d-notes{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;padding-block:40px 56px}
.d-notes>div{border-top:2px solid var(--line);padding-top:12px;display:flex;flex-direction:column;gap:6px}
.d-notes .lab{font:600 10.5px var(--mono);letter-spacing:.14em;color:var(--ca)}
.d-notes p{margin:0;color:var(--mut);font-size:13.5px;line-height:1.6}
@media (max-width:900px){.d-goals{grid-template-columns:1fr}.d-pcard{grid-template-columns:34px minmax(0,1fr)}.d-pside{grid-column:2;flex-direction:row;align-items:center;justify-content:space-between}}
'''

body = r'''
<div class="mk-bar"><b>MOCKUP</b><a class="on" href="dsa-tracker.html">1 · Home</a><a href="problem.html">2 · Problem page</a><a href="pattern.html">3 · Pattern lesson</a><span style="margin-left:auto">progress shown is example data</span></div>
<header class="hdr">
  <a class="logo" href="#" aria-label="anneal home"><span class="mk"><span style="background:var(--acc)"></span><span style="background:var(--vio)"></span><span style="background:var(--grn)"></span><span style="box-shadow:inset 0 0 0 1px var(--line)"></span></span><b>anneal<i>.genuinebasil.dev</i></b></a>
  <nav class="nav" aria-label="Sections"><a class="on" href="#" style="color:var(--acc)">DSA</a><a href="#" style="color:var(--vio)">Rust</a><span style="color:var(--line)">|</span><span class="nav-later">Library</span><span class="nav-later">Mock interview</span><a href="#" style="color:var(--dim)">Progress</a><span class="nav-later">Readiness</span></nav>
  <div class="hdr-r"><span class="rd">SOLVED <b id="solvedN">–</b></span><button class="thm" id="thm" aria-label="Toggle theme"><span></span></button><span class="av">gb</span></div>
</header>
<main class="page" style="--ca:var(--acc);--cab:var(--acc-bg)">
<div class="wrap">
  <section class="cat-top">
    <div style="min-width:0;flex:1 1 520px">
      <div class="eyebrow"><span style="color:var(--ca)">DSA</span><span>/</span><span>NEETCODE</span></div>
      <h1 class="h1 md">Every NeetCode problem, <span style="color:var(--ca)">tracked.</span></h1>
      <p class="lead">Solve on LeetCode, log it here. Anneal keeps the schedule: reviews, streak and readiness. Learn each pattern once, then practise it.</p>
    </div>
    <div class="cat-stats" id="heroStats"></div>
  </section>
  <section class="d-goals" id="goals" aria-label="Goals"></section>
  <div class="cat-body">
    <div class="cat-main">
      <section class="nextup" aria-label="Next up" id="nextup"></section>
      <div class="cat-tools">
        <label class="cat-search"><span aria-hidden="true" style="color:var(--dim)">⌕</span><input id="q" type="search" placeholder="search title, number or tag…" aria-label="Search problems"><kbd>/</kbd></label>
        <div class="seg" role="group" aria-label="View" id="viewSeg"></div>
        <button class="d-fbtn" id="fbtn" aria-pressed="false">⚙ Filters <i id="fcount" hidden></i><kbd>f</kbd></button>
      </div>
      <div class="flabel">LIST</div>
      <div class="fchips" id="lists"></div>
      <div class="d-active" id="active" hidden></div>
      <div id="content" style="display:flex;flex-direction:column;gap:28px"></div>
    </div>
    <aside class="cat-rail" id="rail" aria-label="Activity and filters"></aside>
  </div>
  <section class="d-notes">
    <div><span class="lab">THE RAIL SWAPS</span><p><b>Filters</b> (or press <b>f</b>) replaces the Activity panels in the right rail with one long card per filter; <b>Activity</b> brings them back. Every count already accounts for the other filters. Applying a filter doesn't hide the rail's own state: the tab shows how many are active.</p></div>
    <div><span class="lab">PATTERNS ↔ PROBLEMS</span><p>The grid is the catalog you know, one card per NeetCode pattern, with its lesson one click away. Switch to <b>problems</b> for long cards: each must-learn problem carries the practice problems that reuse its idea underneath it.</p></div>
    <div><span class="lab">GOALS ARE SHORTCUTS</span><p>The three goal cards double as list switches: NeetCode 150, the new ideas in the 250 (must-learn problems the 150 doesn't cover), and All. Blind 75 and the full 250 are in the list chips.</p></div>
  </section>
</div>
</main>
<div class="d-tip" id="tip" hidden></div>
<div class="d-toast" id="toast" hidden></div>
<script>
const DATA = __DATA__;
const GROUPS = __GROUPS__;
const ORDER = __ORDER__;
const BLURB = __BLURB__;
const TECH = __TECH__;
const DIFF = { e: ['Easy', 'var(--grn)'], m: ['Medium', 'var(--warn)'], h: ['Hard', 'var(--bad)'] };
const MIN = { e: 12, m: 25, h: 45 };
const LISTS = [['blind75', 'Blind 75'], ['neetcode150', 'NeetCode 150'], ['neetcode250', 'NeetCode 250'], ['new250', 'New ideas in the 250'], ['all', 'NeetCode All']];
const LRANK = { blind75: 0, neetcode150: 1, neetcode250: 2, all: 3 };
const SCOPE = {
  blind75: (p) => p.l.includes('blind75'),
  neetcode150: (p) => p.l.includes('neetcode150'),
  neetcode250: (p) => p.l.includes('neetcode250'),
  new250: (p) => p.l.includes('neetcode250') && !p.l.includes('neetcode150') && p.r === 'm',
  all: () => true,
};
const byId = Object.fromEntries(DATA.map((p) => [p.i, p]));
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const $ = (s) => document.querySelector(s);

// Example progress (deterministic): the early NeetCode 150 patterns mostly solved, some reviews due.
const STATE = {};
let seed = 7; const rnd = () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);
for (const p of DATA) {
  if (!p.l.includes('neetcode150')) { if (p.l.includes('neetcode250') && rnd() < 0.08) STATE[p.i] = { s: 'solo', due: rnd() < 0.3 ? 0 : 9 }; continue; }
  const k = ORDER.indexOf(p.p);
  const odds = k < 3 ? 0.85 : k < 7 ? 0.45 : k < 10 ? 0.12 : 0;
  if (rnd() < odds) { const r = rnd(); STATE[p.i] = { s: r < 0.7 ? 'solo' : r < 0.92 ? 'help' : 'fail', due: rnd() < 0.18 ? 0 : Math.ceil(rnd() * 20) }; }
}
const isSolved = (p) => STATE[p.i] && STATE[p.i].s !== 'fail';
const statusOf = (p) => { const s = STATE[p.i]; return !s ? 'new' : s.due === 0 && s.s !== 'fail' ? 'due' : s.s === 'fail' ? 'retry' : 'solved'; };
const STATUS_LABEL = { new: 'Not started', solved: 'Solved', due: 'Due for review', retry: "Couldn't yet" };

const F = { list: 'neetcode150', view: 'patterns', railTab: 'activity', status: new Set(), role: new Set(), diff: new Set(), patterns: new Set(), groups: new Set(), companies: new Set(), recent: false, tags: new Set(), hidePremium: false, q: '' };
const UI = { moreTags: false, morePatterns: false, tagQ: '', open: new Set() };
const tests = {
  list: (p) => SCOPE[F.list](p),
  status: (p) => !F.status.size || F.status.has(statusOf(p)),
  role: (p) => !F.role.size || F.role.has(p.r),
  diff: (p) => !F.diff.size || F.diff.has(p.d),
  patterns: (p) => !F.patterns.size || F.patterns.has(p.p),
  company: (p) => (!F.groups.size && !F.companies.size && !F.recent) || p.co.some(([n, g, r]) => (F.companies.size ? F.companies.has(n) : F.groups.size ? F.groups.has(g) : true) && (!F.recent || r)),
  tags: (p) => !F.tags.size || [...F.tags].every((t) => p.tg.includes(t)),
  premium: (p) => !F.hidePremium || !p.pr,
  q: (p) => !F.q || (p.t + ' ' + p.n + ' ' + p.tg.join(' ')).toLowerCase().includes(F.q.toLowerCase()),
};
const passing = (except) => DATA.filter((p) => Object.entries(tests).every(([k, f]) => k === except || f(p)));
const cnt = (items, key) => { const m = new Map(); for (const p of items) for (const v of [].concat(key(p))) m.set(v, (m.get(v) || 0) + 1); return m; };
const activeCount = () => F.status.size + F.role.size + F.diff.size + F.patterns.size + F.groups.size + F.companies.size + (F.recent ? 1 : 0) + F.tags.size + (F.hidePremium ? 1 : 0) + (F.q ? 1 : 0);
const flip = (set, v) => { set.has(v) ? set.delete(v) : set.add(v); render(); };
const rank = (p) => [LRANK[p.l[0]], p.n];
const cmp = (a, b) => { const x = rank(a), y = rank(b); return x[0] - y[0] || x[1] - y[1]; };

let toastTimer;
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => (t.hidden = true), 2600); }
function log(p, kind) { STATE[p.i] = { s: kind, due: kind === 'solo' ? 21 : kind === 'help' ? 3 : 1 }; render(); }
function openProblem(p) { p.s === 'course-schedule' ? (location.href = 'problem.html') : toast('Mockup: only Course Schedule has its problem page written out.'); }
const hours = (m) => (m >= 600 ? `~${Math.round(m / 60)}h` : `~${(m / 60).toFixed(1).replace(/\.0$/, '')}h`);

// ---------------------------------------------------------------- top: hero, goals, next up
function renderTop() {
  const left150 = DATA.filter((p) => SCOPE.neetcode150(p) && !isSolved(p));
  $('#heroStats').innerHTML = `<div><b>${ORDER.length}</b><span>PATTERNS</span></div><div><b>${DATA.length}</b><span>PROBLEMS</span></div><div><b>${hours(left150.reduce((n, p) => n + MIN[p.d], 0))}</b><span>TO FINISH THE 150</span></div>`;
  $('#solvedN').textContent = DATA.filter(isSolved).length;
  const defs = [['neetcode150', 'GOAL · NEETCODE 150', 'var(--acc)'], ['new250', 'NEW IDEAS IN THE 250', 'var(--vio)'], ['all', 'NEETCODE ALL', 'var(--grn)']];
  $('#goals').innerHTML = defs.map(([k, label, c]) => {
    const items = DATA.filter(SCOPE[k]); const done = items.filter(isSolved).length; const ml = items.filter((p) => p.r === 'm' && !isSolved(p)).length;
    const note = k === 'all' ? `<b>${DATA.filter((p) => p.pr).length}</b> need LeetCode Premium` : k === 'new250' ? `must-learn problems the 150 doesn't cover` : `<b>${ml}</b> must-learn left`;
    return `<button class="d-goal${F.list === k ? ' on' : ''}" style="--gc:${c}" data-list="${k}" aria-pressed="${F.list === k}"><span>${label}</span><b>${done}<small>/ ${items.length}</small></b><div class="bar"><i style="width:${(done / items.length) * 100}%;background:${c}"></i></div><em>${note}</em></button>`;
  }).join('');
  const due = DATA.filter((p) => statusOf(p) === 'due').length;
  const next = byId['lc-course-schedule'];
  $('#nextup').innerHTML = `
    <div class="nu-ring"><svg viewBox="0 0 78 78" aria-hidden="true"><circle cx="39" cy="39" r="34" fill="none" stroke="var(--line2)" stroke-width="5"/><circle cx="39" cy="39" r="34" fill="none" stroke="var(--ca)" stroke-width="5" stroke-linecap="round" stroke-dasharray="${(2 * Math.PI * 34 * 6 / 7).toFixed(1)} 214"/></svg><div><b>6</b><span>DAYS</span></div></div>
    <div class="nu-k"><i></i><span style="color:var(--ca)">NEXT UP</span><span style="color:var(--dim)">GRAPHS · TOPOLOGICAL SORT</span></div>
    <div class="nu-sub"><b>6-day streak</b>, keep it going. It's the next must-learn problem in the NeetCode 150${due ? `, and <b>${due}</b> reviews are due too` : ''}.</div>
    <div class="nu-main"><h2>${esc(next.t)}</h2><p>Courses are nodes and prerequisites are edges, so "can you finish?" is a cycle check on a directed graph. Learn the pattern, then the practice problems that reuse it.</p>
      <div class="pills"><span class="cpill" style="color:var(--warn)">medium</span><span class="cpill" style="color:var(--ca)">must learn</span><span class="cpill">Graphs</span><span class="cpill">~25m</span></div></div>
    <div class="nu-gain"><span>NEETCODE 150 · ${Math.round((DATA.filter((p) => SCOPE.neetcode150(p) && isSolved(p)).length / 150) * 100)}% DONE</span><span style="color:var(--ca)">+0.7% IF UNASSISTED</span></div>
    <div class="nu-bar"><span style="width:23%;background:var(--ca)"></span><span style="width:.7%;background:var(--ca);opacity:.4"></span></div>
    <a class="nu-go" href="problem.html">Open the problem page →</a>
    <div style="grid-column:1/-1;display:flex;gap:18px;font:500 12px var(--mono);color:var(--dim)"><a href="https://leetcode.com/problems/course-schedule/" target="_blank" rel="noreferrer" style="color:var(--mut)">solve on LeetCode ↗</a><a href="https://youtu.be/${next.v}" target="_blank" rel="noreferrer" style="color:var(--mut)">▶ NeetCode's video</a></div>`;
}

// ---------------------------------------------------------------- tools, list chips, active filters
function renderTools() {
  $('#viewSeg').innerHTML = [['patterns', '▦ patterns'], ['problems', '☰ problems']].map(([v, l]) => `<button class="${F.view === v ? 'on' : ''}" aria-pressed="${F.view === v}" data-view="${v}">${l}</button>`).join('');
  const n = activeCount(); const fb = $('#fbtn');
  fb.classList.toggle('on', F.railTab === 'filters'); fb.setAttribute('aria-pressed', F.railTab === 'filters');
  $('#fcount').hidden = !n; $('#fcount').textContent = n;
  $('#lists').innerHTML = LISTS.map(([k, l]) => { const c = DATA.filter((p) => SCOPE[k](p) && Object.entries(tests).every(([t, f]) => t === 'list' || f(p))).length; return `<button class="fchip${F.list === k ? ' on' : ''}" aria-pressed="${F.list === k}" data-list="${k}">${l}<small>${c}</small></button>`; }).join('');
  const chips = [];
  const add = (label, off) => chips.push(`<span class="d-chip">${esc(label)}<button aria-label="Remove ${esc(label)}" data-off="${off}">×</button></span>`);
  F.status.forEach((v) => add(STATUS_LABEL[v], `status:${v}`)); F.role.forEach((v) => add(v === 'm' ? 'Must learn' : 'Practice', `role:${v}`));
  F.diff.forEach((v) => add(DIFF[v][0], `diff:${v}`)); F.patterns.forEach((v) => add(v, `patterns:${v}`));
  F.groups.forEach((v) => add(GROUPS[v], `groups:${v}`)); F.companies.forEach((v) => add(v, `companies:${v}`));
  if (F.recent) add('Asked in the last 6 months', 'recent'); F.tags.forEach((v) => add('#' + v, `tags:${v}`));
  if (F.hidePremium) add('No Premium', 'premium'); if (F.q) add(`“${F.q}”`, 'q');
  const act = $('#active'); act.hidden = !chips.length;
  act.innerHTML = chips.join('') + (chips.length ? `<button class="d-clear" data-clear>clear all</button>` : '');
}

// ---------------------------------------------------------------- content: pattern cards or long problem cards
function patternCard(pat, idx) {
  const scope = DATA.filter((p) => p.p === pat && tests.list(p));
  if (!scope.length) return '';
  const match = scope.filter((p) => Object.entries(tests).every(([k, f]) => k === 'list' || f(p)));
  const done = scope.filter(isSolved).length; const ml = scope.filter((p) => p.r === 'm' && !isSolved(p)).length;
  const left = scope.filter((p) => !isSolved(p)).reduce((n, p) => n + MIN[p.d], 0);
  const bands = ['e', 'm', 'h'].map((d) => ({ d, t: scope.filter((p) => p.d === d), })).filter((b) => b.t.length).map((b) => `<span style="flex:${b.t.length}"><i style="width:${(b.t.filter(isSolved).length / b.t.length) * 100}%;background:${DIFF[b.d][1]}"></i></span>`).join('');
  const next = scope.filter((p) => !isSolved(p)).sort((a, b) => (a.r === 'm' ? 0 : 1) - (b.r === 'm' ? 0 : 1) || cmp(a, b))[0];
  const state = pat === 'Graphs' ? 'cur' : done === scope.length ? 'done' : '';
  const badge = state === 'cur' ? '<span class="tc-badge" style="background:var(--cab);color:var(--ca)">NOW ON</span>' : state === 'done' ? '<span class="tc-badge" style="background:var(--grn-bg);color:var(--grn)">DONE</span>' : '';
  const filtered = activeCount() > 0;
  return `<div class="tcard ${state}${filtered && !match.length ? ' dim' : ''}" data-pat="${esc(pat)}" tabindex="0" role="button" aria-label="${esc(pat)}: show its problems">
    <div class="tc-top"><span class="tc-num">${String(idx + 1).padStart(2, '0')}</span><span class="tc-kind">PATTERN · ${LISTS.find((l) => l[0] === F.list)[1].toUpperCase()}</span>${badge}</div>
    <h3>${esc(pat)}</h3><p>${esc(BLURB[pat])}</p>
    <div class="tc-meta"><b>${scope.length}</b> problems · <b>${scope.filter((p) => p.r === 'm').length}</b> must learn · ${hours(left)} left${filtered ? ` · <span class="tc-hit">${match.length} match</span>` : ''}</div>
    <div class="tc-tags">${TECH[pat].map((t) => `<span class="cpill">${esc(t)}</span>`).join('')}</div>
    <div class="tc-prog"><span>progress</span><span><b>${done} / ${scope.length}</b> · ${Math.round((done / scope.length) * 100)}%</span></div>
    <div class="tc-bar">${bands}</div>
    <div class="tc-foot"><span>${next ? `next · ${esc(next.t)}` : 'all solved · reviews keep it fresh'}</span><span class="tc-acts"><a class="tc-go ghost" href="pattern.html" data-lesson title="The pattern lesson">lesson</a><span class="tc-go">problems ›</span></span></div>
  </div>`;
}

function problemCard(p, items, child) {
  const st = STATE[p.i]; const status = statusOf(p); const teacher = p.of && byId[p.of];
  const kids = child ? [] : items.filter((c) => c.of === p.i);
  const lists = p.l.filter((l) => l !== 'all').map((l) => ({ blind75: 'B75', neetcode150: '150', neetcode250: '250' })[l]);
  const cos = p.co.slice(0, 5).map(([n, , r]) => `<span class="d-co${r ? ' hot' : ''}">${esc(n)}</span>`).join('') + (p.co.length > 5 ? `<span class="d-co more" data-more="${esc(p.co.slice(5).map(([n]) => n).join(', '))}">+${p.co.length - 5}</span>` : '');
  const when = status === 'due' ? '<span class="d-when due">review due today</span>' : st && st.s !== 'fail' ? `<span class="d-when">review in ${st.due}d</span>` : st ? '<span class="d-when">retry soon</span>' : '';
  return `<article class="d-pcard${status === 'due' ? ' due' : ''}">
    <span class="d-st ${st ? st.s : ''}" title="${STATUS_LABEL[status]}">${st ? (st.s === 'solo' ? '✓' : st.s === 'help' ? '½' : '✗') : ''}</span>
    <div class="d-pbody">
      <div class="d-ph"><span class="d-pnum">#${p.n}</span><button class="d-ptitle" data-open="${p.i}">${esc(p.t)}</button><a class="d-lc" href="https://leetcode.com/problems/${p.s}/" target="_blank" rel="noreferrer">LeetCode ↗</a>${p.pr ? '<span class="d-bdg prem" title="Needs LeetCode Premium">PREMIUM</span>' : ''}</div>
      <div class="d-pmeta"><span class="d-lv" style="color:${DIFF[p.d][1]}">${DIFF[p.d][0]}</span>${p.r === 'm' ? '<span class="d-bdg ml">MUST LEARN</span>' : '<span class="d-bdg">PRACTICE</span>'}${lists.length ? `<span class="d-bdg" title="in ${lists.join(', ')}">${lists[0]}</span>` : ''}<span>${esc(p.tg.slice(0, 3).join(' · '))}</span>${teacher && !child && !items.includes(teacher) ? `<span class="d-of">· practice of ${esc(teacher.t)}</span>` : ''}</div>
      ${p.co.length ? `<div class="d-cos">${cos}</div>` : ''}
    </div>
    <div class="d-pside">${when}<div class="d-acts">${p.v ? `<a href="https://youtu.be/${p.v}" target="_blank" rel="noreferrer" title="NeetCode's video">▶</a>` : ''}<button class="solo" title="Solved on my own" data-log="${p.i}:solo">✓</button><button title="Solved with help" data-log="${p.i}:help">½</button><button class="fail" title="Couldn't solve it yet" data-log="${p.i}:fail">✗</button></div></div>
    ${kids.length ? `<div class="d-prac"><span>PRACTICE THIS IDEA · ${kids.length}</span>${kids.map((c) => `<a class="d-pp" href="https://leetcode.com/problems/${c.s}/" target="_blank" rel="noreferrer" title="${esc(c.t)} · ${DIFF[c.d][0]}"><i class="${STATE[c.i] ? STATE[c.i].s : ''}"></i>${esc(c.t)}<small style="color:${DIFF[c.d][1]}">${DIFF[c.d][0][0]}</small></a>`).join('')}</div>` : ''}
  </article>`;
}

function renderContent() {
  const el = $('#content');
  const items = DATA.filter((p) => Object.values(tests).every((f) => f(p)));
  if (F.view === 'patterns') {
    const cards = ORDER.map((pat, i) => patternCard(pat, i)).join('');
    el.innerHTML = `<div class="flabel">${F.patterns.size || activeCount() ? `PATTERNS · ${items.length} PROBLEMS MATCH` : 'ALL PATTERNS · IN RECOMMENDED ORDER'}</div><div class="tgrid">${cards}</div>`;
    return;
  }
  if (!items.length) { el.innerHTML = `<div class="cat-empty">No problems match. <button style="color:var(--ca)" data-clear>Clear filters</button></div>`; return; }
  const ids = new Set(items.map((p) => p.i));
  el.innerHTML = ORDER.map((pat) => {
    const inPat = items.filter((p) => p.p === pat); if (!inPat.length) return '';
    const roots = inPat.filter((p) => !(p.of && ids.has(p.of))).sort((a, b) => (a.r === 'm' ? 0 : 1) - (b.r === 'm' ? 0 : 1) || cmp(a, b));
    const cap = UI.open.has(pat) ? roots.length : 8;
    return `<div class="d-group"><div class="flabel d-flabel">${esc(pat.toUpperCase())} · ${inPat.length}<a href="pattern.html">lesson ›</a></div>
      <div class="d-plist" style="margin-top:14px">${roots.slice(0, cap).map((p) => problemCard(p, items)).join('')}${roots.length > cap ? `<button class="d-more" data-more-group="${esc(pat)}">show ${roots.length - cap} more</button>` : ''}</div></div>`;
  }).join('');
}

// ---------------------------------------------------------------- the rail
function opt(label, n, on, attrs, extra) {
  return `<button class="d-opt${on ? ' on' : ''}${n === 0 && !on ? ' zero' : ''}" ${attrs}>${extra && extra.sw ? `<span class="sw" style="background:${extra.sw}"></span>` : '<span class="bx"></span>'}<span class="d">${esc(label)}${extra && extra.hint ? `<small>${esc(extra.hint)}</small>` : ''}</span><span class="c">${n}</span></button>`;
}
function renderRail() {
  const n = activeCount();
  const tabs = `<div class="d-railtabs" role="tablist"><button class="${F.railTab === 'activity' ? 'on' : ''}" role="tab" data-rail="activity">Activity</button><button class="${F.railTab === 'filters' ? 'on' : ''}" role="tab" data-rail="filters">Filters${n ? ` <i>${n}</i>` : ''}</button></div>`;
  let inner;
  if (F.railTab === 'activity') {
    const week = [2, 0, 3, 1, 4, 2, 1];
    const shade = (k) => (k === 0 ? 'var(--line2)' : `color-mix(in oklch, var(--ca) ${Math.min(100, 25 + k * 15)}%, transparent)`);
    const due = DATA.filter((p) => statusOf(p) === 'due').slice(0, 4);
    const recent = [['Course Schedule', 'solved', 'var(--grn)', 'Graphs · on your own'], ['Number of Islands', 'solved', 'var(--grn)', 'Graphs · on your own'], ['Clone Graph', 'help', 'var(--acc)', 'Graphs · with help'], ['Pacific Atlantic Water Flow', 'fail', 'var(--bad)', 'Graphs · not yet']];
    const meters = [['Arrays & Hashing', 92], ['Two Pointers', 88], ['Sliding Window', 74], ['Stack', 61], ['Binary Search', 45], ['Graphs', 38]];
    const pc = (v) => (v >= 70 ? 'var(--grn)' : v >= 40 ? 'var(--warn)' : 'var(--bad)');
    inner = `<div class="rbox"><h4><span>THIS WEEK</span><span style="color:var(--ca)">13 SOLVED</span></h4><div class="week">${['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => `<div><i style="background:${shade(week[i])}" title="${week[i]} solved"></i>${d}</div>`).join('')}</div><div class="rstat"><span>unassisted</span><b>10 of 13</b></div></div>
      <div class="rbox"><h4><span>RECENT</span></h4>${recent.map(([t, , c, d]) => `<div class="ritem"><i style="background:${c}"></i><span>${t}</span><small>${d}</small></div>`).join('')}</div>
      <div class="rbox"><h4><span>RE-SOLVE DUE</span><a href="#" style="color:var(--vio)" data-statusdue>${DATA.filter((p) => statusOf(p) === 'due').length} →</a></h4>${due.map((p) => `<div class="ritem"><i style="background:var(--vio)"></i><span>${esc(p.t)}</span><small>${esc(p.p.split(' ')[0])} · today</small></div>`).join('')}</div>
      <div class="rbox"><h4><span>READINESS</span><small>by pattern</small></h4>${meters.map(([t, v]) => `<div class="rmeter"><span>${t}</span><em style="color:${pc(v)}">${v}%</em><i><b style="width:${v}%;background:${pc(v)}"></b></i></div>`).join('')}</div>`;
  } else {
    const shown = passing('').length; const inList = DATA.filter(SCOPE[F.list]).length; const listName = LISTS.find((l) => l[0] === F.list)[1];
    const sc = cnt(passing('status'), statusOf), rc = cnt(passing('role'), (p) => p.r), dc = cnt(passing('diff'), (p) => p.d), pcn = cnt(passing('patterns'), (p) => p.p);
    const pats = ORDER.filter((p) => pcn.get(p) || F.patterns.has(p));
    const base = passing('company');
    const tc = cnt(passing('tags'), (p) => p.tg); const allTags = [...tc.entries()].sort((a, b) => b[1] - a[1]).map(([t]) => t);
    const tagList = UI.tagQ ? allTags.filter((t) => t.toLowerCase().includes(UI.tagQ.toLowerCase())) : [...new Set([...F.tags, ...(UI.moreTags ? allTags : allTags.slice(0, 10))])];
    const tog = (key, label, hint, on) => `<div class="d-tog"><span>${label}${hint ? `<small>${hint}</small>` : ''}</span><button class="d-sw${on ? ' on' : ''}" data-tog="${key}" aria-pressed="${on}" aria-label="${label}"></button></div>`;
    inner = `<div class="rbox d-sum"><div class="big"><b>${shown}</b><span>of ${inList} in ${listName}</span></div><div class="bar"><i style="width:${(shown / inList) * 100}%"></i></div>${n ? '<button data-clear>reset all filters</button>' : '<span style="font:500 12px var(--mono);color:var(--dim)">no filters on</span>'}</div>
      <div class="rbox"><h4><span>STATUS</span></h4><div class="d-opts">${[['new', 'var(--line)'], ['solved', 'var(--grn)'], ['due', 'var(--vio)'], ['retry', 'var(--bad)']].map(([k, c]) => opt(STATUS_LABEL[k], sc.get(k) || 0, F.status.has(k), `data-f="status:${k}"`, { sw: c })).join('')}</div></div>
      <div class="rbox"><h4><span>IDEA</span></h4><div class="d-opts">${opt('Must learn', rc.get('m') || 0, F.role.has('m'), 'data-f="role:m"', { hint: 'teaches a new idea' })}${opt('Practice', rc.get('p') || 0, F.role.has('p'), 'data-f="role:p"', { hint: 'reuses an idea you learned' })}</div></div>
      <div class="rbox"><h4><span>DIFFICULTY</span></h4><div class="d-opts">${['e', 'm', 'h'].map((k) => opt(DIFF[k][0], dc.get(k) || 0, F.diff.has(k), `data-f="diff:${k}"`, { sw: DIFF[k][1] })).join('')}</div></div>
      <div class="rbox"><h4><span>PATTERN</span><small>${pats.length}</small></h4><div class="d-opts">${(UI.morePatterns ? pats : pats.slice(0, 7)).map((p) => opt(p, pcn.get(p) || 0, F.patterns.has(p), `data-f="patterns:${esc(p)}"`)).join('')}</div>${pats.length > 7 ? `<button class="d-linkmore" data-ui="morePatterns">${UI.morePatterns ? 'show fewer' : `+${pats.length - 7} more`}</button>` : ''}</div>
      <div class="rbox"><h4><span>COMPANIES</span><small>pick a group, then narrow</small></h4><div class="d-opts">${GROUPS.map((g, gi) => {
        const inG = base.filter((p) => p.co.some(([, cg]) => cg === gi));
        const open = F.groups.has(gi);
        const sub = open ? `<div class="d-sub">${[...cnt(inG, (p) => p.co.filter(([, cg]) => cg === gi).map(([n]) => n)).entries()].sort((a, b) => b[1] - a[1]).slice(0, 9).map(([n, k]) => opt(n, k, F.companies.has(n), `data-f="companies:${esc(n)}"`)).join('')}</div>` : '';
        return opt(g, inG.length, open, `data-f="groups:${gi}"`) + sub;
      }).join('')}</div>${tog('recent', 'Asked in the last 6 months', 'for the company filters above', F.recent)}</div>
      <div class="rbox"><h4><span>LEETCODE TAGS</span><small>all of</small></h4><input class="d-tsearch" data-keep="tagq" placeholder="find a tag…" value="${esc(UI.tagQ)}"><div class="d-opts">${tagList.map((t) => opt(t, tc.get(t) || 0, F.tags.has(t), `data-f="tags:${esc(t)}"`)).join('')}</div>${!UI.tagQ && allTags.length > 10 ? `<button class="d-linkmore" data-ui="moreTags">${UI.moreTags ? 'show fewer' : `+${allTags.length - 10} more`}</button>` : ''}</div>
      <div class="rbox"><h4><span>OPTIONS</span></h4>${tog('premium', 'Hide LeetCode Premium', `${DATA.filter((p) => p.pr).length} problems need it`, F.hidePremium)}</div>`;
  }
  $('#rail').innerHTML = tabs + `<div class="d-rail-in" data-tab="${F.railTab}">${inner}</div>`;
}

// ---------------------------------------------------------------- events
function render(keep) {
  const focused = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.keep : null;
  const pos = focused ? document.activeElement.selectionStart : 0;
  renderTop(); renderTools(); renderContent(); renderRail();
  if (focused) { const e = document.querySelector(`[data-keep="${focused}"]`); if (e) { e.focus(); e.setSelectionRange(pos, pos); } }
}
function off(spec) {
  const [k, v] = spec.split(':');
  if (k === 'recent') F.recent = false; else if (k === 'premium') F.hidePremium = false; else if (k === 'q') { F.q = ''; $('#q').value = ''; }
  else { const set = F[k]; set.delete(k === 'groups' ? Number(v) : v); }
  render();
}
function clearAll() { for (const k of ['status', 'role', 'diff', 'patterns', 'groups', 'companies', 'tags']) F[k].clear(); F.recent = false; F.hidePremium = false; F.q = ''; $('#q').value = ''; UI.tagQ = ''; render(); }
document.addEventListener('click', (e) => {
  const t = e.target.closest('button, a, .tcard'); if (!t) return;
  if (t.dataset.list) { F.list = t.dataset.list; render(); return; }
  if (t.dataset.view) { F.view = t.dataset.view; render(); return; }
  if (t.dataset.rail) { F.railTab = t.dataset.rail; render(); return; }
  if (t.id === 'fbtn') { F.railTab = F.railTab === 'filters' ? 'activity' : 'filters'; render(); return; }
  if (t.dataset.off) { off(t.dataset.off); return; }
  if (t.dataset.clear !== undefined) { clearAll(); return; }
  if (t.dataset.f) { const [k, ...r] = t.dataset.f.split(':'); const v = r.join(':'); flip(F[k], k === 'groups' ? Number(v) : v); return; }
  if (t.dataset.tog) { t.dataset.tog === 'recent' ? (F.recent = !F.recent) : (F.hidePremium = !F.hidePremium); render(); return; }
  if (t.dataset.ui) { UI[t.dataset.ui] = !UI[t.dataset.ui]; render(); return; }
  if (t.dataset.log) { const [id, kind] = t.dataset.log.split(':'); log(byId[id], kind); return; }
  if (t.dataset.open) { openProblem(byId[t.dataset.open]); return; }
  if (t.dataset.moreGroup) { UI.open.add(t.dataset.moreGroup); render(); return; }
  if (t.dataset.statusdue !== undefined) { e.preventDefault(); F.status = new Set(['due']); F.railTab = 'filters'; F.view = 'problems'; render(); return; }
  if (t.dataset.lesson !== undefined) return; // a normal link to pattern.html
  if (t.classList.contains('tcard')) { F.patterns = new Set([t.dataset.pat]); F.view = 'problems'; F.railTab = 'filters'; render(); window.scrollTo({ top: $('#viewSeg').getBoundingClientRect().top + scrollY - 90, behavior: 'smooth' }); }
});
document.addEventListener('input', (e) => {
  if (e.target.id === 'q') { F.q = e.target.value; render(); }
  if (e.target.dataset.keep === 'tagq') { UI.tagQ = e.target.value; render(); }
});
document.addEventListener('keydown', (e) => {
  const typing = e.target.closest && e.target.closest('input, textarea');
  if (e.key === '/' && !typing) { e.preventDefault(); $('#q').focus(); }
  if (e.key === 'f' && !typing && !e.metaKey && !e.ctrlKey) { F.railTab = F.railTab === 'filters' ? 'activity' : 'filters'; render(); }
  if ((e.key === 'Enter' || e.key === ' ') && e.target.classList && e.target.classList.contains('tcard')) { e.preventDefault(); e.target.click(); }
});
document.addEventListener('mouseover', (e) => { const m = e.target.closest('[data-more]'); const tip = $('#tip'); if (!m) { tip.hidden = true; return; } tip.hidden = false; tip.textContent = m.dataset.more; const b = m.getBoundingClientRect(); tip.style.left = `${Math.min(b.left, innerWidth - 340)}px`; tip.style.top = `${b.bottom + 6}px`; });
$('#thm').onclick = () => { const r = document.documentElement; r.dataset.theme = (r.dataset.theme || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')) === 'dark' ? 'light' : 'dark'; };
render();
</script>
'''

fonts = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap">'
home = (f'<title>anneal DSA</title>{fonts}<style>{root_css}{css}</style>' + body
        .replace('__DATA__', json.dumps(P, separators=(',', ':')))
        .replace('__GROUPS__', json.dumps(groups)).replace('__ORDER__', json.dumps(ORDER))
        .replace('__BLURB__', json.dumps(BLURB)).replace('__TECH__', json.dumps(TECH)))
(OUT / 'dsa-tracker.html').write_text(home)

# ---- the problem and pattern screens, sliced from the earlier single-file mockup
old = (SP / 'old-dsa-tracker.html').read_text()
old_css = old.split('<style>', 1)[1].split('</style>', 1)[0]
problem_inner = old.split('<div data-show="problem" hidden>', 1)[1].split('</div>\n    <div data-show="pattern" hidden>', 1)[0]
pattern_inner = old.split('<div data-show="pattern" hidden>', 1)[1].split('</div>\n  </div></div>\n  <div class="notes">', 1)[0]
js = '''<script>
document.querySelectorAll('.hint.locked').forEach((h) => (h.onclick = () => { h.classList.remove('locked'); h.innerHTML = h.dataset.text; }));
document.querySelectorAll('.aptabs button').forEach((b) => (b.onclick = () => {
  document.querySelectorAll('.aptabs button').forEach((x) => x.classList.toggle('on', x === b));
  document.querySelectorAll('.ap').forEach((a) => (a.hidden = a.dataset.ap !== b.dataset.ap));
}));
const KW = 'def|class|return|if|elif|else|for|while|in|not|and|or|is|None|True|False|import|from|as|with|yield|lambda|try|except|finally|raise|pass|break|continue|global|nonlocal';
const BI = 'range|len|set|dict|list|deque|sum|any|all|min|max|enumerate|zip|sorted|print|int|str|self';
const RE = new RegExp(`(#[^\\\\n]*)|("(?:[^"\\\\\\\\]|\\\\\\\\.)*"|'(?:[^'\\\\\\\\]|\\\\\\\\.)*')|\\\\b(${KW})\\\\b|\\\\b(${BI})\\\\b|\\\\b(\\\\d[\\\\d_]*)\\\\b|(\\\\w+)(?=\\\\()`, 'g');
document.querySelectorAll('pre.code').forEach((pre) => {
  const esc = pre.textContent.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  pre.innerHTML = esc.replace(RE, (m, c, s, k, b, n, f) => c ? `<span class="c">${c}</span>` : s ? `<span class="s">${s}</span>` : k ? `<span class="k">${k}</span>` : b ? `<span class="b">${b}</span>` : n ? `<span class="n">${n}</span>` : `<span class="f">${f}</span>`);
});
</script>'''
hdr_old = old.split('<div class="hdr">', 1)[1].split('</div>\n    <div data-show="list">', 1)[0].replace('<span>Build</span>', '')
def page(title, inner, current):
    bar = ('<div class="screens"><b>MOCKUP</b>' + ''.join(f'<a class="{"on" if k == current else ""}" href="{h}">{n}</a>' for k, h, n in [('home', 'dsa-tracker.html', '1 · Home'), ('problem', 'problem.html', '2 · Problem page'), ('pattern', 'pattern.html', '3 · Pattern lesson')]) + '</div>')
    inner = inner.replace('data-go="list" href="#"', 'href="dsa-tracker.html"').replace('<a href="#" data-go="list">', '<a href="dsa-tracker.html">').replace('<a href="#" data-go="pattern">', '<a href="pattern.html">')
    inner = re.sub(r'<a ([^>]*)data-go="pattern"', r'<a href="pattern.html" \1', inner)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>{fonts}<style>{old_css}.screens{{display:flex;gap:6px;align-items:center;padding:10px 16px}}.screens b{{font:600 10.5px var(--mono);letter-spacing:.14em;color:var(--dim);margin-right:6px}}.screens a{{padding:6px 12px;border:1px solid var(--line);border-radius:7px;font:600 12.5px var(--sans);color:var(--mut);background:var(--panel);text-decoration:none}}.screens a.on{{border-color:var(--acc);color:var(--fg);background:var(--acc-bg)}}</style></head><body>'
            f'{bar}<div class="frame" style="border-radius:0;border-inline:0;box-shadow:none"><div class="app"><div class="hdr">{hdr_old}</div>{inner}</div></div>{js}</body></html>')
(OUT / 'problem.html').write_text(page('anneal DSA problem', problem_inner, 'problem'))
(OUT / 'pattern.html').write_text(page('anneal DSA patterns', pattern_inner, 'pattern'))
print('home', len(home), 'problem', (OUT / 'problem.html').stat().st_size, 'pattern', (OUT / 'pattern.html').stat().st_size)
