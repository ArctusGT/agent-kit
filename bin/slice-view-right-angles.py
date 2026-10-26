"""slice-view's chart redrawn square: git's turned-over graph of one group on
stdin, box characters out.

Each input line is git's graph, then, on a slice's line, its commit and its
blockers' commits between two \\x1f, then its label, which is printed as it
is. The blocked-by edges come from those commits, not from the graph.

git moves a line sideways one column a row, as a run of diagonals: a
staircase, a crossing over a lane (a diagonal either side of its |), a jump
along a row of _, a step out and back. Each run is one line between two
columns, drawn as a vertical, one horizontal and a vertical, its turn put in
whichever of its rows reads right; a row splits into as many as three where
two turns cannot share it. Lines that share a cell other than by crossing
read as joined, so every slice such a net carries a line from must block
every slice it carries one to. The turns are chosen by a search that weighs,
in order: such false joins, rows borrowed from a line's own lane or a
slice's row, split rows, crossings.
"""
import sys
import time

U, D, L, R = 1, 2, 4, 8
box = {U|D: "│", L|R: "─", U|L: "┘", U|R: "└", D|L: "┐", D|R: "┌", U|D|R: "├",
       U|D|L: "┤", L|R|D: "┬", L|R|U: "┴", U|D|L|R: "┼", U: "│", D: "│", L: "─", R: "─"}
arms_of = {c: a for a, c in box.items() if a not in (U, D, L, R)}
SUB = 3  # the most rows one of git's rows becomes
FALSE_JOIN, BORROWED, SPLIT, CROSSING = 1000, 30, 50, 1

graphs, labels, commits = [], [], {}
for r, line in enumerate(sys.stdin.read().splitlines()):
    graph, _, rest = line.partition("\x1f")
    meta, _, label = rest.partition("\x1f")
    graphs.append(graph)
    labels.append(label)
    if meta:
        commits[r] = meta.split()
H = len(graphs)


def at(r, k):
    return graphs[r][k] if 0 <= r < H and 0 <= k < len(graphs[r]) else " "


cells = [(r, k) for r in range(H) for k in range(len(graphs[r]))]
nodes = {c for c in cells if at(*c) == "*"}
verts = {c for c in cells if at(*c) == "|"}
diags = {c for c in cells if at(*c) in "/\\"}
# the blocked-by edges, blocker first, as pieces (below)
node_of = {commits[r][0]: (r, k) for (r, k) in nodes if r in commits}
edges = {(("n", node_of[p]), ("n", node_of[c[0]])) for c in commits.values() for p in c[1:] if p in node_of}
# an octopus leg, git's -. turned over to -', and the slice it leads into
legs = {}
for r, k in cells:
    if at(r, k) in "-'":
        j = k
        while at(r, j) in "-'":
            j -= 1
        legs[(r, k)] = (r, j)


# a diagonal: which way it leans, where it meets the row boundary above and
# below it in half columns (a \ at k runs from k-1/2 to k+1/2), and the cells
# it leans on there
def sign(d):
    return 1 if at(*d) == "\\" else -1


def top(d):
    return (d[0], 2 * d[1] - sign(d))


def bottom(d):
    return (d[0] + 1, 2 * d[1] + sign(d))


def above(d):
    return (d[0] - 1, d[1] - sign(d))


def below(d):
    return (d[0] + 1, d[1] + sign(d))


tops = {top(d): d for d in diags}
# a row of _ carries a line along the top of its row, from the \ ending at
# its left end to the \ starting at its right
runs = {}
for r in range(H):
    k = 0
    while k < len(graphs[r]):
        if at(r, k) == "_":
            a = k
            while at(r, k + 2) == "_":
                k += 2
            runs[(r, 2 * a - 3)] = (r, 2 * k + 3)
        k += 1


def fork(d):
    """the | a diagonal forks into: git splits a lane where a diagonal ends
    over a |, the | going on straight"""
    c = (d[0] + 1, d[1])
    return c if c in verts else None


def after(d):
    """the diagonal that starts where d ends"""
    p = bottom(d)
    if p in tops:
        return tops[p]
    if sign(d) > 0 and p in runs:
        return tops.get(runs[p])
    return None


def next_of(d):
    """the diagonal the line in d goes on as; None where it ends or forks"""
    if fork(d):
        return None
    if after(d):
        return after(d)
    beyond = (d[0] + 1, d[1] + 2 * sign(d))
    if at(*below(d)) == "|" and at(*beyond) == at(*d):
        return beyond
    return None


# chains: the diagonals of one line, each starting where nothing leads into
# it; the diagonal after a fork starts a line of its own
follows = {d: next_of(d) for d in diags}
led = {n for n in follows.values() if n}
chains = []
for d in sorted(diags):
    # git leaves a stub below some merges, a diagonal leaning on nothing,
    # beside the lines that do carry the merge's edges; it is not drawn
    if d not in led and at(*above(d)) != " ":
        chain = [d]
        while follows[chain[-1]]:
            chain.append(follows[chain[-1]])
        chains.append(chain)


def end_cell(ch):
    """the cell a line ends on: the | it forks into, else the one its last
    diagonal leans on"""
    return fork(ch[-1]) or below(ch[-1])


# pieces: a slice ("n", cell), a | ("v", cell), a chain ("c", index), and a
# slice's tail ("t", cell), the line below it in rows its row became. What
# each leads into below
def piece(c):
    if c in nodes:
        return ("n", c)
    if c in legs:
        return ("n", legs[c])
    if c in verts:
        return ("v", c)
    return None


starts_at = {}
for i, ch in enumerate(chains):
    starts_at.setdefault(above(ch[0]), []).append(i)
succ = {}
for c in nodes | verts:
    kind = ("n", c) if c in nodes else ("v", c)
    out = [("c", i) for i in starts_at.get(c, [])]
    b = piece((c[0] + 1, c[1]))
    # a slice stacked on another joins it only where it blocks it
    if b and (c[0] + 1, c[1]) not in legs and (kind[0] == "v" or b[0] == "v" or (kind, b) in edges):
        out.append(b)
    succ[kind] = out
for i, ch in enumerate(chains):
    b = piece(end_cell(ch))
    succ[("c", i)] = ([b] if b else []) + [("c", j) for j in starts_at.get(ch[-1], [])]
preds = {}
for p, outs in succ.items():
    for q in outs:
        preds.setdefault(q, []).append(p)


def reach(p, step, memo):
    if p not in memo:
        memo[p] = set()
        found = set()
        for q in step.get(p, []):
            found |= {q} if q[0] == "n" else reach(q, step, memo)
        memo[p] = found
    return memo[p]


up_memo, down_memo = {}, {}


def ends(p):
    """the slices a piece carries lines from, and to"""
    if p[0] == "n":
        return {p}, {p}
    if p[0] == "t":
        n = ("n", p[1])
        return {n}, reach(n, succ, down_memo)
    return reach(p, preds, up_memo), reach(p, succ, down_memo)


# a chain as segments, each a run of its rows moving one way, from one
# column to another; a step out and back turns at the column beyond
segments = []
for i, ch in enumerate(chains):
    start = above(ch[0])[1]
    j = 0
    while j < len(ch):
        s = sign(ch[j])
        k = j
        while k + 1 < len(ch) and sign(ch[k + 1]) == s:
            k += 1
        end = end_cell(ch)[1] if k == len(ch) - 1 else (bottom(ch[k])[1] + s) // 2
        segments.append({"chain": i, "rows": [d[0] for d in ch[j:k + 1]], "from": start, "to": end,
                         "first": j == 0, "last": k == len(ch) - 1})
        start = end
        j = k + 1

# where a chain's own rows cannot hold its turn, the | above its first row or
# below its last may, while it carries that chain's line alone and no other
# chain has taken it; and a line
# ending on a slice may come into its ● from the side, along the slice's row,
# rather than join another line coming down into it
owned = set()
for seg in segments:
    i = seg["chain"]
    lent = []
    if seg["first"]:
        c, p = above(chains[i][0]), ("c", i)
        while c in verts - owned and succ.get(("v", c)) == [p] and ends(("v", c))[0] == ends(p)[0]:
            lent.insert(0, c[0])
            owned.add(c)
            p, c = ("v", c), (c[0] - 1, c[1])
    seg["span"] = lent + seg["rows"]
    lent = []
    if seg["last"]:
        c, p = end_cell(chains[i]), ("c", i)
        while c in verts - owned and preds.get(("v", c)) == [p] and ends(("v", c))[1] == ends(p)[1]:
            lent.append(c[0])
            owned.add(c)
            p, c = ("v", c), (c[0] + 1, c[1])
    seg["span"] += lent
    near = lambda r: min(abs(r - seg["rows"][0]), abs(r - seg["rows"][-1]))
    lent = sorted(set(seg["span"]) - set(seg["rows"]), key=near)
    seg["choices"] = [(m, s) for s in range(SUB) for m in seg["rows"]] + [(m, s) for s in range(SUB) for m in lent]
    c = end_cell(chains[i])
    if seg["last"] and c in nodes and seg["from"] != seg["to"]:
        seg["choices"].append((c[0], 0))


def drawn(seg, m, s):
    """the cells, as (row, sub-row, column), a segment draws turning in
    sub-row s of row m, each with its arms"""
    a, b = seg["from"], seg["to"]
    step = 1 if b > a else -1
    out = []
    if m not in seg["span"]:
        # into its slice's ● from the side
        for r in seg["span"]:
            out += [((r, t, a), U | D) for t in range(SUB)]
        out.append(((m, 0, a), U | (R if step > 0 else L)))
        return out + [((m, 0, k), L | R) for k in range(a + step, b, step)]
    for r in seg["span"]:
        for t in range(SUB):
            if (r, t) < (m, s) or a == b:
                out.append(((r, t, a), U | D))
            elif (r, t) > (m, s):
                out.append(((r, t, b), U | D))
            else:
                out.append(((r, t, a), U | (R if step > 0 else L)))
                out += [((r, t, k), L | R) for k in range(a + step, b, step)]
                out.append(((r, t, b), D | (L if step > 0 else R)))
    return out


# what no choice moves: the | no chain took, in every sub-row; legs, in the
# first; a slice's tail, in the others
fixed = {}
for (r, k) in verts - owned:
    for t in range(SUB):
        fixed.setdefault((r, t, k), []).append((("v", (r, k)), U | D))
for c, n in legs.items():
    arms = L | R if at(*c) == "-" else L | U
    if (c[0] - 1, c[1]) in verts or any(end_cell(ch) == c for ch in chains):
        arms |= U
    fixed.setdefault((c[0], 0, c[1]), []).append((("n", n), arms))
for (r, k) in nodes:
    if succ.get(("n", (r, k))):
        for t in range(1, SUB):
            fixed.setdefault((r, t, k), []).append((("t", (r, k)), U | D))


# nets, as a union-find the search undoes in step with itself
parent, net_ends, undo = {}, {}, []


def root(p):
    while parent.get(p, p) != p:
        p = parent[p]
    return p


def join(p, q):
    """join two pieces' nets; what it costs"""
    a, b = root(p), root(q)
    if a == b:
        undo.append(None)
        return 0
    sa, ta = net_ends.get(a) or ends(a)
    sb, tb = net_ends.get(b) or ends(b)
    parent[b] = a
    undo.append((a, b, net_ends.get(a)))
    ss, ts = sa | sb, ta | tb
    net_ends[a] = (ss, ts)
    return 0 if all((s, t) in edges for s in ss for t in ts) else FALSE_JOIN


def unjoin():
    step = undo.pop()
    if step:
        a, b, kept = step
        del parent[b]
        if kept is None:
            net_ends.pop(a, None)
        else:
            net_ends[a] = kept


def put(grid, c, p, arms):
    """add piece p's arms to cell c: what it costs, and how many joins to
    undo"""
    here = grid.setdefault(c, [])
    cost, joins = 0, 0
    if c[1] == 0 and (c[0], c[2]) in nodes:
        cost += FALSE_JOIN
    if len(here) == 1 and here[0][0] != p and {here[0][1], arms} == {L | R, U | D}:
        cost += CROSSING
    elif here:
        # a crossing that a third line now joins is a crossing no more
        if len(here) == 2 and {here[0][1], here[1][1]} == {L | R, U | D} and here[0][0] != here[1][0]:
            cost += join(here[0][0], here[1][0]) - CROSSING
            joins += 1
        for q, _ in here:
            cost += join(p, q)
            joins += 1
    here.append((p, arms))
    return cost, joins


# the search: segments top down, each one's choices cheapest first, so the
# first drawing found is the greedy one; a dense group then has a second to
# better it
order = sorted(range(len(segments)), key=lambda i: (segments[i]["span"][0], segments[i]["from"]))
best = [None, {}]
depth = {}  # row: the sub-rows the turns placed in it use
deadline = time.monotonic() + 1.0


def search(n, grid, cost, chosen):
    if best[0] is not None and (cost >= best[0] or time.monotonic() > deadline):
        return
    if n == len(order):
        best[0], best[1] = cost, dict(chosen)
        return
    seg = segments[order[n]]

    def place(m, s):
        used = depth.setdefault(m, [])
        extra = (0 if m in seg["rows"] else BORROWED) + SPLIT * max(0, s - max(used, default=0))
        used.append(s)
        added, joins = [], 0
        for c, arms in drawn(seg, m, s):
            more, j = put(grid, c, ("c", seg["chain"]), arms)
            extra += more
            joins += j
            added.append(c)
        return extra, added, joins

    def lift(m, added, joins):
        for c in added:
            grid[c].pop()
        for _ in range(joins):
            unjoin()
        depth[m].pop()

    priced = []
    for i, (m, s) in enumerate(seg["choices"]):
        extra, added, joins = place(m, s)
        lift(m, added, joins)
        priced.append((extra, i, m, s))
    for extra, _, m, s in sorted(priced):
        if best[0] is not None and cost + extra >= best[0]:
            break
        extra, added, joins = place(m, s)
        chosen[order[n]] = (m, s)
        search(n + 1, grid, cost + extra, chosen)
        lift(m, added, joins)
    chosen.pop(order[n], None)


start, base = {}, 0
for c, entries in fixed.items():
    for p, arms in entries:
        base += put(start, c, p, arms)[0]
search(0, start, base, {})

dirs = {}
for c, entries in fixed.items():
    for _, arms in entries:
        dirs[c] = dirs.get(c, 0) | arms
split = {r: 1 for r in range(H)}
for i, (m, s) in best[1].items():
    split[m] = max(split[m], s + 1)
    for c, arms in drawn(segments[i], m, s):
        dirs[c] = dirs.get(c, 0) | arms

out = []  # each printed row: its text, its label, {column: the slice there}
for r in range(H):
    width = max([len(graphs[r])] + [c[2] + 1 for c in dirs if c[0] == r])
    for t in range(split[r]):
        text = "".join("●" if t == 0 and (r, k) in nodes else box.get(dirs.get((r, t, k), 0), " ")
                       for k in range(width))
        out.append((text, labels[r] if t == 0 else "", {k: (r, k) for k in range(width) if t == 0 and (r, k) in nodes}))


def arm(text, k, a):
    return k < len(text) and arms_of.get(text[k], 0) & a


# git puts no line between a slice and its blocker on the next row of the
# same column; a row of │ goes there, carrying every line that runs through
for i, (text, label, here) in enumerate(out):
    print((text.rstrip() + " " + label.lstrip()).rstrip() if label and text.strip() else (label or text).rstrip())
    nxt, there = out[i + 1][0::2] if i + 1 < len(out) else ("", {})
    stacked = {k for k in here if k in there and (("n", here[k]), ("n", there[k])) in edges}
    if stacked:
        print("".join("│" if k in stacked or (arm(text, k, D) and arm(nxt, k, U)) else " "
                      for k in range(max(len(text), len(nxt)))).rstrip())
