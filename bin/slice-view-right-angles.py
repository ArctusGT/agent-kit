"""slice-view's chart redrawn square: git's turned-over graph of one group on
stdin, box characters out; main says how."""
import sys
from collections import defaultdict, namedtuple
from functools import partial

# the arms of a cell, the directions its line leaves it in; a cell is drawn as
# the box character for the arms it collects
U, D, L, R = 1, 2, 4, 8
box = {U|D: "│", L|R: "─", U|L: "┘", U|R: "└", D|L: "┐", D|R: "┌", U|D|R: "├",
       U|D|L: "┤", L|R|D: "┬", L|R|U: "┴", U|D|L|R: "┼", U: "│", D: "│", L: "─", R: "─"}
SUB = 3  # the most rows one of git's rows becomes
# what a drawing costs, most important first
FALSE_JOIN = 1000  # a net that joins a slice's line to a slice that does not block it
BORROWED = 30  # a turn put in a row the segment does not run through
SPLIT = 50  # a turn that makes its row one sub-row taller
CROSSING = 1  # a line cutting across another
STEPS = 5000  # how long the search goes on bettering a drawing


class Graph:
    """the input, and the geometry of git's graph in it"""

    def __init__(self, graphs, labels, commits):
        self.graphs, self.labels, self.commits = graphs, labels, commits
        self.H = len(graphs)
        self.cells = [(r, k) for r in range(self.H) for k in range(len(graphs[r]))]
        self.nodes = {c for c in self.cells if self.at(*c) == "*"}
        self.verts = {c for c in self.cells if self.at(*c) == "|"}
        self.diags = {c for c in self.cells if self.at(*c) in "/\\"}
        self.edges = self.blocked_by_edges()
        # an octopus leg, git's -. turned over to -', and the slice it leads into
        self.legs = {}
        for r, k in self.cells:
            if self.at(r, k) in "-'":
                j = k
                while self.at(r, j) in "-'":
                    j -= 1
                self.legs[(r, k)] = (r, j)
        self.tops = {self.top(d): d for d in self.diags}
        self.runs = self.underscore_runs()

    def at(self, r, k):
        g = self.graphs
        return g[r][k] if 0 <= r < self.H and 0 <= k < len(g[r]) else " "

    def blocked_by_edges(self):
        """the blocked-by edges, blocker first, as pieces (see Pieces)"""
        node_of = {self.commits[r][0]: (r, k) for (r, k) in self.nodes if r in self.commits}
        edges = set()
        for c in self.commits.values():
            for p in c[1:]:
                if p in node_of:
                    edges.add((("n", node_of[p]), ("n", node_of[c[0]])))
                else:
                    print(f"slice-view: {c[0]} is blocked by {p}, which is not among the drawn slices",
                          file=sys.stderr)
        return edges

    # a diagonal: which way it leans, where it meets the row boundary above and
    # below it in half columns (a \ at k runs from k-1/2 to k+1/2), and the cells
    # it leans on there
    def sign(self, d):
        return 1 if self.at(*d) == "\\" else -1

    def top(self, d):
        return (d[0], 2 * d[1] - self.sign(d))

    def bottom(self, d):
        return (d[0] + 1, 2 * d[1] + self.sign(d))

    def above(self, d):
        return (d[0] - 1, d[1] - self.sign(d))

    def below(self, d):
        return (d[0] + 1, d[1] + self.sign(d))

    def underscore_runs(self):
        # a row of _ carries a line along the top of its row, from the \ ending
        # at its left end to the \ starting at its right: {where the first meets
        # the row: where the second does}, in half columns
        runs = {}
        for r in range(self.H):
            k = 0
            while k < len(self.graphs[r]):
                if self.at(r, k) == "_":
                    a = k
                    while self.at(r, k + 2) == "_":
                        k += 2
                    # the \ at a-2 meets the row at its bottom(), the \ at k+2 at its top()
                    runs[(r, 2 * (a - 2) + 1)] = (r, 2 * (k + 2) - 1)
                k += 1
        return runs

    def fork(self, d):
        """the | a diagonal forks into: git splits a lane where a diagonal ends
        over a |, the | going on straight"""
        c = (d[0] + 1, d[1])
        return c if c in self.verts else None

    def after(self, d):
        """the diagonal that starts where d ends"""
        p = self.bottom(d)
        if p in self.tops:
            return self.tops[p]
        if self.sign(d) > 0 and p in self.runs:
            return self.tops.get(self.runs[p])
        return None

    def next_of(self, d):
        """the diagonal the line in d goes on as; None where it ends or forks"""
        if self.fork(d):
            return None
        if self.after(d):
            return self.after(d)
        beyond = (d[0] + 1, d[1] + 2 * self.sign(d))
        if self.at(*self.below(d)) == "|" and self.at(*beyond) == self.at(*d):
            return beyond
        return None

    def end_cell(self, ch):
        """the cell a line ends on: the | it forks into, else the one its last
        diagonal leans on"""
        return self.fork(ch[-1]) or self.below(ch[-1])

    def piece(self, c):
        if c in self.nodes:
            return ("n", c)
        if c in self.legs:
            return ("n", self.legs[c])
        if c in self.verts:
            return ("v", c)
        return None


def parse(text):
    graphs, labels, commits = [], [], {}
    for r, line in enumerate(text.splitlines()):
        graph, _, rest = line.partition("\x1f")
        meta, _, label = rest.partition("\x1f")
        graphs.append(graph)
        labels.append(label)
        if meta:
            commits[r] = meta.split()
    return Graph(graphs, labels, commits)


def find_chains(g):
    """the diagonals of one line, each chain starting where nothing leads into
    it; the diagonal after a fork starts a line of its own"""
    follows = {d: g.next_of(d) for d in g.diags}
    led = {n for n in follows.values() if n}
    chains = []
    for d in sorted(g.diags):
        # git leaves a stub below some merges, a diagonal leaning on nothing,
        # beside the lines that do carry the merge's edges; it is not drawn
        if d not in led and g.at(*g.above(d)) != " ":
            chain = [d]
            while follows[chain[-1]]:
                chain.append(follows[chain[-1]])
            chains.append(chain)
    return chains


class Pieces:
    """what a line is made of, and what each piece leads into (succ) and comes
    from (preds): a slice ("n", cell), a | ("v", cell), a chain ("c", index),
    and a slice's tail ("t", cell), the line below it in rows its row became"""

    def __init__(self, g, chains):
        self.succ, self.preds = {}, {}
        self.up_memo, self.down_memo = {}, {}
        starts_at = {}
        for i, ch in enumerate(chains):
            starts_at.setdefault(g.above(ch[0]), []).append(i)
        for c in g.nodes | g.verts:
            kind = ("n", c) if c in g.nodes else ("v", c)
            out = [("c", i) for i in starts_at.get(c, [])]
            below = (c[0] + 1, c[1])
            b = g.piece(below)
            # a slice stacked on another joins it only where it blocks it
            if b and below not in g.legs and (kind[0] == "v" or b[0] == "v" or (kind, b) in g.edges):
                out.append(b)
            self.succ[kind] = out
        for i, ch in enumerate(chains):
            b = g.piece(g.end_cell(ch))
            self.succ[("c", i)] = ([b] if b else []) + [("c", j) for j in starts_at.get(ch[-1], [])]
        for p, outs in self.succ.items():
            for q in outs:
                self.preds.setdefault(q, []).append(p)

    @staticmethod
    def reach(p, step, memo):
        """the slices a piece leads to through step, by way of other pieces; step
        only moves down the rows (up, for preds), so the walk cannot loop"""
        if p not in memo:
            found = set()
            for q in step.get(p, []):
                found |= {q} if q[0] == "n" else Pieces.reach(q, step, memo)
            memo[p] = found
        return memo[p]

    def ends(self, p):
        """the slices a piece carries lines from, and to"""
        if p[0] == "n":
            return {p}, {p}
        if p[0] == "t":
            n = ("n", p[1])
            return {n}, self.reach(n, self.succ, self.down_memo)
        return self.reach(p, self.preds, self.up_memo), self.reach(p, self.succ, self.down_memo)


def gap(rows, r):
    """how far row r is from the nearest end of rows"""
    return min(abs(r - rows[0]), abs(r - rows[-1]))


def borrow(g, pieces, owned, start, p, dr):
    """the rows of the | from start, going dr (-1 up, +1 down) a row at a time,
    that carry piece p's line alone and that no chain has taken, in the order
    they are claimed into owned, first come first served"""
    # going up the | leads down into p; going down it comes from p
    step, side = (pieces.succ, 0) if dr < 0 else (pieces.preds, 1)
    rows = []
    c = start
    while c in g.verts and c not in owned and step.get(("v", c)) == [p] \
            and pieces.ends(("v", c))[side] == pieces.ends(p)[side]:
        rows.append(c[0])
        owned.add(c)
        p, c = ("v", c), (c[0] + dr, c[1])
    return rows


def build_segments(g, chains, pieces):
    """a chain as segments, each a run of its rows moving one way, from one
    column to another, with the rows it may turn in and the choices of where;
    and the | the segments borrowed"""
    segments = []
    for i, ch in enumerate(chains):
        start = g.above(ch[0])[1]
        j = 0
        while j < len(ch):
            s = g.sign(ch[j])
            k = j
            while k + 1 < len(ch) and g.sign(ch[k + 1]) == s:
                k += 1
            # a step out and back turns at the column beyond its diagonal's
            end = g.end_cell(ch)[1] if k == len(ch) - 1 else ch[k][1] + s
            segments.append({"chain": i, "rows": [d[0] for d in ch[j:k + 1]], "from": start, "to": end,
                             "first": j == 0, "last": k == len(ch) - 1})
            start = end
            j = k + 1

    # a chain's segment may borrow the | above its first row or below its last,
    # while it carries that chain's line alone and no other chain has taken it
    owned = set()
    for seg in segments:
        i = seg["chain"]
        borrowed_above, borrowed_below = [], []
        if seg["first"]:
            borrowed_above = borrow(g, pieces, owned, g.above(chains[i][0]), ("c", i), -1)
        if seg["last"]:
            borrowed_below = borrow(g, pieces, owned, g.end_cell(chains[i]), ("c", i), 1)
        seg["span"] = borrowed_above[::-1] + seg["rows"] + borrowed_below
        by_nearness = sorted(set(seg["span"]) - set(seg["rows"]), key=partial(gap, seg["rows"]))
        seg["choices"] = [(m, s) for s in range(SUB) for m in seg["rows"]] \
            + [(m, s) for s in range(SUB) for m in by_nearness]
        # a line ending on a slice may come into its ● from the side, along the
        # slice's row, rather than join another line coming down into it
        c = g.end_cell(chains[i])
        seg["side_row"] = None
        if seg["last"] and c in g.nodes and seg["from"] != seg["to"]:
            seg["side_row"] = c[0]
            seg["choices"].append((c[0], 0))
    return segments, owned


def side_entry(seg):
    """the cells a segment draws coming into its slice's ● from the side"""
    a, b = seg["from"], seg["to"]
    step = 1 if b > a else -1
    out = []
    for r in seg["span"]:
        out += [((r, t, a), U | D) for t in range(SUB)]
    out.append(((seg["side_row"], 0, a), U | (R if step > 0 else L)))
    return out + [((seg["side_row"], 0, k), L | R) for k in range(a + step, b, step)]


def turn(seg, m, s):
    """the cells a segment draws turning in sub-row s of row m"""
    a, b = seg["from"], seg["to"]
    step = 1 if b > a else -1
    out = []
    for r in seg["span"]:
        for t in range(SUB):
            above_turn = (r, t) < (m, s) or a == b
            below_turn = (r, t) > (m, s)
            if above_turn:
                out.append(((r, t, a), U | D))
            elif below_turn:
                out.append(((r, t, b), U | D))
            else:
                out.append(((r, t, a), U | (R if step > 0 else L)))
                out += [((r, t, k), L | R) for k in range(a + step, b, step)]
                out.append(((r, t, b), D | (L if step > 0 else R)))
    return out


def drawn(seg, m, s):
    """the cells, as (row, sub-row, column), a segment draws turning in
    sub-row s of row m, each with its arms"""
    if m == seg["side_row"]:
        return side_entry(seg)
    return turn(seg, m, s)


def fix_cell(fixed, r, t, k, p, arms):
    fixed[(r, t, k)].append((p, arms))


def fixed_cells(g, chains, pieces, owned):
    """what no choice moves: the | no chain took, in every sub-row; legs, in the
    first; a slice's tail, in the others"""
    fixed = defaultdict(list)
    for (r, k) in g.verts - owned:
        for t in range(SUB):
            fix_cell(fixed, r, t, k, ("v", (r, k)), U | D)
    for c, n in g.legs.items():
        arms = (L | R) if g.at(*c) == "-" else (L | U)
        if (c[0] - 1, c[1]) in g.verts or any(g.end_cell(ch) == c for ch in chains):
            arms |= U
        fix_cell(fixed, c[0], 0, c[1], ("n", n), arms)
    for (r, k) in g.nodes:
        if pieces.succ.get(("n", (r, k))):
            for t in range(1, SUB):
                fix_cell(fixed, r, t, k, ("t", (r, k)), U | D)
    return fixed


def crosses(a, b):
    """whether arms a and b are one line across the other"""
    return {a, b} == {L | R, U | D}


class Search:
    """the search: segments top down, each one's choices cheapest first, so the
    first drawing found is the greedy one; a dense group then has STEPS more
    steps of the search to better it, a count rather than a time so that one
    group draws the same on any host

    It holds the grid of what is drawn so far, the best drawing found (its cost
    and each segment's choice), the steps left, the sub-rows the turns placed
    in each row use, and the nets: a union-find, with the slices each net
    carries lines from and to, that the search undoes in step with itself"""

    def __init__(self, g, segments, pieces):
        self.nodes, self.edges, self.pieces = g.nodes, g.edges, pieces
        self.segments = segments
        self.order = sorted(range(len(segments)), key=lambda i: (segments[i]["span"][0], segments[i]["from"]))
        self.grid = {}
        self.best_cost, self.best_chosen = None, {}
        self.steps = STEPS
        self.depth = {}  # row: the sub-rows the turns placed in it use
        self.parent, self.net_ends, self.undo = {}, {}, []

    def root(self, p):
        while self.parent.get(p, p) != p:
            p = self.parent[p]
        return p

    def merge_and_price(self, p, q):
        """merge two pieces' nets and return what the merged net costs: FALSE_JOIN
        where a slice it carries a line from does not block a slice it carries
        one to"""
        a, b = self.root(p), self.root(q)
        if a == b:
            self.undo.append(None)
            return 0
        # net_ends is kept at a net's root; a piece not yet in a net carries its own ends
        sa, ta = self.net_ends.get(a) or self.pieces.ends(a)
        sb, tb = self.net_ends.get(b) or self.pieces.ends(b)
        self.parent[b] = a
        self.undo.append((a, b, self.net_ends.get(a)))
        ss, ts = sa | sb, ta | tb
        self.net_ends[a] = (ss, ts)
        return 0 if all((s, t) in self.edges for s in ss for t in ts) else FALSE_JOIN

    def unmerge(self):
        step = self.undo.pop()
        if step:
            a, b, kept = step
            del self.parent[b]
            if kept is None:
                self.net_ends.pop(a, None)
            else:
                self.net_ends[a] = kept

    def put(self, c, p, arms):
        """add piece p's arms to cell c: what it costs, and how many merges to
        undo"""
        here = self.grid.setdefault(c, [])
        cost, merges = 0, 0
        # arms on a slice's ● cost FALSE_JOIN: a line drawn through a slice reads
        # as joining it
        if c[1] == 0 and (c[0], c[2]) in self.nodes:
            cost += FALSE_JOIN
        if len(here) == 1 and here[0][0] != p and crosses(here[0][1], arms):
            cost += CROSSING
        elif here:
            # a crossing that a third line now joins is a crossing no more
            if len(here) == 2 and crosses(here[0][1], here[1][1]) and here[0][0] != here[1][0]:
                cost += self.merge_and_price(here[0][0], here[1][0]) - CROSSING
                merges += 1
            for q, _ in here:
                cost += self.merge_and_price(p, q)
                merges += 1
        here.append((p, arms))
        return cost, merges

    def place(self, seg, m, s):
        """draw seg turning in sub-row s of row m: what it adds to the cost, the
        cells it drew, and how many merges to undo"""
        used = self.depth.setdefault(m, [])
        extra = (0 if m in seg["rows"] else BORROWED) + SPLIT * max(0, s - max(used, default=0))
        used.append(s)
        added, merges = [], 0
        for c, arms in drawn(seg, m, s):
            more, j = self.put(c, ("c", seg["chain"]), arms)
            extra += more
            merges += j
            added.append(c)
        return extra, added, merges

    def lift(self, m, added, merges):
        """undo place: take back the cells it drew and its merges"""
        for c in added:
            self.grid[c].pop()
        for _ in range(merges):
            self.unmerge()
        self.depth[m].pop()

    def beaten(self, cost):
        """whether a drawing costing cost cannot better the best: it costs as
        much, or the steps are spent, once there is a best"""
        return self.best_cost is not None and (cost >= self.best_cost or self.steps < 0)

    def descend(self, n, cost, chosen):
        """choose a place for the n-th segment of the order, then go on to the
        next: its choices are priced alone and tried cheapest first, and a
        drawing of every segment better than the best so far becomes the best"""
        self.steps -= 1
        if self.beaten(cost):
            return
        if n == len(self.order):
            self.best_cost, self.best_chosen = cost, dict(chosen)
            return
        seg = self.segments[self.order[n]]
        priced = []
        for i, (m, s) in enumerate(seg["choices"]):
            extra, added, merges = self.place(seg, m, s)
            self.lift(m, added, merges)
            priced.append((extra, i, m, s))
        for extra, _, m, s in sorted(priced):
            if self.beaten(cost + extra):
                break
            extra, added, merges = self.place(seg, m, s)
            chosen[self.order[n]] = (m, s)
            self.descend(n + 1, cost + extra, chosen)
            self.lift(m, added, merges)
        chosen.pop(self.order[n], None)

    def run(self, fixed):
        """the best choice for each segment, as {segment: (row, sub-row)}"""
        base = 0
        for c, entries in fixed.items():
            for p, arms in entries:
                base += self.put(c, p, arms)[0]
        self.descend(0, base, {})
        return self.best_chosen


# a printed row: its box characters, its label, {column: slice} for the slices
# on it, and {column: arms} for the lines on it
Row = namedtuple("Row", "text label slices arms")


def printed_rows(g, dirs, split):
    """the rows to print, git's row r as split[r] of them, each cell drawn from
    the arms in dirs, keyed (row, sub-row, column)"""
    width = {r: len(g.graphs[r]) for r in range(g.H)}
    for c in dirs:
        width[c[0]] = max(width[c[0]], c[2] + 1)
    rows = []
    for r in range(g.H):
        for t in range(split[r]):
            chars, slices, arms = [], {}, {}
            for k in range(width[r]):
                if t == 0 and (r, k) in g.nodes:
                    chars.append("●")
                    slices[k] = (r, k)
                else:
                    chars.append(box.get(dirs.get((r, t, k), 0), " "))
                    if dirs.get((r, t, k)):
                        arms[k] = dirs[(r, t, k)]
            rows.append(Row("".join(chars), g.labels[r] if t == 0 else "", slices, arms))
    return rows


def render(g, fixed, segments, chosen):
    dirs = defaultdict(int)
    for c, entries in fixed.items():
        for _, arms in entries:
            dirs[c] |= arms
    split = {r: 1 for r in range(g.H)}
    for i, (m, s) in chosen.items():
        split[m] = max(split[m], s + 1)
        for c, arms in drawn(segments[i], m, s):
            dirs[c] |= arms
    rows = printed_rows(g, dirs, split)

    # git puts no line between a slice and its blocker on the next row of the
    # same column; a row of │ goes there, carrying every line that runs through
    for row, nxt in zip(rows, rows[1:] + [Row("", "", {}, {})]):
        text, label = row.text, row.label
        # the label follows its row's drawing after one space; a row with no
        # drawing, or no label, prints as the one it has
        print((text.rstrip() + " " + label.lstrip()).rstrip() if label and text.strip() else (label or text).rstrip())
        stacked = {k for k, s in row.slices.items() if k in nxt.slices and (("n", s), ("n", nxt.slices[k])) in g.edges}
        if stacked:
            print("".join("│" if k in stacked or (row.arms.get(k, 0) & D and nxt.arms.get(k, 0) & U) else " "
                          for k in range(max(len(text), len(nxt.text)))).rstrip())


def main():
    """Each input line is git's graph, then, on a slice's line, its commit
    and its blockers' commits between two \\x1f, then its label, which is
    printed as it is. The blocked-by edges come from those commits, not
    from the graph.

    git moves a line sideways one column a row, as a run of diagonals: a
    staircase, a crossing over a lane (a diagonal either side of its |), a
    jump along a row of _, a step out and back. Each run is one line between
    two columns, drawn as a vertical, one horizontal and a vertical, its turn
    put in whichever of its rows reads right; a row splits into as many as
    three where two turns cannot share it. Lines that share a cell other
    than by crossing read as joined, so every slice such a net carries a
    line from must block every slice it carries one to. The turns are chosen
    by a search that weighs, in order: such false joins, rows borrowed from
    a line's own lane or a slice's row, split rows, crossings."""
    g = parse(sys.stdin.read())
    chains = find_chains(g)
    pieces = Pieces(g, chains)
    segments, owned = build_segments(g, chains, pieces)
    fixed = fixed_cells(g, chains, pieces, owned)
    chosen = Search(g, segments, pieces).run(fixed)
    render(g, fixed, segments, chosen)


main()
