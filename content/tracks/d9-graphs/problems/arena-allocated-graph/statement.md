Build a generic graph that owns every node's value in one `Vec` and hands out `NodeId`s. Edges are
directed. `reachable` returns the nodes reachable from `from` (itself first) in BFS order, trying
neighbours in the order their edges were added.
