`Graph` has an **associated type** `Node`: a graph has exactly one node type, so callers never have to name
it. `From<T>` has a **type parameter**: `Grid` implements it twice, once for `&str` and once for `Vec<&str>`.

Implement both graphs and both conversions, then two functions that work on *any* `Graph` whose nodes are
`Eq + Hash + Clone` (the tests define graphs of their own, including one whose nodes are borrowed `&str`s):

- `reachable` counts the nodes reachable from `start`, including `start`;
- `shortest_path` returns the nodes on a shortest path, both ends included (any shortest path will do).

- `AdjList`: `edges[i]` lists the nodes `i` has a one-way edge to.
- `Grid`: `.` is open, `#` is a wall. From an open cell you can move up, down, left or right onto an open
  cell. Rows may have different lengths; `start` is always an open cell.
