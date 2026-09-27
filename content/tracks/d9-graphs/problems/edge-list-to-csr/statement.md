Store a directed graph in compressed sparse row form: `targets` holds every edge's target, grouped by
source node, and node `u`'s targets are `targets[offsets[u]..offsets[u + 1]]`. `offsets` has `n + 1` entries.

Within a node, keep targets in input order. `parts` exposes both Vecs so the layout can be checked.
