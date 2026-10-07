import json
cs = json.load(open('cs207.json'))['data']['question']

COURSE_SCHEDULE = {
  "statement": cs["content"],
  "hints": cs["hints"],
  "intuition": "Each course is a node and each prerequisite <code>[a, b]</code> is an edge <code>b → a</code>: b has to come before a. You can finish everything unless some courses wait on each other in a loop, and a loop is exactly a <b>cycle</b> in that directed graph. So the question is really: <i>does this directed graph have a cycle?</i>",
  "tips": [
    "Get the edge direction right: <code>[a, b]</code> means <code>b → a</code>. Reversing every edge still gives the right answer here, but not in Course Schedule II, where you return the order.",
    "The graph can be disconnected: start a search from <b>every</b> course, not just course 0.",
    "A plain <code>visited</code> set isn't enough for directed graphs. A diamond (0→1, 0→2, 1→3, 2→3) reaches 3 twice without any cycle. Use three states: unseen, on the current path, done.",
    "<code>numCourses</code> goes up to 2000, deeper than Python's default recursion limit of 1000. Raise it with <code>sys.setrecursionlimit</code>, or use Kahn's algorithm, which needs no recursion.",
    "In an interview, say the reduction out loud first: \"this is cycle detection in a directed graph\". It's most of the credit.",
  ],
  "approaches": [
    {"name": "DFS with three states", "label": "classic DFS", "idea": "Walk from each course. Mark a node <b>visiting</b> while it's on the current path and <b>done</b> once everything after it is explored. Meeting a <b>visiting</b> node again means you've come back around: a cycle.",
     "code": '''import sys

class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        sys.setrecursionlimit(10_000)  # up to 2000 courses deep
        graph = [[] for _ in range(numCourses)]
        for course, pre in prerequisites:
            graph[pre].append(course)

        UNSEEN, VISITING, DONE = 0, 1, 2
        state = [UNSEEN] * numCourses

        def has_cycle(node: int) -> bool:
            if state[node] == VISITING:
                return True   # back on our own path: a cycle
            if state[node] == DONE:
                return False  # already proven cycle-free
            state[node] = VISITING
            if any(has_cycle(nxt) for nxt in graph[node]):
                return True
            state[node] = DONE
            return False

        return not any(has_cycle(c) for c in range(numCourses))''',
     "time": "O(V + E)", "space": "O(V + E)", "note": "Each course and prerequisite is visited once; the graph and the recursion stack take the space."},
    {"name": "Kahn's algorithm (BFS topological sort)", "label": "topological sort", "idea": "Repeatedly take a course with no remaining prerequisites (in-degree 0) and remove its outgoing edges. If every course gets taken, there's an order; if some are left, they're stuck in a cycle.",
     "code": '''from collections import deque

class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        graph = [[] for _ in range(numCourses)]
        indegree = [0] * numCourses
        for course, pre in prerequisites:
            graph[pre].append(course)
            indegree[course] += 1

        queue = deque(c for c in range(numCourses) if indegree[c] == 0)
        taken = 0
        while queue:
            node = queue.popleft()
            taken += 1
            for nxt in graph[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        return taken == numCourses''',
     "time": "O(V + E)", "space": "O(V + E)", "note": "No recursion, and the dequeue order <i>is</i> a valid course order, which is all Course Schedule II adds."},
  ],
}

GRAPH_PATTERNS = [
  {"id": "dfs", "name": "DFS: recursive and iterative", "when": ["explore everything reachable from a node", "count connected components", "does a path exist?"],
   "code": '''def dfs(node, graph, seen):
    seen.add(node)
    for nxt in graph[node]:
        if nxt not in seen:
            dfs(nxt, graph, seen)

# Iterative: the same walk with an explicit stack. Use it when the
# graph can be deeper than Python's recursion limit (1000).
def dfs_iterative(start, graph):
    seen, stack = {start}, [start]
    while stack:
        node = stack.pop()
        for nxt in graph[node]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen''',
   "pitfalls": ["Python's recursion limit is 1000: deep graphs need the iterative form or sys.setrecursionlimit.", "Mark a node seen before exploring it, or cycles loop forever."],
   "problems": ["clone-graph", "number-of-provinces", "keys-and-rooms", "find-if-path-exists-in-graph", "all-paths-from-source-to-target"]},
  {"id": "bfs", "name": "BFS: shortest path in unweighted graphs", "when": ["fewest steps / moves / edges", "level by level (distance k)", "every edge costs the same"],
   "code": '''from collections import deque

def bfs(start, graph):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph[node]:
            if nxt not in dist:          # mark when enqueued,
                dist[nxt] = dist[node] + 1  # not when dequeued
                queue.append(nxt)
    return dist''',
   "pitfalls": ["Mark visited when you enqueue; marking on dequeue lets the same node in many times.", "Weighted edges break BFS: that's Dijkstra (Advanced Graphs)."],
   "problems": ["word-ladder", "shortest-path-in-binary-matrix", "open-the-lock", "minimum-genetic-mutation", "snakes-and-ladders"]},
  {"id": "flood", "name": "Flood fill on grids", "when": ["a 2-D grid of cells", "islands, regions, enclosed areas", "connected cells of the same kind"],
   "code": '''DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def fill(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != "1":
        return 0
    grid[r][c] = "#"   # sink it: the grid is the visited set
    return 1 + sum(fill(grid, r + dr, c + dc) for dr, dc in DIRS)''',
   "pitfalls": ["Check bounds before reading the cell.", "Mutating the grid is fine in an interview if you say so; otherwise keep a seen set.", "Work from the border inwards for \"enclosed\" questions (Surrounded Regions, Pacific Atlantic)."],
   "problems": ["number-of-islands", "max-area-of-island", "flood-fill", "island-perimeter", "surrounded-regions", "pacific-atlantic-water-flow"]},
  {"id": "multi", "name": "Multi-source BFS", "when": ["distance from the nearest of many sources", "something spreads from several places at once"],
   "code": '''from collections import deque

def spread(grid, sources):
    queue = deque((r, c, 0) for r, c in sources)  # all sources start together
    seen = set(sources)
    while queue:
        r, c, d = queue.popleft()
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if (nr, nc) not in seen and inside(grid, nr, nc):
                seen.add((nr, nc))
                queue.append((nr, nc, d + 1))''',
   "pitfalls": ["Starting a BFS from each source separately is O(k·n): seed one queue with all of them."],
   "problems": ["rotting-oranges", "01-matrix", "as-far-from-land-as-possible", "walls-and-gates"]},
  {"id": "topo", "name": "Topological sort and directed cycles", "when": ["prerequisites, dependencies, build order", "\"is there an order?\" / \"return an order\"", "a cycle means it's impossible"],
   "code": '''from collections import deque

def topo_order(n, edges):            # edges: (before, after)
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for a, b in edges:
        graph[a].append(b)
        indegree[b] += 1
    queue = deque(v for v in range(n) if indegree[v] == 0)
    order = []
    while queue:
        v = queue.popleft()
        order.append(v)
        for w in graph[v]:
            indegree[w] -= 1
            if indegree[w] == 0:
                queue.append(w)
    return order if len(order) == n else []   # [] = cycle''',
   "pitfalls": ["A visited set alone can't find directed cycles: use three states, or Kahn's count.", "Mind the edge direction the problem gives you."],
   "problems": ["course-schedule", "course-schedule-ii", "alien-dictionary", "find-all-possible-recipes-from-given-supplies", "parallel-courses"]},
  {"id": "dsu", "name": "Union-Find (disjoint sets)", "when": ["merge groups and ask \"same group?\"", "edges arrive one at a time", "undirected cycle / redundant edge"],
   "code": '''class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False           # already connected: this edge closes a cycle
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        return True''',
   "pitfalls": ["Without path compression and union by size, finds degrade to O(n)."],
   "problems": ["redundant-connection", "number-of-connected-components-in-an-undirected-graph", "graph-valid-tree", "accounts-merge", "satisfiability-of-equality-equations"]},
  {"id": "bip", "name": "Two-colouring (bipartite)", "when": ["split into two groups with no conflict inside a group", "odd cycles make it impossible"],
   "code": '''def is_bipartite(graph):
    color = {}
    for start in range(len(graph)):
        if start in color:
            continue
        color[start] = 0
        stack = [start]
        while stack:
            v = stack.pop()
            for w in graph[v]:
                if w not in color:
                    color[w] = 1 - color[v]
                    stack.append(w)
                elif color[w] == color[v]:
                    return False
    return True''',
   "pitfalls": ["Colour every component, not just the one containing node 0."],
   "problems": ["is-graph-bipartite", "possible-bipartition"]},
]
