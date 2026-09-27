from author import T, write_track

P = []

NEAR = "[(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)]"

# ---------------------------------------------------------------- representation

P.append(dict(
    slug="build-an-adjacency-list", title="Build an adjacency list", level="easy", stage="representation",
    tags=["Vec<Vec<usize>>", "dedup"],
    teaches=["`vec![Vec::new(); n]` clones one empty Vec n times.", "Nodes as `usize` indices, not objects."],
    statement="""
        Build the adjacency list of an undirected graph with nodes `0..n`. Each node's list is sorted
        ascending, with no duplicates, even when `edges` repeats an edge. A self-loop `(u, u)` lists `u` once.
    """,
    examples=[("n = 4, edges = [(0, 1), (2, 1), (1, 0)]", "[[1], [0, 2], [1], []]")],
    starter="""
        pub fn adjacency_list(n: usize, edges: &[(usize, usize)]) -> Vec<Vec<usize>> {
            todo!()
        }
    """,
    solution="""
        pub fn adjacency_list(n: usize, edges: &[(usize, usize)]) -> Vec<Vec<usize>> {
            let mut adj = vec![Vec::new(); n];
            for &(u, v) in edges {
                adj[u].push(v);
                adj[v].push(u);
            }
            for list in &mut adj {
                list.sort_unstable();
                list.dedup();
            }
            adj
        }
    """,
    visible=[
        T("small", "n = 4, edges = [(0, 1), (2, 1), (1, 0)]", "adjacency_list(4, &[(0, 1), (2, 1), (1, 0)])", "vec![vec![1], vec![0, 2], vec![1], vec![]]"),
        T("no_edges", "n = 2, edges = []", "adjacency_list(2, &[])", "vec![Vec::<usize>::new(), vec![]]"),
        T("repeated_edge", "n = 3, edges = [(0, 2), (2, 0), (0, 2)]", "adjacency_list(3, &[(0, 2), (2, 0), (0, 2)])", "vec![vec![2], vec![], vec![0]]"),
        T("neighbours_sorted", "n = 4, edges = [(0, 3), (0, 1), (0, 2)]", "adjacency_list(4, &[(0, 3), (0, 1), (0, 2)])", "vec![vec![1, 2, 3], vec![0], vec![0], vec![0]]"),
        T("self_loop_once", "n = 2, edges = [(1, 1), (0, 1)]", "adjacency_list(2, &[(1, 1), (0, 1)])", "vec![vec![1], vec![0, 1]]"),
    ],
    hidden=[
        T("self_loop", "n = 1, edges = [(0, 0)]", "adjacency_list(1, &[(0, 0)])", "vec![vec![0]]"),
        T("sorted", "n = 4, edges = [(0, 3), (0, 1), (0, 2)]", "adjacency_list(4, &[(0, 3), (0, 1), (0, 2)])[0].clone()", "vec![1, 2, 3]"),
        T("zero_nodes", "n = 0, edges = []", "adjacency_list(0, &[])", "Vec::<Vec<usize>>::new()"),
        T("self_loop_among_others", "n = 2, edges = [(1, 1), (0, 1), (1, 1)]", "adjacency_list(2, &[(1, 1), (0, 1), (1, 1)])", "vec![vec![1], vec![0, 1]]"),
        T("complete_k4", "n = 4, every pair once", "adjacency_list(4, &[(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])", "vec![vec![1, 2, 3], vec![0, 2, 3], vec![0, 1, 3], vec![0, 1, 2]]"),
        T("isolated_middle", "n = 5, edges = [(4, 0)]", "adjacency_list(5, &[(4, 0)])", "vec![vec![4], vec![], vec![], vec![], vec![0]]"),
        T("both_directions_listed", "n = 3, edges = [(2, 1), (2, 0), (1, 0)]", "adjacency_list(3, &[(2, 1), (2, 0), (1, 0)])", "vec![vec![1, 2], vec![0, 2], vec![0, 1]]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(901);
            for _ in 0..300 {
                let n = 1 + rng.below(8);
                let m = rng.below(15);
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                let want: Vec<Vec<usize>> = (0..n)
                    .map(|u| (0..n).filter(|&v| edges.iter().any(|&(a, b)| (a, b) == (u, v) || (a, b) == (v, u))).collect())
                    .collect();
                check!(format!("n = {n}, edges = {edges:?}"), adjacency_list(n, &edges), want);
            }
        }

        #[test]
        fn scale_star_200k() {
            // Node 0 touches every other node, each edge listed in both directions.
            let n = 200_001;
            let edges: Vec<(usize, usize)> = (1..n).rev().flat_map(|i| [(i, 0), (0, i)]).collect();
            let adj = adjacency_list(n, &edges);
            check!("star: 0 joined to 1..=200000, each edge twice", (adj[0].len(), adj[0][0], adj[0][199_999], adj[200_000].clone()), (200_000, 1, 200_000, vec![0]));
        }
        """,
    ],
    wrong=dict(
        one_direction="""
            pub fn adjacency_list(n: usize, edges: &[(usize, usize)]) -> Vec<Vec<usize>> {
                let mut adj = vec![Vec::new(); n];
                for &(u, v) in edges {
                    adj[u].push(v);
                }
                for list in &mut adj {
                    list.sort_unstable();
                    list.dedup();
                }
                adj
            }
        """,
        no_dedup="""
            pub fn adjacency_list(n: usize, edges: &[(usize, usize)]) -> Vec<Vec<usize>> {
                let mut adj = vec![Vec::new(); n];
                for &(u, v) in edges {
                    adj[u].push(v);
                    if u != v {
                        adj[v].push(u);
                    }
                }
                for list in &mut adj {
                    list.sort_unstable();
                }
                adj
            }
        """,
        contains_check="""
            pub fn adjacency_list(n: usize, edges: &[(usize, usize)]) -> Vec<Vec<usize>> {
                let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
                for &(u, v) in edges {
                    if !adj[u].contains(&v) {
                        adj[u].push(v);
                    }
                    if !adj[v].contains(&u) {
                        adj[v].push(u);
                    }
                }
                for list in &mut adj {
                    list.sort_unstable();
                }
                adj
            }
        """,
    ),
    hints=[("rust", "`vec![Vec::new(); n]` works because `Vec` is `Clone`; each node gets its own empty list."),
           ("rust", "`sort_unstable` then `dedup` removes repeats, since `dedup` only drops adjacent equal items.")],
    notes=("Each undirected edge goes in both lists. Sorting then deduplicating handles repeated edges and the self-loop's double push.", "O(V + E log E)", "O(V + E)"),
    follow_up="When would you store neighbours in a `HashSet` or `BTreeSet` instead of a sorted `Vec`?",
    related=["S3"],
))

P.append(dict(
    slug="degree-counts-with-iterators", title="Degree counts with iterators", level="easy", stage="representation",
    tags=["fold", "iterators"],
    teaches=["`fold` with an owned accumulator.", "Closure patterns like `|&(_, &(a, _))|`."],
    statement="""
        For a directed graph with nodes `0..n`, `degrees` returns `(in_degree, out_degree)` for each node, and
        `sources` returns the nodes nothing points at, ascending.
    """,
    examples=[("n = 3, edges = [(0, 1), (0, 2), (1, 2)]", "degrees: [(0, 2), (1, 1), (2, 0)] · sources: [0]")],
    starter="""
        pub fn degrees(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
            todo!()
        }

        pub fn sources(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
            todo!()
        }
    """,
    solution="""
        pub fn degrees(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
            edges.iter().fold(vec![(0, 0); n], |mut d, &(u, v)| {
                d[u].1 += 1;
                d[v].0 += 1;
                d
            })
        }

        pub fn sources(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
            degrees(n, edges)
                .iter()
                .enumerate()
                .filter(|&(_, &(indeg, _))| indeg == 0)
                .map(|(u, _)| u)
                .collect()
        }
    """,
    visible=[
        T("triangle", "n = 3, edges = [(0, 1), (0, 2), (1, 2)]", "(degrees(3, &[(0, 1), (0, 2), (1, 2)]), sources(3, &[(0, 1), (0, 2), (1, 2)]))", "(vec![(0, 2), (1, 1), (2, 0)], vec![0])"),
        T("isolated", "n = 2, edges = []", "(degrees(2, &[]), sources(2, &[]))", "(vec![(0, 0), (0, 0)], vec![0, 1])"),
        T("fan_in", "n = 3, edges = [(0, 2), (1, 2)]", "(degrees(3, &[(0, 2), (1, 2)]), sources(3, &[(0, 2), (1, 2)]))", "(vec![(0, 1), (0, 1), (2, 0)], vec![0, 1])"),
        T("parallel_edges_count_twice", "n = 2, edges = [(1, 0), (1, 0)]", "(degrees(2, &[(1, 0), (1, 0)]), sources(2, &[(1, 0), (1, 0)]))", "(vec![(2, 0), (0, 2)], vec![1])"),
        T("self_loop_counts_both_ways", "n = 2, edges = [(1, 1)]", "(degrees(2, &[(1, 1)]), sources(2, &[(1, 1)]))", "(vec![(0, 0), (1, 1)], vec![0])"),
    ],
    hidden=[
        T("cycle", "n = 2, edges = [(0, 1), (1, 0)]", "sources(2, &[(0, 1), (1, 0)])", "Vec::<usize>::new()"),
        T("self_loop", "n = 1, edges = [(0, 0)]", "degrees(1, &[(0, 0)])", "vec![(1, 1)]"),
        T("no_nodes", "n = 0, edges = []", "(degrees(0, &[]), sources(0, &[]))", "(Vec::<(usize, usize)>::new(), Vec::<usize>::new())"),
        T("parallel_edges", "n = 2, edges = [(0, 1), (0, 1)]", "degrees(2, &[(0, 1), (0, 1)])", "vec![(0, 2), (2, 0)]"),
        T("self_loop_is_not_a_source", "n = 2, edges = [(0, 0)]", "sources(2, &[(0, 0)])", "vec![1]"),
        T("source_is_last", "n = 3, edges = [(2, 0), (2, 1)]", "sources(3, &[(2, 0), (2, 1)])", "vec![2]"),
        T("sink", "n = 4, edges = [(0, 3), (1, 3), (2, 3)]", "degrees(4, &[(0, 3), (1, 3), (2, 3)])", "vec![(0, 1), (0, 1), (0, 1), (3, 0)]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(902);
            for _ in 0..300 {
                let n = 1 + rng.below(8);
                let m = rng.below(15);
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                let want_deg: Vec<(usize, usize)> = (0..n)
                    .map(|u| (edges.iter().filter(|e| e.1 == u).count(), edges.iter().filter(|e| e.0 == u).count()))
                    .collect();
                let want_src: Vec<usize> = (0..n).filter(|&u| want_deg[u].0 == 0).collect();
                check!(format!("n = {n}, edges = {edges:?}"), (degrees(n, &edges), sources(n, &edges)), (want_deg, want_src));
            }
        }

        #[test]
        fn scale_chain_200k() {
            let n = 200_000;
            let edges: Vec<(usize, usize)> = (0..n - 1).map(|i| (i, i + 1)).collect();
            let d = degrees(n, &edges);
            let s = sources(n, &edges);
            check!("chain 0 → 1 → … → 199999", (d[0], d[100_000], d[n - 1], s), ((0, 1), (1, 1), (1, 0), vec![0]));
        }
        """,
    ],
    wrong=dict(
        swapped="""
            pub fn degrees(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
                edges.iter().fold(vec![(0, 0); n], |mut d, &(u, v)| {
                    d[u].0 += 1;
                    d[v].1 += 1;
                    d
                })
            }

            pub fn sources(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
                degrees(n, edges).iter().enumerate().filter(|&(_, &(_, out))| out == 0).map(|(u, _)| u).collect()
            }
        """,
        sources_by_scanning="""
            pub fn degrees(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
                edges.iter().fold(vec![(0, 0); n], |mut d, &(u, v)| {
                    d[u].1 += 1;
                    d[v].0 += 1;
                    d
                })
            }

            pub fn sources(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
                (0..n).filter(|&u| !edges.iter().any(|&(_, v)| v == u)).collect()
            }
        """,
        self_loops_skipped="""
            pub fn degrees(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
                edges.iter().filter(|&&(u, v)| u != v).fold(vec![(0, 0); n], |mut d, &(u, v)| {
                    d[u].1 += 1;
                    d[v].0 += 1;
                    d
                })
            }

            pub fn sources(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
                degrees(n, edges).iter().enumerate().filter(|&(_, &(indeg, _))| indeg == 0).map(|(u, _)| u).collect()
            }
        """,
    ),
    hints=[("rust", "`fold(vec![(0, 0); n], |mut d, &(u, v)| { ...; d })` moves the Vec through every step."),
           ("rust", "`enumerate` gives `(index, &item)`; destructure the tuple right in the closure's parameter.")],
    notes=("`fold` threads an owned Vec through the edges, so no `let mut` outside is needed. `sources` reuses `degrees` and filters on the first field.", "O(V + E)", "O(V)"),
    follow_up="How would you compute the same counts in parallel with rayon?",
    related=["S6"],
))

P.append(dict(
    slug="edge-list-to-csr", title="Edge list to CSR", level="medium", stage="representation",
    tags=["CSR", "prefix sums", "slices"],
    teaches=["Compressed sparse row: two flat Vecs instead of `Vec<Vec<_>>`.", "Returning `&[usize]` slices into your own storage."],
    statement="""
        Store a directed graph in compressed sparse row form: `targets` holds every edge's target, grouped by
        source node, and node `u`'s targets are `targets[offsets[u]..offsets[u + 1]]`. `offsets` has `n + 1` entries.

        Within a node, keep targets in input order. `parts` exposes both Vecs so the layout can be checked.
    """,
    examples=[("n = 3, edges = [(1, 2), (0, 1), (1, 0)]", "offsets = [0, 1, 3, 3], targets = [1, 2, 0]")],
    constraints=["0 ≤ n ≤ 10⁶", "edges.len() ≤ 10⁶"],
    starter="""
        pub struct Csr {
            offsets: Vec<usize>,
            targets: Vec<usize>,
        }

        impl Csr {
            pub fn from_edges(n: usize, edges: &[(usize, usize)]) -> Self {
                todo!()
            }

            pub fn neighbors(&self, u: usize) -> &[usize] {
                todo!()
            }

            /// (offsets, targets)
            pub fn parts(&self) -> (&[usize], &[usize]) {
                (&self.offsets, &self.targets)
            }
        }
    """,
    solution="""
        pub struct Csr {
            offsets: Vec<usize>,
            targets: Vec<usize>,
        }

        impl Csr {
            pub fn from_edges(n: usize, edges: &[(usize, usize)]) -> Self {
                let mut offsets = vec![0; n + 1];
                for &(u, _) in edges {
                    offsets[u + 1] += 1;
                }
                for i in 0..n {
                    offsets[i + 1] += offsets[i];
                }
                let mut next = offsets[..n].to_vec();
                let mut targets = vec![0; edges.len()];
                for &(u, v) in edges {
                    targets[next[u]] = v;
                    next[u] += 1;
                }
                Csr { offsets, targets }
            }

            pub fn neighbors(&self, u: usize) -> &[usize] {
                &self.targets[self.offsets[u]..self.offsets[u + 1]]
            }

            /// (offsets, targets)
            pub fn parts(&self) -> (&[usize], &[usize]) {
                (&self.offsets, &self.targets)
            }
        }
    """,
    visible=[
        T("layout", "n = 3, edges = [(1, 2), (0, 1), (1, 0)]", "Csr::from_edges(3, &[(1, 2), (0, 1), (1, 0)]).parts()", "(&[0, 1, 3, 3][..], &[1, 2, 0][..])",
          setup=""),
        T("neighbours", "n = 3, edges = [(1, 2), (0, 1), (1, 0)]; neighbors(1)", "g.neighbors(1)", "&[2, 0]",
          setup="let g = Csr::from_edges(3, &[(1, 2), (0, 1), (1, 0)]);"),
        T("node_without_edges", "n = 3, edges = [(1, 2), (0, 1), (1, 0)]; neighbors(2)", "g.neighbors(2)", "&[]",
          setup="let g = Csr::from_edges(3, &[(1, 2), (0, 1), (1, 0)]);"),
        T("targets_keep_input_order", "n = 2, edges = [(0, 1), (0, 0), (0, 1)]; neighbors(0)", "g.neighbors(0)", "&[1, 0, 1]",
          setup="let g = Csr::from_edges(2, &[(0, 1), (0, 0), (0, 1)]);"),
        T("empty_graph", "n = 0, edges = []; parts()", "g.parts()", "(&[0][..], &[][..])", setup="let g = Csr::from_edges(0, &[]);"),
    ],
    hidden=[
        T("empty_node", "n = 2, edges = [(1, 0)]; neighbors(0)", "g.neighbors(0).is_empty()", "true",
          setup="let g = Csr::from_edges(2, &[(1, 0)]);"),
        T("no_nodes", "n = 0, edges = []", "g.parts()", "(&[0][..], &[][..])", setup="let g = Csr::from_edges(0, &[]);"),
        T("million_edges", "n = 1000, 10⁶ edges", "(g.neighbors(999).len(), g.parts().1.len())", "(1000, 1_000_000)",
          setup="let edges: Vec<(usize, usize)> = (0..1_000_000).map(|i| (i % 1000, i / 1000)).collect();\nlet g = Csr::from_edges(1000, &edges);"),
        T("no_edges", "n = 3, edges = []", "g.parts()", "(&[0, 0, 0, 0][..], &[][..])", setup="let g = Csr::from_edges(3, &[]);"),
        T("all_from_last", "n = 3, edges = [(2, 0), (2, 1), (2, 2)]", "g.parts()", "(&[0, 0, 0, 3][..], &[0, 1, 2][..])",
          setup="let g = Csr::from_edges(3, &[(2, 0), (2, 1), (2, 2)]);"),
        T("input_order_kept", "n = 2, edges = [(0, 1), (1, 0), (0, 0), (0, 1)]; neighbors(0)", "g.neighbors(0)", "&[1, 0, 1]",
          setup="let g = Csr::from_edges(2, &[(0, 1), (1, 0), (0, 0), (0, 1)]);"),
        T("trailing_empty_node", "n = 4, edges = [(0, 3)]; neighbors(3)", "(g.neighbors(3).is_empty(), g.parts().0.to_vec())", "(true, vec![0, 1, 1, 1, 1])",
          setup="let g = Csr::from_edges(4, &[(0, 3)]);"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(903);
            for _ in 0..300 {
                let n = 1 + rng.below(7);
                let m = rng.below(15);
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                let g = Csr::from_edges(n, &edges);
                let got: Vec<Vec<usize>> = (0..n).map(|u| g.neighbors(u).to_vec()).collect();
                let want: Vec<Vec<usize>> = (0..n).map(|u| edges.iter().filter(|e| e.0 == u).map(|e| e.1).collect()).collect();
                let offsets: Vec<usize> = (0..=n).map(|u| edges.iter().filter(|e| e.0 < u).count()).collect();
                check!(format!("n = {n}, edges = {edges:?}"), (got, g.parts().0.to_vec()), (want, offsets));
            }
        }

        #[test]
        fn scale_200k_nodes() {
            let n = 200_000;
            let edges: Vec<(usize, usize)> = (0..n).rev().map(|i| (i * 7 % n, i)).collect();
            let g = Csr::from_edges(n, &edges);
            // Node 0 gets exactly one edge (from i = 0); the last source written is 7·1 % n = 7 → 1.
            check!("n = 200000, edges = [(i·7 % n, i) for i in n-1..=0]", (g.parts().0[n], g.neighbors(0).to_vec(), g.neighbors(7).to_vec()), (200_000, vec![0], vec![1]));
        }
        """,
    ],
    wrong=dict(
        quadratic="""
            pub struct Csr {
                offsets: Vec<usize>,
                targets: Vec<usize>,
            }

            impl Csr {
                pub fn from_edges(n: usize, edges: &[(usize, usize)]) -> Self {
                    let mut offsets = vec![0];
                    let mut targets = Vec::new();
                    for u in 0..n {
                        for &(a, b) in edges {
                            if a == u {
                                targets.push(b);
                            }
                        }
                        offsets.push(targets.len());
                    }
                    Csr { offsets, targets }
                }

                pub fn neighbors(&self, u: usize) -> &[usize] {
                    &self.targets[self.offsets[u]..self.offsets[u + 1]]
                }

                /// (offsets, targets)
                pub fn parts(&self) -> (&[usize], &[usize]) {
                    (&self.offsets, &self.targets)
                }
            }
        """,
        sorted_targets="""
            pub struct Csr {
                offsets: Vec<usize>,
                targets: Vec<usize>,
            }

            impl Csr {
                pub fn from_edges(n: usize, edges: &[(usize, usize)]) -> Self {
                    let mut sorted = edges.to_vec();
                    sorted.sort();
                    let mut offsets = vec![0; n + 1];
                    for &(u, _) in &sorted {
                        offsets[u + 1] += 1;
                    }
                    for i in 0..n {
                        offsets[i + 1] += offsets[i];
                    }
                    Csr { offsets, targets: sorted.into_iter().map(|(_, v)| v).collect() }
                }

                pub fn neighbors(&self, u: usize) -> &[usize] {
                    &self.targets[self.offsets[u]..self.offsets[u + 1]]
                }

                /// (offsets, targets)
                pub fn parts(&self) -> (&[usize], &[usize]) {
                    (&self.offsets, &self.targets)
                }
            }
        """,
    ),
    hints=[("approach", "Count each node's out-degree into `offsets[u + 1]`, then take a running sum."),
           ("approach", "Keep a copy of the start offsets as write cursors, and place each edge at its source's cursor."),
           ("rust", "`neighbors` returns a slice of `targets`; its lifetime is tied to `&self` by elision.")],
    notes=("Two passes over the edges and one prefix sum. The graph lives in two allocations instead of n + 1, which is friendlier to the cache and the allocator.", "O(V + E)", "O(V + E)"),
    follow_up="How would you add edges after construction without rebuilding everything?",
    related=["S3"],
))
P[-1]["visible"][0] = T("layout", "n = 3, edges = [(1, 2), (0, 1), (1, 0)]", "g.parts()", "(&[0, 1, 3, 3][..], &[1, 2, 0][..])",
                        setup="let g = Csr::from_edges(3, &[(1, 2), (0, 1), (1, 0)]);")

P.append(dict(
    slug="fix-a-graph-that-owns-its-nodes", title="Fix: a graph that owns its nodes", mode="fix", level="medium", stage="representation",
    tags=["E0507", "indices"],
    teaches=["A node can't own its neighbours when neighbours point back.", "Store indices; look nodes up through the graph."],
    statement="""
        `Graph` stores each node's neighbours inside the node. It doesn't compile, and it can't: in a graph
        with a cycle, every node would have to own the others.

        Change the representation so edges refer to nodes instead of owning them. Keep the public methods.
    """,
    starter="""
        #[derive(Default)]
        pub struct Graph {
            pub nodes: Vec<Node>,
        }

        pub struct Node {
            pub name: String,
            pub next: Vec<Node>,
        }

        impl Graph {
            pub fn new() -> Self {
                Graph::default()
            }

            pub fn add_node(&mut self, name: &str) -> usize {
                self.nodes.push(Node { name: name.to_string(), next: Vec::new() });
                self.nodes.len() - 1
            }

            pub fn add_edge(&mut self, from: usize, to: usize) {
                let target = self.nodes[to];
                self.nodes[from].next.push(target);
            }

            pub fn neighbors(&self, u: usize) -> Vec<&str> {
                self.nodes[u].next.iter().map(|n| n.name.as_str()).collect()
            }
        }
    """,
    solution="""
        #[derive(Default)]
        pub struct Graph {
            pub nodes: Vec<Node>,
        }

        pub struct Node {
            pub name: String,
            pub next: Vec<usize>,
        }

        impl Graph {
            pub fn new() -> Self {
                Graph::default()
            }

            pub fn add_node(&mut self, name: &str) -> usize {
                self.nodes.push(Node { name: name.to_string(), next: Vec::new() });
                self.nodes.len() - 1
            }

            pub fn add_edge(&mut self, from: usize, to: usize) {
                self.nodes[from].next.push(to);
            }

            pub fn neighbors(&self, u: usize) -> Vec<&str> {
                self.nodes[u].next.iter().map(|&v| self.nodes[v].name.as_str()).collect()
            }
        }
    """,
    visible=[
        T("cycle", "a → b, b → a; neighbors(b)", "g.neighbors(b)", 'vec!["a"]',
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\ng.add_edge(a, b);\ng.add_edge(b, a);'),
        T("rename_after_linking", "a → b, then rename b to \"b!\"; neighbors(a)", "g.neighbors(a)", 'vec!["b!"]',
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\ng.add_edge(a, b);\ng.nodes[b].name.push(\'!\');'),
        T("no_edges", "a alone; neighbors(a)", "g.neighbors(a)", "Vec::<&str>::new()", setup='let mut g = Graph::new();\nlet a = g.add_node("a");'),
        T("edges_in_insertion_order", "a → c, then a → b; neighbors(a)", "g.neighbors(a)", 'vec!["c", "b"]',
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\nlet c = g.add_node("c");\ng.add_edge(a, c);\ng.add_edge(a, b);'),
        T("repeated_edge_listed_twice", "a → b twice; neighbors(a)", "g.neighbors(a)", 'vec!["b", "b"]',
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\ng.add_edge(a, b);\ng.add_edge(a, b);'),
    ],
    hidden=[
        T("self_edge", "a → a", "g.neighbors(a)", 'vec!["a"]', setup='let mut g = Graph::new();\nlet a = g.add_node("a");\ng.add_edge(a, a);'),
        T("fan_out", "a → b, a → c", "g.neighbors(a)", 'vec!["b", "c"]',
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\nlet c = g.add_node("c");\ng.add_edge(a, b);\ng.add_edge(a, c);'),
        T("ids_are_sequential", "add three nodes", "(a, b, c)", "(0, 1, 2)",
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\nlet c = g.add_node("c");'),
        T("rename_seen_by_every_edge", "a → c, b → c, rename c to \"z\"", "(g.neighbors(a), g.neighbors(b))", '(vec!["z"], vec!["z"])',
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\nlet c = g.add_node("c");\ng.add_edge(a, c);\ng.add_edge(b, c);\ng.nodes[c].name = "z".to_string();'),
        T("unicode_names", "\"é\" → \"日本\"", "g.neighbors(a)", 'vec!["日本"]',
          setup='let mut g = Graph::new();\nlet a = g.add_node("é");\nlet b = g.add_node("日本");\ng.add_edge(a, b);'),
        T("edge_added_before_later_node_renamed", "a → b, add c, b → c, rename a; neighbors(b)", "(g.neighbors(b), g.neighbors(a))", '(vec!["c"], vec!["b"])',
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\ng.add_edge(a, b);\nlet c = g.add_node("c");\ng.add_edge(b, c);\ng.nodes[a].name.push(\'?\');'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(904);
            for _ in 0..200 {
                let n = 1 + rng.below(6);
                let m = rng.below(12);
                let names: Vec<String> = (0..n).map(|i| format!("n{i}")).collect();
                let mut g = Graph::new();
                for name in &names {
                    g.add_node(name);
                }
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                for &(u, v) in &edges {
                    g.add_edge(u, v);
                }
                for u in 0..n {
                    let want: Vec<&str> = edges.iter().filter(|e| e.0 == u).map(|e| names[e.1].as_str()).collect();
                    check!(format!("n = {n}, edges = {edges:?}; neighbors({u})"), g.neighbors(u), want);
                }
            }
        }

        #[test]
        fn long_ring() {
            let mut g = Graph::new();
            let ids: Vec<usize> = (0..100_000).map(|i| g.add_node(&i.to_string())).collect();
            for i in 0..ids.len() {
                g.add_edge(ids[i], ids[(i + 1) % ids.len()]);
            }
            check!("ring of 100000 nodes; neighbors(99999)", g.neighbors(ids[99_999]), vec!["0"]);
        }
        """,
    ],
    wrong=dict(
        copy_names="""
            #[derive(Default)]
            pub struct Graph {
                pub nodes: Vec<Node>,
            }

            pub struct Node {
                pub name: String,
                pub next: Vec<String>,
            }

            impl Graph {
                pub fn new() -> Self {
                    Graph::default()
                }

                pub fn add_node(&mut self, name: &str) -> usize {
                    self.nodes.push(Node { name: name.to_string(), next: Vec::new() });
                    self.nodes.len() - 1
                }

                pub fn add_edge(&mut self, from: usize, to: usize) {
                    let target = self.nodes[to].name.to_string();
                    self.nodes[from].next.push(target);
                }

                pub fn neighbors(&self, u: usize) -> Vec<&str> {
                    self.nodes[u].next.iter().map(|n| n.as_str()).collect()
                }
            }
        """,
        set_of_indices="""
            use std::collections::BTreeSet;

            #[derive(Default)]
            pub struct Graph {
                pub nodes: Vec<Node>,
            }

            pub struct Node {
                pub name: String,
                pub next: BTreeSet<usize>,
            }

            impl Graph {
                pub fn new() -> Self {
                    Graph::default()
                }

                pub fn add_node(&mut self, name: &str) -> usize {
                    self.nodes.push(Node { name: name.to_string(), next: BTreeSet::new() });
                    self.nodes.len() - 1
                }

                pub fn add_edge(&mut self, from: usize, to: usize) {
                    self.nodes[from].next.insert(to);
                }

                pub fn neighbors(&self, u: usize) -> Vec<&str> {
                    self.nodes[u].next.iter().map(|&v| self.nodes[v].name.as_str()).collect()
                }
            }
        """,
    ),
    hints=[("rust", "`self.nodes[to]` tries to move a node out of the Vec. Even with `clone`, you'd get a copy that goes stale."),
           ("approach", "What small, `Copy` value identifies a node and stays valid while the Vec only grows?")],
    notes=("Indices make edges cheap `Copy` handles into one owner, the `Vec<Node>`. Cycles and self-edges are just numbers, and renaming a node is visible from every edge.", "O(1) per edge", "O(V + E)"),
    follow_up="What goes wrong with plain indices once you allow removing nodes, and how do generational indices fix it?",
    rules=dict(methods=["clone"], types=["Rc", "RefCell", "Box"]),
    related=["L1", "L7"],
))

# ---------------------------------------------------------------- traversal

P.append(dict(
    slug="number-of-islands", title="Number of islands", level="easy", stage="traversal",
    tags=["flood fill", "grid", "Blind 75"],
    teaches=["Grid neighbours with `wrapping_sub` and one bounds check.", "An explicit stack instead of recursion."],
    statement="""
        `grid` is a map of `'1'` (land) and `'0'` (water). Return how many islands it has. An island is land
        connected horizontally or vertically.
    """,
    examples=[('grid = ["11000", "11000", "00100", "00011"]', "3")],
    constraints=["1 ≤ rows, cols ≤ 300"],
    starter="""
        pub fn num_islands(grid: &[&str]) -> usize {
            todo!()
        }
    """,
    solution=f"""
        pub fn num_islands(grid: &[&str]) -> usize {{
            let rows: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
            let (h, w) = (rows.len(), rows.first().map_or(0, |r| r.len()));
            let mut seen = vec![vec![false; w]; h];
            let mut count = 0;
            for r0 in 0..h {{
                for c0 in 0..w {{
                    if rows[r0][c0] != b'1' || seen[r0][c0] {{
                        continue;
                    }}
                    count += 1;
                    seen[r0][c0] = true;
                    let mut stack = vec![(r0, c0)];
                    while let Some((r, c)) = stack.pop() {{
                        for (nr, nc) in {NEAR} {{
                            if nr < h && nc < w && rows[nr][nc] == b'1' && !seen[nr][nc] {{
                                seen[nr][nc] = true;
                                stack.push((nr, nc));
                            }}
                        }}
                    }}
                }}
            }}
            count
        }}
    """,
    visible=[
        T("three", 'grid = ["11000", "11000", "00100", "00011"]', 'num_islands(&["11000", "11000", "00100", "00011"])', "3"),
        T("one_big", 'grid = ["11110", "11010", "11000", "00000"]', 'num_islands(&["11110", "11010", "11000", "00000"])', "1"),
        T("single_land", 'grid = ["1"]', 'num_islands(&["1"])', "1"),
        T("diagonals_dont_join", 'grid = ["101", "010", "101"]', 'num_islands(&["101", "010", "101"])', "5"),
        T("ring_around_a_lake", 'grid = ["111", "101", "111"]', 'num_islands(&["111", "101", "111"])', "1"),
    ],
    hidden=[
        T("all_water", 'grid = ["000"]', 'num_islands(&["000"])', "0"),
        T("diagonal_not_connected", 'grid = ["10", "01"]', 'num_islands(&["10", "01"])', "2"),
        T("big_spiral", "300×300 all land", "num_islands(&grid)", "1",
          setup='let row = "1".repeat(300);\nlet grid: Vec<&str> = (0..300).map(|_| row.as_str()).collect();'),
        T("single_row", 'grid = ["10101"]', 'num_islands(&["10101"])', "3"),
        T("single_column", 'grid = ["1", "0", "1", "1"]', 'num_islands(&["1", "0", "1", "1"])', "2"),
        T("u_shape_joins_below", 'grid = ["101", "101", "111"]', 'num_islands(&["101", "101", "111"])', "1"),
        T("comb_joined_at_the_last_cell", 'grid = ["10101", "10101", "10101", "11111"]', 'num_islands(&["10101", "10101", "10101", "11111"])', "1"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(905);
            for _ in 0..300 {
                let h = 1 + rng.below(6);
                let w = 1 + rng.below(6);
                let rows: Vec<String> = (0..h).map(|_| rng.string(w, "0011")).collect();
                let grid: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
                // Brute force: every land cell starts with its own label; spread the smallest label until nothing changes.
                let land: Vec<Vec<bool>> = rows.iter().map(|r| r.bytes().map(|b| b == b'1').collect()).collect();
                let mut label: Vec<Vec<usize>> = (0..h).map(|r| (0..w).map(|c| r * w + c).collect()).collect();
                loop {
                    let mut changed = false;
                    for r in 0..h {
                        for c in 0..w {
                            if !land[r][c] {
                                continue;
                            }
                            for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                                if nr < h && nc < w && land[nr][nc] && label[nr][nc] < label[r][c] {
                                    label[r][c] = label[nr][nc];
                                    changed = true;
                                }
                            }
                        }
                    }
                    if !changed {
                        break;
                    }
                }
                let want = (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).filter(|&(r, c)| land[r][c] && label[r][c] == r * w + c).count();
                check!(format!("grid = {rows:?}"), num_islands(&grid), want);
            }
        }

        #[test]
        fn scale_checkerboard_300() {
            let even: String = (0..300).map(|c| if c % 2 == 0 { '1' } else { '0' }).collect();
            let odd: String = (0..300).map(|c| if c % 2 == 1 { '1' } else { '0' }).collect();
            let grid: Vec<&str> = (0..300).map(|r| if r % 2 == 0 { even.as_str() } else { odd.as_str() }).collect();
            check!("300×300 checkerboard", num_islands(&grid), 45_000);
        }
        """,
    ],
    wrong=dict(
        recursive_flood="""
            pub fn num_islands(grid: &[&str]) -> usize {
                fn sink(rows: &[&[u8]], seen: &mut Vec<Vec<bool>>, r: usize, c: usize) {
                    if r >= rows.len() || c >= rows[r].len() || rows[r][c] != b'1' || seen[r][c] {
                        return;
                    }
                    seen[r][c] = true;
                    sink(rows, seen, r.wrapping_sub(1), c);
                    sink(rows, seen, r + 1, c);
                    sink(rows, seen, r, c.wrapping_sub(1));
                    sink(rows, seen, r, c + 1);
                }

                let rows: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
                let w = rows.first().map_or(0, |r| r.len());
                let mut seen = vec![vec![false; w]; rows.len()];
                let mut count = 0;
                for r in 0..rows.len() {
                    for c in 0..w {
                        if rows[r][c] == b'1' && !seen[r][c] {
                            count += 1;
                            sink(&rows, &mut seen, r, c);
                        }
                    }
                }
                count
            }
        """,
        eight_neighbours="""
            pub fn num_islands(grid: &[&str]) -> usize {
                let rows: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
                let (h, w) = (rows.len(), rows.first().map_or(0, |r| r.len()));
                let mut seen = vec![vec![false; w]; h];
                let mut count = 0;
                for r0 in 0..h {
                    for c0 in 0..w {
                        if rows[r0][c0] != b'1' || seen[r0][c0] {
                            continue;
                        }
                        count += 1;
                        seen[r0][c0] = true;
                        let mut stack = vec![(r0, c0)];
                        while let Some((r, c)) = stack.pop() {
                            for dr in [usize::MAX, 0, 1] {
                                for dc in [usize::MAX, 0, 1] {
                                    let (nr, nc) = (r.wrapping_add(dr), c.wrapping_add(dc));
                                    if nr < h && nc < w && rows[nr][nc] == b'1' && !seen[nr][nc] {
                                        seen[nr][nc] = true;
                                        stack.push((nr, nc));
                                    }
                                }
                            }
                        }
                    }
                }
                count
            }
        """,
    ),
    hints=[("approach", "Scan every cell. Each unvisited land cell starts a new island; flood it so its other cells don't count again."),
           ("rust", "`r.wrapping_sub(1)` turns -1 into `usize::MAX`, so one `nr < h` check covers both edges.")],
    notes=("Every cell is pushed at most once. The explicit stack means a 300×300 island can't overflow the call stack, which a recursive flood fill can.", "O(rows · cols)", "O(rows · cols)"),
    follow_up="How would you count islands in a grid too large to fit in memory, streamed row by row?",
))

P.append(dict(
    slug="clone-graph", title="Clone graph", level="medium", stage="traversal",
    tags=["Rc<RefCell>", "HashMap", "Blind 75"],
    teaches=["`Rc::as_ptr` as an identity key.", "Deep-copying shared, cyclic structure."],
    statement="""
        Nodes are `Rc<RefCell<Node>>` and edges are undirected (each side lists the other). Return a deep copy of
        the connected graph containing `start`: every copied node is new, and the copy has the same shape,
        cycles and self-loops included.

        ```rust
        pub struct Node { pub val: i32, pub neighbors: Vec<NodeRef> }
        pub type NodeRef = Rc<RefCell<Node>>;
        ```
    """,
    starter="""
        use std::cell::RefCell;
        use std::collections::HashMap;
        use std::rc::Rc;

        pub struct Node {
            pub val: i32,
            pub neighbors: Vec<NodeRef>,
        }

        pub type NodeRef = Rc<RefCell<Node>>;

        pub fn node(val: i32) -> NodeRef {
            Rc::new(RefCell::new(Node { val, neighbors: Vec::new() }))
        }

        pub fn link(a: &NodeRef, b: &NodeRef) {
            a.borrow_mut().neighbors.push(Rc::clone(b));
            b.borrow_mut().neighbors.push(Rc::clone(a));
        }

        pub fn clone_graph(start: &NodeRef) -> NodeRef {
            todo!()
        }
    """,
    solution="""
        use std::cell::RefCell;
        use std::collections::HashMap;
        use std::rc::Rc;

        pub struct Node {
            pub val: i32,
            pub neighbors: Vec<NodeRef>,
        }

        pub type NodeRef = Rc<RefCell<Node>>;

        pub fn node(val: i32) -> NodeRef {
            Rc::new(RefCell::new(Node { val, neighbors: Vec::new() }))
        }

        pub fn link(a: &NodeRef, b: &NodeRef) {
            a.borrow_mut().neighbors.push(Rc::clone(b));
            b.borrow_mut().neighbors.push(Rc::clone(a));
        }

        pub fn clone_graph(start: &NodeRef) -> NodeRef {
            let mut copies: HashMap<*const RefCell<Node>, NodeRef> = HashMap::new();
            copies.insert(Rc::as_ptr(start), node(start.borrow().val));
            let mut stack = vec![Rc::clone(start)];
            while let Some(old) = stack.pop() {
                let copy = Rc::clone(&copies[&Rc::as_ptr(&old)]);
                for nb in &old.borrow().neighbors {
                    let key = Rc::as_ptr(nb);
                    if !copies.contains_key(&key) {
                        copies.insert(key, node(nb.borrow().val));
                        stack.push(Rc::clone(nb));
                    }
                    copy.borrow_mut().neighbors.push(Rc::clone(&copies[&key]));
                }
            }
            Rc::clone(&copies[&Rc::as_ptr(start)])
        }
    """,
    visible=[
        T("four_cycle", "1-2-3-4-1; clone from 1", "(vals, fresh)", "(vec![2, 4], true)",
          setup="""
            let n: Vec<NodeRef> = (1..=4).map(node).collect();
            link(&n[0], &n[1]);
            link(&n[1], &n[2]);
            link(&n[2], &n[3]);
            link(&n[3], &n[0]);
            let c = clone_graph(&n[0]);
            let vals: Vec<i32> = c.borrow().neighbors.iter().map(|x| x.borrow().val).collect();
            let fresh = !n.iter().any(|x| std::rc::Rc::ptr_eq(x, &c));
          """),
        T("back_edge_is_shared", "1-2; clone 1, follow 1 → 2 → 1", "same", "true",
          setup="""
            let a = node(1);
            let b = node(2);
            link(&a, &b);
            let c = clone_graph(&a);
            let c2 = std::rc::Rc::clone(&c.borrow().neighbors[0]);
            let back = std::rc::Rc::clone(&c2.borrow().neighbors[0]);
            let same = std::rc::Rc::ptr_eq(&back, &c);
          """),
        T("single_node", "a single node 1 with no neighbours", "(c.borrow().val, c.borrow().neighbors.len(), std::rc::Rc::ptr_eq(&a, &c))", "(1, 0, false)",
          setup="let a = node(1);\nlet c = clone_graph(&a);"),
        T("neighbour_order_kept", "1 linked to 3, then 2, then 4; clone 1", "vals", "vec![3, 2, 4]",
          setup="""
            let n: Vec<NodeRef> = (1..=4).map(node).collect();
            link(&n[0], &n[2]);
            link(&n[0], &n[1]);
            link(&n[0], &n[3]);
            let c = clone_graph(&n[0]);
            let vals: Vec<i32> = c.borrow().neighbors.iter().map(|x| x.borrow().val).collect();
          """),
        T("equal_values_are_different_nodes", "two nodes both valued 5, linked; clone one", "(first_is_other_node, back_is_start)", "(true, true)",
          setup="""
            let a = node(5);
            let b = node(5);
            link(&a, &b);
            let c = clone_graph(&a);
            let first = std::rc::Rc::clone(&c.borrow().neighbors[0]);
            let first_is_other_node = !std::rc::Rc::ptr_eq(&first, &c);
            let back = std::rc::Rc::clone(&first.borrow().neighbors[0]);
            let back_is_start = std::rc::Rc::ptr_eq(&back, &c);
          """),
    ],
    hidden=[
        """
        use std::collections::HashMap;
        use std::rc::Rc;

        /// Every node reachable from `start` (BFS, no recursion): sorted (val, neighbour vals), plus the node addresses.
        fn shape(start: &NodeRef) -> (Vec<(i32, Vec<i32>)>, Vec<usize>) {
            let mut index: HashMap<usize, usize> = HashMap::new();
            let mut nodes = vec![Rc::clone(start)];
            index.insert(Rc::as_ptr(start) as usize, 0);
            let mut i = 0;
            while i < nodes.len() {
                let cur = Rc::clone(&nodes[i]);
                i += 1;
                for nb in &cur.borrow().neighbors {
                    let key = Rc::as_ptr(nb) as usize;
                    if !index.contains_key(&key) {
                        index.insert(key, nodes.len());
                        nodes.push(Rc::clone(nb));
                    }
                }
            }
            let mut out: Vec<(i32, Vec<i32>)> = nodes.iter().map(|x| (x.borrow().val, x.borrow().neighbors.iter().map(|y| y.borrow().val).collect())).collect();
            out.sort();
            (out, nodes.iter().map(|x| Rc::as_ptr(x) as usize).collect())
        }
        """,
        T("independent", "1-2; clone, set copy's val to 9; original val", "v", "1",
          setup="let a = node(1);\nlet b = node(2);\nlink(&a, &b);\nlet c = clone_graph(&a);\nc.borrow_mut().val = 9;\nlet v = a.borrow().val;"),
        T("self_loop", "1 linked to itself", "same", "true",
          setup="let a = node(1);\nlink(&a, &a);\nlet c = clone_graph(&a);\nlet first = std::rc::Rc::clone(&c.borrow().neighbors[0]);\nlet same = std::rc::Rc::ptr_eq(&first, &c) && c.borrow().neighbors.len() == 2;"),
        T("lonely", "a single node", "n", "(7, 0)", setup="let c = clone_graph(&node(7));\nlet n = (c.borrow().val, c.borrow().neighbors.len());"),
        T("clone_from_middle", "path 1-2-3; clone from 2", "shape(&c).0", "vec![(1, vec![2]), (2, vec![1, 3]), (3, vec![2])]",
          setup="let n: Vec<NodeRef> = (1..=3).map(node).collect();\nlink(&n[0], &n[1]);\nlink(&n[1], &n[2]);\nlet c = clone_graph(&n[1]);"),
        T("original_untouched", "1-2-3 triangle; clone, then add a link inside the copy; original shape", "shape(&a).0", "vec![(1, vec![2, 3]), (2, vec![1, 3]), (3, vec![2, 1])]",
          setup="let (a, b, d) = (node(1), node(2), node(3));\nlink(&a, &b);\nlink(&b, &d);\nlink(&d, &a);\nlet c = clone_graph(&a);\nlet c2 = Rc::clone(&c.borrow().neighbors[0]);\nlink(&c, &c2);"),
        T("complete_k5_negative_values", "K5 on values -1..=-5; clone from -3", "(got.0, got.1.iter().any(|p| orig.1.contains(p)))", "(orig.0.clone(), false)",
          setup="""
            let n: Vec<NodeRef> = (1..=5).map(|v| node(-v)).collect();
            for i in 0..5 {
                for j in i + 1..5 {
                    link(&n[i], &n[j]);
                }
            }
            let orig = shape(&n[2]);
            let got = shape(&clone_graph(&n[2]));
          """),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(906);
            for _ in 0..200 {
                let n = 1 + rng.below(7);
                let m = rng.below(12);
                let nodes: Vec<NodeRef> = (0..n as i32).map(node).collect();
                let mut edges = Vec::new();
                for _ in 0..m {
                    let (a, b) = (rng.below(n), rng.below(n));
                    edges.push((a, b));
                    link(&nodes[a], &nodes[b]);
                }
                let start = rng.below(n);
                let want = shape(&nodes[start]);
                let got = shape(&clone_graph(&nodes[start]));
                let shared = got.1.iter().any(|p| want.1.contains(p));
                check!(format!("n = {n}, edges = {edges:?}, start = {start}"), (got.0, shared), (want.0, false));
            }
        }

        #[test]
        fn scale_path_100k() {
            let nodes: Vec<NodeRef> = (0..100_000).map(node).collect();
            for i in 1..nodes.len() {
                link(&nodes[i - 1], &nodes[i]);
            }
            let (got, _) = shape(&clone_graph(&nodes[0]));
            check!("path 0-1-…-99999; clone from 0", (got.len(), got[99_999].clone()), (100_000, (99_999, vec![99_998])));
        }
        """,
    ],
    wrong=dict(
        keyed_by_value="""
            use std::cell::RefCell;
            use std::collections::HashMap;
            use std::rc::Rc;

            pub struct Node {
                pub val: i32,
                pub neighbors: Vec<NodeRef>,
            }

            pub type NodeRef = Rc<RefCell<Node>>;

            pub fn node(val: i32) -> NodeRef {
                Rc::new(RefCell::new(Node { val, neighbors: Vec::new() }))
            }

            pub fn link(a: &NodeRef, b: &NodeRef) {
                a.borrow_mut().neighbors.push(Rc::clone(b));
                b.borrow_mut().neighbors.push(Rc::clone(a));
            }

            pub fn clone_graph(start: &NodeRef) -> NodeRef {
                let mut copies: HashMap<i32, NodeRef> = HashMap::new();
                let v0 = start.borrow().val;
                copies.insert(v0, node(v0));
                let mut stack = vec![Rc::clone(start)];
                while let Some(old) = stack.pop() {
                    let copy = Rc::clone(&copies[&old.borrow().val]);
                    for nb in &old.borrow().neighbors {
                        let key = nb.borrow().val;
                        if !copies.contains_key(&key) {
                            copies.insert(key, node(key));
                            stack.push(Rc::clone(nb));
                        }
                        copy.borrow_mut().neighbors.push(Rc::clone(&copies[&key]));
                    }
                }
                Rc::clone(&copies[&v0])
            }
        """,
        recursive="""
            use std::cell::RefCell;
            use std::collections::HashMap;
            use std::rc::Rc;

            pub struct Node {
                pub val: i32,
                pub neighbors: Vec<NodeRef>,
            }

            pub type NodeRef = Rc<RefCell<Node>>;

            pub fn node(val: i32) -> NodeRef {
                Rc::new(RefCell::new(Node { val, neighbors: Vec::new() }))
            }

            pub fn link(a: &NodeRef, b: &NodeRef) {
                a.borrow_mut().neighbors.push(Rc::clone(b));
                b.borrow_mut().neighbors.push(Rc::clone(a));
            }

            fn go(old: &NodeRef, copies: &mut HashMap<*const RefCell<Node>, NodeRef>) -> NodeRef {
                if let Some(c) = copies.get(&Rc::as_ptr(old)) {
                    return Rc::clone(c);
                }
                let copy = node(old.borrow().val);
                copies.insert(Rc::as_ptr(old), Rc::clone(&copy));
                for nb in &old.borrow().neighbors {
                    let c = go(nb, copies);
                    copy.borrow_mut().neighbors.push(c);
                }
                copy
            }

            pub fn clone_graph(start: &NodeRef) -> NodeRef {
                go(start, &mut HashMap::new())
            }
        """,
        linear_lookup="""
            use std::cell::RefCell;
            use std::rc::Rc;

            pub struct Node {
                pub val: i32,
                pub neighbors: Vec<NodeRef>,
            }

            pub type NodeRef = Rc<RefCell<Node>>;

            pub fn node(val: i32) -> NodeRef {
                Rc::new(RefCell::new(Node { val, neighbors: Vec::new() }))
            }

            pub fn link(a: &NodeRef, b: &NodeRef) {
                a.borrow_mut().neighbors.push(Rc::clone(b));
                b.borrow_mut().neighbors.push(Rc::clone(a));
            }

            pub fn clone_graph(start: &NodeRef) -> NodeRef {
                let mut copies: Vec<(NodeRef, NodeRef)> = vec![(Rc::clone(start), node(start.borrow().val))];
                let mut stack = vec![Rc::clone(start)];
                while let Some(old) = stack.pop() {
                    let copy = Rc::clone(&copies.iter().find(|(o, _)| Rc::ptr_eq(o, &old)).unwrap().1);
                    for nb in &old.borrow().neighbors {
                        let found = copies.iter().find(|(o, _)| Rc::ptr_eq(o, nb)).map(|(_, c)| Rc::clone(c));
                        let c = match found {
                            Some(c) => c,
                            None => {
                                let c = node(nb.borrow().val);
                                copies.push((Rc::clone(nb), Rc::clone(&c)));
                                stack.push(Rc::clone(nb));
                                c
                            }
                        };
                        copy.borrow_mut().neighbors.push(c);
                    }
                }
                Rc::clone(&copies[0].1)
            }
        """,
    ),
    hints=[("approach", "Keep a map from each original node to its copy. Create a copy the first time you see a node; after that, reuse it."),
           ("rust", "`Rc::as_ptr(&rc)` is a stable address for the node, usable as a `HashMap` key."),
           ("rust", "Don't hold `borrow_mut()` on a copy while calling `borrow()` on the same copy.")],
    notes=("The map is what keeps cycles finite and shared nodes shared. Cycles of `Rc` leak when dropped; the arena-allocated graph later in this track avoids that.", "O(V + E)", "O(V)"),
    follow_up="Why does this graph leak when the last outside `Rc` is dropped, and what would you change?",
    related=["S7", "L7"],
))

P.append(dict(
    slug="fix-recursive-closure-dfs", title="Fix: recursive closure DFS", mode="fix", level="medium", stage="traversal",
    tags=["E0425", "inner fn"],
    teaches=["A closure can't call itself.", "An inner `fn` with explicit `&mut` parameters."],
    statement="`count_reachable` should return how many nodes can be reached from `start`, including it. It doesn't compile.",
    starter="""
        /// How many nodes can be reached from `start`, including `start`.
        pub fn count_reachable(adj: &[Vec<usize>], start: usize) -> usize {
            let mut seen = vec![false; adj.len()];
            let mut dfs = |u: usize| {
                if seen[u] {
                    return;
                }
                seen[u] = true;
                for &v in &adj[u] {
                    dfs(v);
                }
            };
            dfs(start);
            seen.iter().filter(|&&s| s).count()
        }
    """,
    solution="""
        /// How many nodes can be reached from `start`, including `start`.
        pub fn count_reachable(adj: &[Vec<usize>], start: usize) -> usize {
            fn dfs(adj: &[Vec<usize>], seen: &mut [bool], u: usize) {
                if seen[u] {
                    return;
                }
                seen[u] = true;
                for &v in &adj[u] {
                    dfs(adj, seen, v);
                }
            }

            let mut seen = vec![false; adj.len()];
            dfs(adj, &mut seen, start);
            seen.iter().filter(|&&s| s).count()
        }
    """,
    visible=[
        T("partial", "adj = [[1], [2], [], [0]], start = 0", "count_reachable(&[vec![1], vec![2], vec![], vec![0]], 0)", "3"),
        T("cycle", "adj = [[1], [0]], start = 1", "count_reachable(&[vec![1], vec![0]], 1)", "2"),
        T("from_the_middle", "adj = [[1], [2], [3], []], start = 2", "count_reachable(&[vec![1], vec![2], vec![3], vec![]], 2)", "2"),
        T("diamond_counts_once", "adj = [[1, 2], [3], [3], []], start = 0", "count_reachable(&[vec![1, 2], vec![3], vec![3], vec![]], 0)", "4"),
        T("edges_are_directed", "adj = [[], [0]], start = 0", "count_reachable(&[vec![], vec![0]], 0)", "1"),
    ],
    hidden=[
        T("alone", "adj = [[]], start = 0", "count_reachable(&[vec![]], 0)", "1"),
        T("self_loop", "adj = [[0], []], start = 0", "count_reachable(&[vec![0], vec![]], 0)", "1"),
        T("duplicate_edges", "adj = [[1, 1, 1], [0, 0]], start = 0", "count_reachable(&[vec![1, 1, 1], vec![0, 0]], 0)", "2"),
        T("other_component", "adj = [[1], [0], [3], [2]], start = 2", "count_reachable(&[vec![1], vec![0], vec![3], vec![2]], 2)", "2"),
        T("star", "adj = [[1, 2, 3, 4], [], [], [], []], start = 0", "count_reachable(&[vec![1, 2, 3, 4], vec![], vec![], vec![], vec![]], 0)", "5"),
        T("chain_5000", "path 0 → 1 → … → 4999, start = 0", "count_reachable(&adj, 0)", "5000",
          setup="let adj: Vec<Vec<usize>> = (0..5000).map(|i| if i + 1 < 5000 { vec![i + 1] } else { vec![] }).collect();"),
        T("many_paths", "30 layers of 2 nodes, each node → both nodes of the next layer; start = 0", "count_reachable(&adj, 0)", "59",
          setup="let adj: Vec<Vec<usize>> = (0..60).map(|u| if u / 2 < 29 { vec![u / 2 * 2 + 2, u / 2 * 2 + 3] } else { vec![] }).collect();"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(907);
            for _ in 0..300 {
                let n = 1 + rng.below(8);
                let adj: Vec<Vec<usize>> = (0..n).map(|_| { let k = rng.below(4); (0..k).map(|_| rng.below(n)).collect() }).collect();
                let start = rng.below(n);
                let mut seen = vec![false; n];
                seen[start] = true;
                let mut todo = vec![start];
                while let Some(u) = todo.pop() {
                    for &v in &adj[u] {
                        if !seen[v] {
                            seen[v] = true;
                            todo.push(v);
                        }
                    }
                }
                let want = seen.iter().filter(|&&s| s).count();
                check!(format!("adj = {adj:?}, start = {start}"), count_reachable(&adj, start), want);
            }
        }
        """,
    ],
    wrong=dict(
        marks_after_recursing="""
            /// How many nodes can be reached from `start`, including `start`.
            pub fn count_reachable(adj: &[Vec<usize>], start: usize) -> usize {
                fn dfs(adj: &[Vec<usize>], seen: &mut [bool], u: usize) {
                    if seen[u] {
                        return;
                    }
                    for &v in &adj[u] {
                        dfs(adj, seen, v);
                    }
                    seen[u] = true;
                }

                let mut seen = vec![false; adj.len()];
                dfs(adj, &mut seen, start);
                seen.iter().filter(|&&s| s).count()
            }
        """,
        seen_per_path="""
            /// How many nodes can be reached from `start`, including `start`.
            pub fn count_reachable(adj: &[Vec<usize>], start: usize) -> usize {
                fn dfs(adj: &[Vec<usize>], seen: &[bool], u: usize) -> usize {
                    if seen[u] {
                        return 0;
                    }
                    let mut seen = seen.to_vec();
                    seen[u] = true;
                    1 + adj[u].iter().map(|&v| dfs(adj, &seen, v)).sum::<usize>()
                }

                dfs(adj, &vec![false; adj.len()], start)
            }
        """,
    ),
    hints=[("rust", "Inside its own body, `dfs` doesn't exist yet: a closure has no name it can call."),
           ("rust", "Write `fn dfs(adj: &[Vec<usize>], seen: &mut [bool], u: usize)` inside the function, passing the state explicitly.")],
    notes=("An inner `fn` can recurse but can't capture, so the state it touches is passed in, which also makes the borrows explicit. For deep graphs, switch to an explicit stack (next problems).", "O(V + E)", "O(V)"),
    follow_up="Could you make a recursive closure work with `&dyn Fn`, and what would it cost?",
    rules=dict(methods=["clone"]),
    related=["D11"],
))

P.append(dict(
    slug="rotting-oranges", title="Rotting oranges", level="medium", stage="traversal",
    tags=["multi-source BFS", "VecDeque", "Option"],
    teaches=["Multi-source BFS: seed the queue with every source.", "`Option` for 'impossible' instead of `-1`."],
    statement="""
        In `grid`, `0` is empty, `1` a fresh orange and `2` a rotten one. Each minute, every fresh orange next to
        a rotten one (up, down, left, right) rots. Return the minutes until no fresh orange is left, or `None`
        if some never rot.
    """,
    examples=[("grid = [[2,1,1],[1,1,0],[0,1,1]]", "Some(4)"), ("grid = [[2,1,1],[0,1,1],[1,0,1]]", "None")],
    constraints=["1 ≤ rows, cols ≤ 500"],
    starter="""
        pub fn minutes_to_rot(grid: &[Vec<u8>]) -> Option<u32> {
            todo!()
        }
    """,
    solution=f"""
        use std::collections::VecDeque;

        pub fn minutes_to_rot(grid: &[Vec<u8>]) -> Option<u32> {{
            let mut g = grid.to_vec();
            let (h, w) = (g.len(), g.first().map_or(0, Vec::len));
            let mut queue = VecDeque::new();
            let mut fresh = 0;
            for (r, row) in g.iter().enumerate() {{
                for (c, &cell) in row.iter().enumerate() {{
                    match cell {{
                        2 => queue.push_back((r, c, 0)),
                        1 => fresh += 1,
                        _ => {{}}
                    }}
                }}
            }}
            let mut minutes = 0;
            while let Some((r, c, t)) = queue.pop_front() {{
                minutes = t;
                for (nr, nc) in {NEAR} {{
                    if nr < h && nc < w && g[nr][nc] == 1 {{
                        g[nr][nc] = 2;
                        fresh -= 1;
                        queue.push_back((nr, nc, t + 1));
                    }}
                }}
            }}
            (fresh == 0).then_some(minutes)
        }}
    """,
    visible=[
        T("four", "grid = [[2,1,1],[1,1,0],[0,1,1]]", "minutes_to_rot(&[vec![2, 1, 1], vec![1, 1, 0], vec![0, 1, 1]])", "Some(4)"),
        T("stranded", "grid = [[2,1,1],[0,1,1],[1,0,1]]", "minutes_to_rot(&[vec![2, 1, 1], vec![0, 1, 1], vec![1, 0, 1]])", "None"),
        T("no_fresh_is_zero_minutes", "grid = [[0,2]]", "minutes_to_rot(&[vec![0, 2]])", "Some(0)"),
        T("diagonal_does_not_spread", "grid = [[2,0],[0,1]]", "minutes_to_rot(&[vec![2, 0], vec![0, 1]])", "None"),
        T("all_sources_spread_at_once", "grid = [[2,1,1],[1,1,1],[1,1,2]]", "minutes_to_rot(&[vec![2, 1, 1], vec![1, 1, 1], vec![1, 1, 2]])", "Some(2)"),
    ],
    hidden=[
        T("nothing_fresh", "grid = [[0,2]]", "minutes_to_rot(&[vec![0, 2]])", "Some(0)"),
        T("no_rotten", "grid = [[1]]", "minutes_to_rot(&[vec![1]])", "None"),
        T("two_sources", "grid = [[2,1,1,1,2]]", "minutes_to_rot(&[vec![2, 1, 1, 1, 2]])", "Some(2)"),
        T("single_rotten", "grid = [[2]]", "minutes_to_rot(&[vec![2]])", "Some(0)"),
        T("all_empty", "grid = [[0,0],[0,0]]", "minutes_to_rot(&[vec![0, 0], vec![0, 0]])", "Some(0)"),
        T("walled_off", "grid = [[2,0,1]]", "minutes_to_rot(&[vec![2, 0, 1]])", "None"),
        T("column", "grid = [[2],[1],[1],[1]]", "minutes_to_rot(&[vec![2], vec![1], vec![1], vec![1]])", "Some(3)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(908);
            for _ in 0..300 {
                let h = 1 + rng.below(5);
                let w = 1 + rng.below(5);
                let grid: Vec<Vec<u8>> = (0..h).map(|_| rng.vec(w, 0, 2)).collect();
                // Brute force: simulate minute by minute.
                let mut g = grid.clone();
                let mut minutes = 0;
                let want = loop {
                    let fresh = g.iter().flatten().filter(|&&x| x == 1).count();
                    if fresh == 0 {
                        break Some(minutes);
                    }
                    let prev = g.clone();
                    for r in 0..h {
                        for c in 0..w {
                            let near = [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)];
                            if prev[r][c] == 1 && near.iter().any(|&(nr, nc)| nr < h && nc < w && prev[nr][nc] == 2) {
                                g[r][c] = 2;
                            }
                        }
                    }
                    if g == prev {
                        break None;
                    }
                    minutes += 1;
                };
                check!(format!("grid = {grid:?}"), minutes_to_rot(&grid), want);
            }
        }

        #[test]
        fn scale_snake_499x500() {
            // Full rows joined at alternating ends: one corridor 125249 cells long, rotten at its start.
            let mut grid: Vec<Vec<u8>> = (0..499)
                .map(|r| if r % 2 == 0 { vec![1; 500] } else { let mut row = vec![0; 500]; row[if r % 4 == 1 { 499 } else { 0 }] = 1; row })
                .collect();
            grid[0][0] = 2;
            check!("499×500 snake corridor, rotten at (0, 0)", minutes_to_rot(&grid), Some(125_248));
        }
        """,
    ],
    wrong=dict(
        simulate_each_minute="""
            pub fn minutes_to_rot(grid: &[Vec<u8>]) -> Option<u32> {
                let mut g = grid.to_vec();
                let (h, w) = (g.len(), g[0].len());
                let mut minutes = 0;
                loop {
                    let mut next = g.clone();
                    let mut fresh = 0;
                    let mut changed = false;
                    for r in 0..h {
                        for c in 0..w {
                            if g[r][c] != 1 {
                                continue;
                            }
                            let rotten_near = (r > 0 && g[r - 1][c] == 2) || (r + 1 < h && g[r + 1][c] == 2) || (c > 0 && g[r][c - 1] == 2) || (c + 1 < w && g[r][c + 1] == 2);
                            if rotten_near {
                                next[r][c] = 2;
                                changed = true;
                            } else {
                                fresh += 1;
                            }
                        }
                    }
                    if !changed {
                        return (fresh == 0).then_some(minutes);
                    }
                    g = next;
                    minutes += 1;
                }
            }
        """,
        counts_the_last_layer="""
            use std::collections::VecDeque;

            pub fn minutes_to_rot(grid: &[Vec<u8>]) -> Option<u32> {
                let mut g = grid.to_vec();
                let (h, w) = (g.len(), g[0].len());
                let mut queue = VecDeque::new();
                let mut fresh = 0;
                for r in 0..h {
                    for c in 0..w {
                        match g[r][c] {
                            2 => queue.push_back((r, c)),
                            1 => fresh += 1,
                            _ => {}
                        }
                    }
                }
                let mut minutes = 0;
                while !queue.is_empty() {
                    for _ in 0..queue.len() {
                        let (r, c) = queue.pop_front().unwrap();
                        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                            if nr < h && nc < w && g[nr][nc] == 1 {
                                g[nr][nc] = 2;
                                fresh -= 1;
                                queue.push_back((nr, nc));
                            }
                        }
                    }
                    minutes += 1;
                }
                (fresh == 0).then_some(minutes)
            }
        """,
    ),
    hints=[("approach", "Start the BFS from every rotten orange at once, at minute 0. The last minute you dequeue is the answer."),
           ("edge case", "Count fresh oranges first. If any are left when the queue empties, return `None`.")],
    notes=("Seeding the queue with all sources makes BFS levels equal minutes. `then_some` turns the fresh count into the `Option` result.", "O(rows · cols)", "O(rows · cols)"),
    follow_up="How would the answer change if some oranges took two minutes to spread rot?",
    related=["S1"],
))

P.append(dict(
    slug="pacific-atlantic-water-flow", title="Pacific Atlantic water flow", level="medium", stage="traversal",
    tags=["reverse BFS", "grid", "Blind 75"],
    teaches=["Search backwards from the targets instead of forwards from every cell.", "A closure returning an owned `Vec<Vec<bool>>`."],
    statement="""
        Rain flows from a cell to a neighbour (up, down, left, right) of equal or lower height. The Pacific
        touches the top and left edges; the Atlantic touches the bottom and right edges.

        Return every cell from which water can reach both oceans, in row-major order.
    """,
    examples=[("heights = [[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]", "[(0,4), (1,3), (1,4), (2,2), (3,0), (3,1), (4,0)]")],
    constraints=["1 ≤ rows, cols ≤ 300"],
    starter="""
        pub fn pacific_atlantic(heights: &[Vec<u32>]) -> Vec<(usize, usize)> {
            todo!()
        }
    """,
    solution=f"""
        pub fn pacific_atlantic(heights: &[Vec<u32>]) -> Vec<(usize, usize)> {{
            let (h, w) = (heights.len(), heights.first().map_or(0, Vec::len));
            if h == 0 || w == 0 {{
                return Vec::new();
            }}
            // Walk uphill from the ocean: every cell reached can drain into it.
            let climb = |starts: Vec<(usize, usize)>| {{
                let mut seen = vec![vec![false; w]; h];
                for &(r, c) in &starts {{
                    seen[r][c] = true;
                }}
                let mut stack = starts;
                while let Some((r, c)) = stack.pop() {{
                    for (nr, nc) in {NEAR} {{
                        if nr < h && nc < w && !seen[nr][nc] && heights[nr][nc] >= heights[r][c] {{
                            seen[nr][nc] = true;
                            stack.push((nr, nc));
                        }}
                    }}
                }}
                seen
            }};
            let pacific = climb((0..h).map(|r| (r, 0)).chain((0..w).map(|c| (0, c))).collect());
            let atlantic = climb((0..h).map(|r| (r, w - 1)).chain((0..w).map(|c| (h - 1, c))).collect());
            (0..h)
                .flat_map(|r| (0..w).map(move |c| (r, c)))
                .filter(|&(r, c)| pacific[r][c] && atlantic[r][c])
                .collect()
        }}
    """,
    visible=[
        T("example", "heights = [[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]",
          "pacific_atlantic(&[vec![1, 2, 2, 3, 5], vec![3, 2, 3, 4, 4], vec![2, 4, 5, 3, 1], vec![6, 7, 1, 4, 5], vec![5, 1, 1, 2, 4]])",
          "vec![(0, 4), (1, 3), (1, 4), (2, 2), (3, 0), (3, 1), (4, 0)]"),
        T("single", "heights = [[1]]", "pacific_atlantic(&[vec![1]])", "vec![(0, 0)]"),
        T("single_row_touches_both", "heights = [[1,2,3]]", "pacific_atlantic(&[vec![1, 2, 3]])", "vec![(0, 0), (0, 1), (0, 2)]"),
        T("pit_drains_nowhere", "heights = [[3,3,3],[3,1,3],[3,3,3]]", "pacific_atlantic(&[vec![3, 3, 3], vec![3, 1, 3], vec![3, 3, 3]])",
          "vec![(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]"),
        T("spiral", "heights = [[1,2,3],[8,9,4],[7,6,5]]", "pacific_atlantic(&[vec![1, 2, 3], vec![8, 9, 4], vec![7, 6, 5]])",
          "vec![(0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]"),
    ],
    hidden=[
        T("flat", "heights = [[3,3],[3,3]]", "pacific_atlantic(&[vec![3, 3], vec![3, 3]])", "vec![(0, 0), (0, 1), (1, 0), (1, 1)]"),
        T("valley", "heights = [[5,1,5]]", "pacific_atlantic(&[vec![5, 1, 5]])", "vec![(0, 0), (0, 1), (0, 2)]"),
        T("pit", "heights = [[3,3,3],[3,1,3],[3,3,3]]", "pacific_atlantic(&[vec![3, 3, 3], vec![3, 1, 3], vec![3, 3, 3]]).len()", "8"),
        T("single_column", "heights = [[3],[2],[1]]", "pacific_atlantic(&[vec![3], vec![2], vec![1]])", "vec![(0, 0), (1, 0), (2, 0)]"),
        T("corner_only_pacific", "heights = [[1,2],[4,3]]", "pacific_atlantic(&[vec![1, 2], vec![4, 3]])", "vec![(0, 1), (1, 0), (1, 1)]"),
        T("slope_to_the_atlantic", "heights = [[5,4,3],[4,3,2],[3,2,1]]", "pacific_atlantic(&[vec![5, 4, 3], vec![4, 3, 2], vec![3, 2, 1]])",
          "vec![(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)]"),
        T("extreme_heights", "heights = [[MAX,0,MAX],[0,MAX,0],[MAX,0,MAX]] (MAX = u32::MAX)",
          "pacific_atlantic(&[vec![u32::MAX, 0, u32::MAX], vec![0, u32::MAX, 0], vec![u32::MAX, 0, u32::MAX]])", "vec![(0, 2), (1, 1), (2, 0)]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(909);
            for _ in 0..300 {
                let h = 1 + rng.below(5);
                let w = 1 + rng.below(5);
                let heights: Vec<Vec<u32>> = (0..h).map(|_| rng.vec(w, 0, 4)).collect();
                // Brute force: search downhill from every cell.
                let mut want = Vec::new();
                for r in 0..h {
                    for c in 0..w {
                        let mut seen = vec![vec![false; w]; h];
                        seen[r][c] = true;
                        let mut stack = vec![(r, c)];
                        let (mut pacific, mut atlantic) = (false, false);
                        while let Some((a, b)) = stack.pop() {
                            pacific |= a == 0 || b == 0;
                            atlantic |= a == h - 1 || b == w - 1;
                            for (x, y) in [(a.wrapping_sub(1), b), (a + 1, b), (a, b.wrapping_sub(1)), (a, b + 1)] {
                                if x < h && y < w && !seen[x][y] && heights[x][y] <= heights[a][b] {
                                    seen[x][y] = true;
                                    stack.push((x, y));
                                }
                            }
                        }
                        if pacific && atlantic {
                            want.push((r, c));
                        }
                    }
                }
                check!(format!("heights = {heights:?}"), pacific_atlantic(&heights), want);
            }
        }

        #[test]
        fn scale_basin_300() {
            // A ring of height 10 around a flat basin of height 1: only the ring drains anywhere.
            let heights: Vec<Vec<u32>> = (0..300).map(|r| (0..300).map(|c| if r == 0 || c == 0 || r == 299 || c == 299 { 10 } else { 1 }).collect()).collect();
            let out = pacific_atlantic(&heights);
            check!("300×300 basin with a rim of height 10", (out.len(), out[0], out[298], out[299], out[1195]), (1196, (0, 0), (0, 298), (0, 299), (299, 299)));
        }
        """,
    ],
    wrong=dict(
        search_from_every_cell="""
            pub fn pacific_atlantic(heights: &[Vec<u32>]) -> Vec<(usize, usize)> {
                let (h, w) = (heights.len(), heights[0].len());
                let mut out = Vec::new();
                for r in 0..h {
                    for c in 0..w {
                        let mut seen = vec![vec![false; w]; h];
                        seen[r][c] = true;
                        let mut stack = vec![(r, c)];
                        let (mut pacific, mut atlantic) = (false, false);
                        while let Some((a, b)) = stack.pop() {
                            pacific |= a == 0 || b == 0;
                            atlantic |= a == h - 1 || b == w - 1;
                            if pacific && atlantic {
                                break;
                            }
                            for (x, y) in [(a.wrapping_sub(1), b), (a + 1, b), (a, b.wrapping_sub(1)), (a, b + 1)] {
                                if x < h && y < w && !seen[x][y] && heights[x][y] <= heights[a][b] {
                                    seen[x][y] = true;
                                    stack.push((x, y));
                                }
                            }
                        }
                        if pacific && atlantic {
                            out.push((r, c));
                        }
                    }
                }
                out
            }
        """,
        strictly_uphill="""
            pub fn pacific_atlantic(heights: &[Vec<u32>]) -> Vec<(usize, usize)> {
                let (h, w) = (heights.len(), heights[0].len());
                let climb = |starts: Vec<(usize, usize)>| {
                    let mut seen = vec![vec![false; w]; h];
                    for &(r, c) in &starts {
                        seen[r][c] = true;
                    }
                    let mut stack = starts;
                    while let Some((r, c)) = stack.pop() {
                        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                            if nr < h && nc < w && !seen[nr][nc] && heights[nr][nc] > heights[r][c] {
                                seen[nr][nc] = true;
                                stack.push((nr, nc));
                            }
                        }
                    }
                    seen
                };
                let pacific = climb((0..h).map(|r| (r, 0)).chain((0..w).map(|c| (0, c))).collect());
                let atlantic = climb((0..h).map(|r| (r, w - 1)).chain((0..w).map(|c| (h - 1, c))).collect());
                (0..h).flat_map(|r| (0..w).map(move |c| (r, c))).filter(|&(r, c)| pacific[r][c] && atlantic[r][c]).collect()
            }
        """,
    ),
    hints=[("approach", "Searching from every cell is O((rc)²). Instead, start at each ocean's shore and walk uphill."),
           ("rust", "A closure that takes the start cells and returns the `seen` grid lets you run the same search for both oceans.")],
    notes=("Two reverse searches, one per ocean, then intersect. The closure only reads `heights`, so both calls can borrow it.", "O(rows · cols)", "O(rows · cols)"),
    follow_up="How would you parallelise the two searches?",
))

P.append(dict(
    slug="iterative-dfs-with-an-explicit-stack", title="Iterative DFS with an explicit stack", level="medium", stage="traversal",
    tags=["DFS", "stack", "no recursion"],
    teaches=["Why deep recursion overflows a 2 MiB thread stack.", "Pushing neighbours in reverse to keep recursive order."],
    statement="""
        Return the order in which a recursive, preorder DFS from `start` would first visit nodes, trying each
        node's neighbours in list order. Don't recurse: the hidden tests include a path 200,000 nodes long.
    """,
    examples=[("adj = [[1, 2], [3], [3], []], start = 0", "[0, 1, 3, 2]")],
    starter="""
        pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
            todo!()
        }
    """,
    solution="""
        pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
            let mut seen = vec![false; adj.len()];
            let mut order = Vec::new();
            let mut stack = vec![start];
            while let Some(u) = stack.pop() {
                if seen[u] {
                    continue;
                }
                seen[u] = true;
                order.push(u);
                stack.extend(adj[u].iter().rev().filter(|&&v| !seen[v]));
            }
            order
        }
    """,
    visible=[
        T("diamond", "adj = [[1, 2], [3], [3], []], start = 0", "dfs_order(&[vec![1, 2], vec![3], vec![3], vec![]], 0)", "vec![0, 1, 3, 2]"),
        T("not_bfs", "adj = [[1, 2], [3], [], []], start = 0", "dfs_order(&[vec![1, 2], vec![3], vec![], vec![]], 0)", "vec![0, 1, 3, 2]"),
        T("single", "adj = [[]], start = 0", "dfs_order(&[vec![]], 0)", "vec![0]"),
        T("deeper_path_first", "adj = [[1, 2], [2, 3], [], []], start = 0", "dfs_order(&[vec![1, 2], vec![2, 3], vec![], vec![]], 0)", "vec![0, 1, 2, 3]"),
        T("unreachable_left_out", "adj = [[1], [], [0]], start = 0", "dfs_order(&[vec![1], vec![], vec![0]], 0)", "vec![0, 1]"),
    ],
    hidden=[
        T("cycle", "adj = [[1], [2], [0]], start = 1", "dfs_order(&[vec![1], vec![2], vec![0]], 1)", "vec![1, 2, 0]"),
        T("long_path", "path 0 → 1 → … → 199999", "(order.len(), order.last().copied())", "(200_000, Some(199_999))",
          setup="let adj: Vec<Vec<usize>> = (0..200_000).map(|i| if i + 1 < 200_000 { vec![i + 1] } else { vec![] }).collect();\nlet order = dfs_order(&adj, 0);"),
        T("self_loop_and_repeats", "adj = [[0, 1, 1], [0]], start = 0", "dfs_order(&[vec![0, 1, 1], vec![0]], 0)", "vec![0, 1]"),
        T("complete_k4_from_2", "adj = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]], start = 2",
          "dfs_order(&[vec![1, 2, 3], vec![0, 2, 3], vec![0, 1, 3], vec![0, 1, 2]], 2)", "vec![2, 0, 1, 3]"),
        T("start_is_last_node", "adj = [[], [0], [1, 0]], start = 2", "dfs_order(&[vec![], vec![0], vec![1, 0]], 2)", "vec![2, 1, 0]"),
        T("backtracks_to_the_root", "adj = [[1, 4], [2], [3], [], [5], []], start = 0",
          "dfs_order(&[vec![1, 4], vec![2], vec![3], vec![], vec![5], vec![]], 0)", "vec![0, 1, 2, 3, 4, 5]"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn rec(adj: &[Vec<usize>], u: usize, seen: &mut [bool], out: &mut Vec<usize>) {
                seen[u] = true;
                out.push(u);
                for &v in &adj[u] {
                    if !seen[v] {
                        rec(adj, v, seen, out);
                    }
                }
            }
            let mut rng = anneal_prelude::Rng::new(910);
            for _ in 0..300 {
                let n = 1 + rng.below(8);
                let adj: Vec<Vec<usize>> = (0..n).map(|_| { let k = rng.below(4); (0..k).map(|_| rng.below(n)).collect() }).collect();
                let start = rng.below(n);
                let mut want = Vec::new();
                rec(&adj, start, &mut vec![false; n], &mut want);
                check!(format!("adj = {adj:?}, start = {start}"), dfs_order(&adj, start), want);
            }
        }

        #[test]
        fn scale_star_with_back_edges() {
            // 0 → every node, every node → 0 and → the next node.
            let n = 200_000;
            let adj: Vec<Vec<usize>> = (0..n).map(|u| if u == 0 { (1..n).collect() } else { vec![0, (u + 1) % n] }).collect();
            let order = dfs_order(&adj, 0);
            check!("star of 200000 nodes plus a ring", (order.len(), order[1], order[n - 1]), (n, 1, n - 1));
        }
        """,
    ],
    wrong=dict(
        recursive="""
            pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
                fn go(adj: &[Vec<usize>], u: usize, seen: &mut [bool], out: &mut Vec<usize>) {
                    seen[u] = true;
                    out.push(u);
                    for &v in &adj[u] {
                        if !seen[v] {
                            go(adj, v, seen, out);
                        }
                    }
                }
                let mut out = Vec::new();
                go(adj, start, &mut vec![false; adj.len()], &mut out);
                out
            }
        """,
        mark_on_push="""
            pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
                let mut seen = vec![false; adj.len()];
                seen[start] = true;
                let mut order = Vec::new();
                let mut stack = vec![start];
                while let Some(u) = stack.pop() {
                    order.push(u);
                    for &v in adj[u].iter().rev() {
                        if !seen[v] {
                            seen[v] = true;
                            stack.push(v);
                        }
                    }
                }
                order
            }
        """,
        no_reverse="""
            pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
                let mut seen = vec![false; adj.len()];
                let mut order = Vec::new();
                let mut stack = vec![start];
                while let Some(u) = stack.pop() {
                    if seen[u] {
                        continue;
                    }
                    seen[u] = true;
                    order.push(u);
                    stack.extend(adj[u].iter().filter(|&&v| !seen[v]));
                }
                order
            }
        """,
        order_as_seen_set="""
            pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
                let mut order: Vec<usize> = Vec::new();
                let mut stack = vec![start];
                while let Some(u) = stack.pop() {
                    if order.contains(&u) {
                        continue;
                    }
                    order.push(u);
                    stack.extend(adj[u].iter().rev().filter(|v| !order.contains(v)));
                }
                order
            }
        """,
    ),
    hints=[("approach", "Mark a node visited when you pop it, not when you push it; skip it if it's already been visited."),
           ("approach", "The stack is last-in, first-out, so push the neighbours in reverse to try the first one first.")],
    notes=("Marking on pop is what makes this match recursive DFS exactly; marking on push gives a different order. Test threads get a 2 MiB stack, and 200,000 recursive frames don't fit.", "O(V + E)", "O(V + E)"),
    follow_up="How would you also record postorder (finish times) without recursion?",
))

P.append(dict(
    slug="word-ladder", title="Word ladder", level="hard", stage="traversal",
    tags=["BFS", "HashSet<&[u8]>"],
    teaches=["BFS over implicit neighbours.", "Removing from the set as you enqueue, instead of a separate `seen`."],
    statement="""
        Change `begin` into `end` one letter at a time; every intermediate word must be in `words`. Return the
        number of words in the shortest such sequence, counting both ends, or 0 if there's none. `begin` doesn't
        need to be in `words`. All words are lowercase ASCII and the same length.
    """,
    examples=[('begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log","cog"]', "5  (hit → hot → dot → dog → cog)")],
    constraints=["1 ≤ word length ≤ 10", "words.len() ≤ 2·10⁵"],
    starter="""
        pub fn ladder_length(begin: &str, end: &str, words: &[&str]) -> usize {
            todo!()
        }
    """,
    solution="""
        use std::collections::{HashSet, VecDeque};

        pub fn ladder_length(begin: &str, end: &str, words: &[&str]) -> usize {
            let mut unseen: HashSet<&[u8]> = words.iter().map(|w| w.as_bytes()).collect();
            if !unseen.contains(end.as_bytes()) {
                return 0;
            }
            unseen.remove(begin.as_bytes());
            let mut queue = VecDeque::from([(begin.as_bytes().to_vec(), 1)]);
            while let Some((mut w, steps)) = queue.pop_front() {
                if w == end.as_bytes() {
                    return steps;
                }
                for i in 0..w.len() {
                    let original = w[i];
                    for b in b'a'..=b'z' {
                        w[i] = b;
                        if b != original && unseen.remove(w.as_slice()) {
                            queue.push_back((w.to_vec(), steps + 1));
                        }
                    }
                    w[i] = original;
                }
            }
            0
        }
    """,
    visible=[
        T("five", 'begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log","cog"]', 'ladder_length("hit", "cog", &["hot", "dot", "dog", "lot", "log", "cog"])', "5"),
        T("end_missing", 'begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log"]', 'ladder_length("hit", "cog", &["hot", "dot", "dog", "lot", "log"])', "0"),
        T("counts_words_not_steps", 'begin = "hot", end = "dot", words = ["dot"]', 'ladder_length("hot", "dot", &["dot"])', "2"),
        T("begin_may_be_listed", 'begin = "hot", end = "dog", words = ["hot","dot","dog"]', 'ladder_length("hot", "dog", &["hot", "dot", "dog"])', "3"),
        T("two_letters_at_once_is_not_a_step", 'begin = "hit", end = "cog", words = ["hot","cog"]', 'ladder_length("hit", "cog", &["hot", "cog"])', "0"),
    ],
    hidden=[
        T("one_step", 'begin = "a", end = "c", words = ["a","b","c"]', 'ladder_length("a", "c", &["a", "b", "c"])', "2"),
        T("disconnected", 'begin = "ab", end = "xy", words = ["xy"]', 'ladder_length("ab", "xy", &["xy"])', "0"),
        T("many_words", "5000 three-letter words", 'ladder_length("aaa", "zzz", &refs)', "4",
          setup="let words: Vec<String> = (0..5000u32).map(|i| { let b = [b'a' + (i % 26) as u8, b'a' + (i / 26 % 26) as u8, b'a' + (i / 676 % 26) as u8]; String::from_utf8(b.to_vec()).unwrap() }).collect();\nlet mut refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();\nrefs.push(\"zzz\");"),
        T("shorter_of_two_routes", 'begin = "aaa", end = "ccc", words = ["aab","abb","bbb","bbc","bcc","ccc","aca","acc"]',
          'ladder_length("aaa", "ccc", &["aab", "abb", "bbb", "bbc", "bcc", "ccc", "aca", "acc"])', "4"),
        T("through_listed_words_only", 'begin = "hit", end = "cog", words = ["hot","cot","cog"]', 'ladder_length("hit", "cog", &["hot", "cot", "cog"])', "4"),
        T("ten_letter_words", 'begin = "abcdefghij", end = "abcdefghiz", words = ["abcdefghiz"]', 'ladder_length("abcdefghij", "abcdefghiz", &["abcdefghiz"])', "2"),
        T("duplicate_words", 'begin = "ab", end = "cb", words = ["cb","cb","ab"]', 'ladder_length("ab", "cb", &["cb", "cb", "ab"])', "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(911);
            for _ in 0..300 {
                let len = 1 + rng.below(3);
                let n = rng.below(12);
                let words: Vec<String> = (0..n).map(|_| rng.string(len, "abc")).collect();
                let begin = rng.string(len, "abc");
                let end = if n > 0 && rng.below(4) > 0 { words[rng.below(n)].clone() } else { rng.string(len, "abc") };
                // Brute force: BFS comparing every pair of words letter by letter.
                let differ_by_one = |a: &str, b: &str| a.bytes().zip(b.bytes()).filter(|(x, y)| x != y).count() == 1;
                let mut dist: Vec<Option<usize>> = vec![None; n];
                let mut queue: Vec<(String, usize)> = vec![(begin.clone(), 1)];
                let mut want = 0;
                let mut i = 0;
                if words.contains(&end) {
                    while i < queue.len() {
                        let (w, d) = queue[i].clone();
                        i += 1;
                        if w == end {
                            want = d;
                            break;
                        }
                        for j in 0..n {
                            if dist[j].is_none() && words[j] != begin && differ_by_one(&w, &words[j]) {
                                dist[j] = Some(d + 1);
                                queue.push((words[j].clone(), d + 1));
                            }
                        }
                    }
                }
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                check!(format!("begin = {begin:?}, end = {end:?}, words = {words:?}"), ladder_length(&begin, &end, &refs), want);
            }
        }

        #[test]
        fn scale_110k_words() {
            // 10⁴ reachable words ("????a" over a..j) plus 10⁵ filler words over q..z that differ from them in every letter.
            let spell = |mut i: u32, base: u8, len: usize| -> String { (0..len).map(|_| { let c = (base + (i % 10) as u8) as char; i /= 10; c }).collect() };
            let mut words: Vec<String> = (0..10_000).map(|i| spell(i, b'a', 4) + "a").collect();
            words.extend((0..100_000).map(|i| spell(i, b'q', 5)));
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            check!("10000 words ????a over a..j plus 100000 filler words over q..z, begin = \\"aaaaa\\", end = \\"jjjja\\"", ladder_length("aaaaa", "jjjja", &refs), 5);
        }
        """,
    ],
    wrong=dict(
        compare_every_pair="""
            use std::collections::VecDeque;

            pub fn ladder_length(begin: &str, end: &str, words: &[&str]) -> usize {
                if !words.contains(&end) {
                    return 0;
                }
                let differ_by_one = |a: &str, b: &str| a.bytes().zip(b.bytes()).filter(|(x, y)| x != y).count() == 1;
                let mut unseen: Vec<&str> = words.iter().copied().filter(|&w| w != begin).collect();
                let mut queue = VecDeque::from([(begin, 1)]);
                while let Some((w, steps)) = queue.pop_front() {
                    if w == end {
                        return steps;
                    }
                    let (next, rest): (Vec<&str>, Vec<&str>) = unseen.into_iter().partition(|&x| differ_by_one(w, x));
                    unseen = rest;
                    for x in next {
                        queue.push_back((x, steps + 1));
                    }
                }
                0
            }
        """,
        counts_changes="""
            use std::collections::{HashSet, VecDeque};

            pub fn ladder_length(begin: &str, end: &str, words: &[&str]) -> usize {
                let mut unseen: HashSet<&[u8]> = words.iter().map(|w| w.as_bytes()).collect();
                if !unseen.contains(end.as_bytes()) {
                    return 0;
                }
                unseen.remove(begin.as_bytes());
                let mut queue = VecDeque::from([(begin.as_bytes().to_vec(), 0)]);
                while let Some((mut w, steps)) = queue.pop_front() {
                    if w == end.as_bytes() {
                        return steps;
                    }
                    for i in 0..w.len() {
                        let original = w[i];
                        for b in b'a'..=b'z' {
                            w[i] = b;
                            if b != original && unseen.remove(w.as_slice()) {
                                queue.push_back((w.to_vec(), steps + 1));
                            }
                        }
                        w[i] = original;
                    }
                }
                0
            }
        """,
    ),
    hints=[("approach", "Words are nodes; two words are adjacent if they differ in one letter. BFS finds the shortest sequence."),
           ("approach", "Instead of comparing every pair of words, try all 26 letters at each position and look the result up."),
           ("rust", "A `HashSet<&[u8]>` borrows the input words; `remove` doubles as the visited check.")],
    notes=("Removing a word when it's enqueued means it's never enqueued twice. Generating neighbours costs 26·L lookups per word instead of comparing against every word.", "O(N · L · 26)", "O(N · L)"),
    follow_up="How would bidirectional BFS change the running time?",
    related=["S2", "S4"],
))

# ---------------------------------------------------------------- topological sort

P.append(dict(
    slug="course-schedule", title="Course schedule", level="medium", stage="topological-sort",
    tags=["Kahn's", "cycle detection", "Blind 75"],
    teaches=["Kahn's algorithm: repeatedly take nodes with in-degree 0.", "Iterative, so deep chains can't overflow."],
    statement="""
        There are `n` courses, `0..n`. `(a, b)` means course `a` must be taken before course `b`. Return whether
        every course can be finished.
    """,
    examples=[("n = 2, prereqs = [(0, 1)]", "true"), ("n = 2, prereqs = [(0, 1), (1, 0)]", "false")],
    constraints=["1 ≤ n ≤ 2·10⁵", "prereqs.len() ≤ 2·10⁵"],
    starter="""
        pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
            todo!()
        }
    """,
    solution="""
        use std::collections::VecDeque;

        pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
            let mut adj = vec![Vec::new(); n];
            let mut indeg = vec![0u32; n];
            for &(a, b) in prereqs {
                adj[a].push(b);
                indeg[b] += 1;
            }
            let mut ready: VecDeque<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
            let mut taken = 0;
            while let Some(u) = ready.pop_front() {
                taken += 1;
                for &v in &adj[u] {
                    indeg[v] -= 1;
                    if indeg[v] == 0 {
                        ready.push_back(v);
                    }
                }
            }
            taken == n
        }
    """,
    visible=[
        T("possible", "n = 2, prereqs = [(0, 1)]", "can_finish(2, &[(0, 1)])", "true"),
        T("cycle", "n = 2, prereqs = [(0, 1), (1, 0)]", "can_finish(2, &[(0, 1), (1, 0)])", "false"),
        T("no_prereqs", "n = 3, prereqs = []", "can_finish(3, &[])", "true"),
        T("diamond_is_not_a_cycle", "n = 4, prereqs = [(0, 1), (0, 2), (1, 3), (2, 3)]", "can_finish(4, &[(0, 1), (0, 2), (1, 3), (2, 3)])", "true"),
        T("cycle_after_a_free_course", "n = 3, prereqs = [(0, 1), (1, 2), (2, 1)]", "can_finish(3, &[(0, 1), (1, 2), (2, 1)])", "false"),
    ],
    hidden=[
        T("self_loop", "n = 1, prereqs = [(0, 0)]", "can_finish(1, &[(0, 0)])", "false"),
        T("cycle_off_to_the_side", "n = 4, prereqs = [(0, 1), (2, 3), (3, 2)]", "can_finish(4, &[(0, 1), (2, 3), (3, 2)])", "false"),
        T("long_chain", "n = 10⁵, chain 0 → 1 → … → 99999", "can_finish(100_000, &chain)", "true",
          setup="let chain: Vec<(usize, usize)> = (0..99_999).map(|i| (i, i + 1)).collect();"),
        T("single", "n = 1, prereqs = []", "can_finish(1, &[])", "true"),
        T("duplicate_prereq", "n = 2, prereqs = [(0, 1), (0, 1)]", "can_finish(2, &[(0, 1), (0, 1)])", "true"),
        T("three_cycle_with_tail", "n = 5, prereqs = [(0, 1), (1, 2), (2, 0), (3, 4)]", "can_finish(5, &[(0, 1), (1, 2), (2, 0), (3, 4)])", "false"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(912);
            for _ in 0..300 {
                let n = 1 + rng.below(7);
                let m = rng.below(9);
                let prereqs: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                // Brute force: keep removing a course none of the remaining courses points at.
                let mut left: Vec<usize> = (0..n).collect();
                while let Some(pos) = left.iter().position(|&u| !prereqs.iter().any(|&(a, b)| b == u && left.contains(&a))) {
                    left.remove(pos);
                }
                check!(format!("n = {n}, prereqs = {prereqs:?}"), can_finish(n, &prereqs), left.is_empty());
            }
        }

        #[test]
        fn scale_reversed_chain_200k() {
            let n = 200_000;
            let chain: Vec<(usize, usize)> = (0..n - 1).map(|i| (i + 1, i)).collect();
            check!("n = 200000, chain 199999 → … → 1 → 0", can_finish(n, &chain), true);
        }

        #[test]
        fn scale_one_big_cycle() {
            let n = 200_000;
            let edges: Vec<(usize, usize)> = (0..n).map(|i| (i, (i + 1) % n)).collect();
            check!("n = 200000, one cycle through every course", can_finish(n, &edges), false);
        }
        """,
    ],
    wrong=dict(
        recursive_dfs="""
            pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
                fn has_cycle(u: usize, adj: &[Vec<usize>], state: &mut [u8]) -> bool {
                    state[u] = 1;
                    for &v in &adj[u] {
                        if state[v] == 1 || (state[v] == 0 && has_cycle(v, adj, state)) {
                            return true;
                        }
                    }
                    state[u] = 2;
                    false
                }
                let mut adj = vec![Vec::new(); n];
                for &(a, b) in prereqs {
                    adj[a].push(b);
                }
                let mut state = vec![0u8; n];
                (0..n).all(|u| state[u] != 0 || !has_cycle(u, &adj, &mut state))
            }
        """,
        undirected_cycle_check="""
            pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
                let mut parent: Vec<usize> = (0..n).collect();
                fn root(parent: &mut [usize], mut x: usize) -> usize {
                    while parent[x] != x {
                        parent[x] = parent[parent[x]];
                        x = parent[x];
                    }
                    x
                }
                for &(a, b) in prereqs {
                    let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
                    if ra == rb {
                        return false;
                    }
                    parent[ra] = rb;
                }
                true
            }
        """,
        rescan_for_ready="""
            pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
                let mut adj = vec![Vec::new(); n];
                let mut indeg = vec![0u32; n];
                for &(a, b) in prereqs {
                    adj[a].push(b);
                    indeg[b] += 1;
                }
                let mut taken = vec![false; n];
                for _ in 0..n {
                    let Some(u) = (0..n).find(|&u| !taken[u] && indeg[u] == 0) else {
                        return false;
                    };
                    taken[u] = true;
                    for &v in &adj[u] {
                        indeg[v] -= 1;
                    }
                }
                true
            }
        """,
    ),
    hints=[("approach", "A course with no unmet prerequisites can be taken now. Taking it may free up others."),
           ("approach", "If you run out of takeable courses before taking all n, the rest are stuck in or behind a cycle.")],
    notes=("Kahn's algorithm takes each node once and touches each edge once. Unlike recursive DFS with colours, it can't overflow on a 10⁵-long chain.", "O(V + E)", "O(V + E)"),
    follow_up="How would you report one actual cycle, not just that one exists?",
))

P.append(dict(
    slug="build-order-with-cycle-report", title="Build order with cycle report", level="medium", stage="topological-sort",
    tags=["Result", "BinaryHeap", "Reverse"],
    teaches=["`Result<Vec<_>, Vec<_>>` carrying data on both sides.", "The lexicographically smallest topological order with a min-heap."],
    statement="""
        `(a, b)` means package `a` must be built before package `b`. Return `Ok(order)`: when several packages
        are ready, build the smallest number first. If some packages can never be built, return `Err` with all
        of them, ascending.
    """,
    examples=[("n = 4, deps = [(2, 0), (0, 1), (3, 1)]", "Ok([2, 0, 3, 1])"), ("n = 4, deps = [(0, 1), (1, 2), (2, 1), (2, 3)]", "Err([1, 2, 3])")],
    constraints=["1 ≤ n ≤ 2·10⁵", "deps.len() ≤ 2·10⁵"],
    starter="""
        pub fn build_order(n: usize, deps: &[(usize, usize)]) -> Result<Vec<usize>, Vec<usize>> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub fn build_order(n: usize, deps: &[(usize, usize)]) -> Result<Vec<usize>, Vec<usize>> {
            let mut adj = vec![Vec::new(); n];
            let mut indeg = vec![0u32; n];
            for &(a, b) in deps {
                adj[a].push(b);
                indeg[b] += 1;
            }
            let mut ready: BinaryHeap<Reverse<usize>> = (0..n).filter(|&u| indeg[u] == 0).map(Reverse).collect();
            let mut order = Vec::with_capacity(n);
            while let Some(Reverse(u)) = ready.pop() {
                order.push(u);
                for &v in &adj[u] {
                    indeg[v] -= 1;
                    if indeg[v] == 0 {
                        ready.push(Reverse(v));
                    }
                }
            }
            if order.len() == n {
                Ok(order)
            } else {
                Err((0..n).filter(|&u| indeg[u] > 0).collect())
            }
        }
    """,
    visible=[
        T("ok", "n = 4, deps = [(2, 0), (0, 1), (3, 1)]", "build_order(4, &[(2, 0), (0, 1), (3, 1)])", "Ok(vec![2, 0, 3, 1])"),
        T("stuck", "n = 4, deps = [(0, 1), (1, 2), (2, 1), (2, 3)]", "build_order(4, &[(0, 1), (1, 2), (2, 1), (2, 3)])", "Err(vec![1, 2, 3])"),
        T("single", "n = 1, deps = []", "build_order(1, &[])", "Ok(vec![0])"),
        T("smallest_ready_not_first_ready", "n = 4, deps = [(0, 3), (1, 2)]", "build_order(4, &[(0, 3), (1, 2)])", "Ok(vec![0, 1, 2, 3])"),
        T("self_dependency", "n = 3, deps = [(1, 1)]", "build_order(3, &[(1, 1)])", "Err(vec![1])"),
    ],
    hidden=[
        T("no_deps", "n = 3, deps = []", "build_order(3, &[])", "Ok(vec![0, 1, 2])"),
        T("smallest_first", "n = 3, deps = [(2, 1)]", "build_order(3, &[(2, 1)])", "Ok(vec![0, 2, 1])"),
        T("all_stuck", "n = 2, deps = [(0, 1), (1, 0)]", "build_order(2, &[(0, 1), (1, 0)])", "Err(vec![0, 1])"),
        T("downstream_of_a_cycle", "n = 5, deps = [(1, 2), (2, 1), (2, 3), (0, 4)]", "build_order(5, &[(1, 2), (2, 1), (2, 3), (0, 4)])", "Err(vec![1, 2, 3])"),
        T("duplicate_dependency", "n = 2, deps = [(0, 1), (0, 1)]", "build_order(2, &[(0, 1), (0, 1)])", "Ok(vec![0, 1])"),
        T("reversed_numbers", "n = 3, deps = [(2, 1), (1, 0)]", "build_order(3, &[(2, 1), (1, 0)])", "Ok(vec![2, 1, 0])"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(913);
            for _ in 0..300 {
                let n = 1 + rng.below(7);
                let m = rng.below(9);
                let deps: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                // Brute force: build the smallest package whose dependencies are all built.
                let mut built = vec![false; n];
                let mut order = Vec::new();
                while let Some(u) = (0..n).find(|&u| !built[u] && deps.iter().all(|&(a, b)| b != u || built[a])) {
                    built[u] = true;
                    order.push(u);
                }
                let want = if order.len() == n { Ok(order) } else { Err((0..n).filter(|&u| !built[u]).collect()) };
                check!(format!("n = {n}, deps = {deps:?}"), build_order(n, &deps), want);
            }
        }

        #[test]
        fn scale_reversed_chain_200k() {
            let n = 200_000;
            let deps: Vec<(usize, usize)> = (0..n - 1).map(|i| (i + 1, i)).collect();
            let out = build_order(n, &deps).unwrap();
            check!("n = 200000, deps = [(i + 1, i)]", (out.len(), out[0], out[n - 1]), (n, n - 1, 0));
        }

        #[test]
        fn scale_cycle_at_the_end() {
            // 0 → 1 → … → 199999 → 199998: everything before 199998 builds.
            let n = 200_000;
            let mut deps: Vec<(usize, usize)> = (0..n - 1).map(|i| (i, i + 1)).collect();
            deps.push((n - 1, n - 2));
            check!("n = 200000, chain with a cycle between the last two", build_order(n, &deps), Err(vec![n - 2, n - 1]));
        }
        """,
    ],
    wrong=dict(
        fifo_queue="""
            use std::collections::VecDeque;

            pub fn build_order(n: usize, deps: &[(usize, usize)]) -> Result<Vec<usize>, Vec<usize>> {
                let mut adj = vec![Vec::new(); n];
                let mut indeg = vec![0u32; n];
                for &(a, b) in deps {
                    adj[a].push(b);
                    indeg[b] += 1;
                }
                let mut ready: VecDeque<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
                let mut order = Vec::with_capacity(n);
                while let Some(u) = ready.pop_front() {
                    order.push(u);
                    for &v in &adj[u] {
                        indeg[v] -= 1;
                        if indeg[v] == 0 {
                            ready.push_back(v);
                        }
                    }
                }
                if order.len() == n {
                    Ok(order)
                } else {
                    Err((0..n).filter(|&u| indeg[u] > 0).collect())
                }
            }
        """,
        rescan_for_smallest="""
            pub fn build_order(n: usize, deps: &[(usize, usize)]) -> Result<Vec<usize>, Vec<usize>> {
                let mut adj = vec![Vec::new(); n];
                let mut indeg = vec![0u32; n];
                for &(a, b) in deps {
                    adj[a].push(b);
                    indeg[b] += 1;
                }
                let mut built = vec![false; n];
                let mut order = Vec::with_capacity(n);
                while let Some(u) = (0..n).find(|&u| !built[u] && indeg[u] == 0) {
                    built[u] = true;
                    order.push(u);
                    for &v in &adj[u] {
                        indeg[v] -= 1;
                    }
                }
                if order.len() == n {
                    Ok(order)
                } else {
                    Err((0..n).filter(|&u| !built[u]).collect())
                }
            }
        """,
    ),
    hints=[("approach", "Kahn's algorithm, but take the smallest ready package each time."),
           ("rust", "`BinaryHeap<Reverse<usize>>` pops the smallest. `.map(Reverse)` wraps while collecting."),
           ("edge case", "After the loop, the packages that can't be built are exactly those whose in-degree never reached 0.")],
    notes=("The min-heap makes the order deterministic and lexicographically smallest. Leftover in-degrees identify every package in or behind a cycle, so the error needs no extra search.", "O((V + E) log V)", "O(V + E)"),
    follow_up="How would you print one cycle as a path for the error message?",
    related=["S1", "D7"],
))

P.append(dict(
    slug="fix-invalidation-in-kahns", title="Fix: invalidation in Kahn's", mode="fix", level="medium", stage="topological-sort",
    tags=["E0502", "index loop"],
    teaches=["Pushing to the Vec you're iterating.", "A growing work list walked by index."],
    statement="`topo_order` should return a topological order, or `None` on a cycle. Nodes are processed in the order they become ready. It doesn't compile.",
    starter="""
        /// Kahn's algorithm. `(a, b)` means a comes before b. Nodes are processed
        /// in the order they become ready.
        pub fn topo_order(n: usize, edges: &[(usize, usize)]) -> Option<Vec<usize>> {
            let mut adj = vec![Vec::new(); n];
            let mut indeg = vec![0u32; n];
            for &(a, b) in edges {
                adj[a].push(b);
                indeg[b] += 1;
            }
            let mut ready: Vec<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
            let mut order = Vec::new();
            for &u in &ready {
                order.push(u);
                for &v in &adj[u] {
                    indeg[v] -= 1;
                    if indeg[v] == 0 {
                        ready.push(v);
                    }
                }
            }
            (order.len() == n).then_some(order)
        }
    """,
    solution="""
        /// Kahn's algorithm. `(a, b)` means a comes before b. Nodes are processed
        /// in the order they become ready.
        pub fn topo_order(n: usize, edges: &[(usize, usize)]) -> Option<Vec<usize>> {
            let mut adj = vec![Vec::new(); n];
            let mut indeg = vec![0u32; n];
            for &(a, b) in edges {
                adj[a].push(b);
                indeg[b] += 1;
            }
            let mut ready: Vec<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
            let mut order = Vec::new();
            let mut i = 0;
            while i < ready.len() {
                let u = ready[i];
                i += 1;
                order.push(u);
                for &v in &adj[u] {
                    indeg[v] -= 1;
                    if indeg[v] == 0 {
                        ready.push(v);
                    }
                }
            }
            (order.len() == n).then_some(order)
        }
    """,
    visible=[
        T("chain", "n = 3, edges = [(0, 1), (1, 2)]", "topo_order(3, &[(0, 1), (1, 2)])", "Some(vec![0, 1, 2])"),
        T("join", "n = 4, edges = [(0, 2), (1, 2), (2, 3)]", "topo_order(4, &[(0, 2), (1, 2), (2, 3)])", "Some(vec![0, 1, 2, 3])"),
        T("single", "n = 1, edges = []", "topo_order(1, &[])", "Some(vec![0])"),
        T("two_cycle", "n = 2, edges = [(0, 1), (1, 0)]", "topo_order(2, &[(0, 1), (1, 0)])", "None"),
        T("processed_in_ready_order", "n = 5, edges = [(0, 4), (1, 2), (2, 3)]", "topo_order(5, &[(0, 4), (1, 2), (2, 3)])", "Some(vec![0, 1, 4, 2, 3])"),
    ],
    hidden=[
        T("cycle", "n = 3, edges = [(0, 1), (1, 2), (2, 1)]", "topo_order(3, &[(0, 1), (1, 2), (2, 1)])", "None"),
        T("fifo", "n = 4, edges = [(0, 3), (1, 2)]", "topo_order(4, &[(0, 3), (1, 2)])", "Some(vec![0, 1, 3, 2])"),
        T("self_loop", "n = 1, edges = [(0, 0)]", "topo_order(1, &[(0, 0)])", "None"),
        T("no_nodes", "n = 0, edges = []", "topo_order(0, &[])", "Some(Vec::new())"),
        T("diamond", "n = 4, edges = [(0, 1), (0, 2), (1, 3), (2, 3)]", "topo_order(4, &[(0, 1), (0, 2), (1, 3), (2, 3)])", "Some(vec![0, 1, 2, 3])"),
        T("duplicate_edge", "n = 2, edges = [(0, 1), (0, 1)]", "topo_order(2, &[(0, 1), (0, 1)])", "Some(vec![0, 1])"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(914);
            for _ in 0..300 {
                let n = 1 + rng.below(7);
                let m = rng.below(9);
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                // Reference: Kahn's with a VecDeque.
                let mut indeg = vec![0; n];
                for &(_, b) in &edges {
                    indeg[b] += 1;
                }
                let mut queue: std::collections::VecDeque<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
                let mut order = Vec::new();
                while let Some(u) = queue.pop_front() {
                    order.push(u);
                    for &(a, b) in &edges {
                        if a == u {
                            indeg[b] -= 1;
                            if indeg[b] == 0 {
                                queue.push_back(b);
                            }
                        }
                    }
                }
                let want = (order.len() == n).then_some(order);
                check!(format!("n = {n}, edges = {edges:?}"), topo_order(n, &edges), want);
            }
        }

        #[test]
        fn scale_star_1m() {
            let n = 1_000_000;
            let edges: Vec<(usize, usize)> = (1..n).map(|i| (0, i)).collect();
            let out = topo_order(n, &edges).unwrap();
            check!("n = 1000000, 0 → every other node", (out.len(), out[0], out[1], out[n - 1]), (n, 0, 1, n - 1));
        }
        """,
    ],
    wrong=dict(
        pop_from_the_back="""
            /// Kahn's algorithm. `(a, b)` means a comes before b. Nodes are processed
            /// in the order they become ready.
            pub fn topo_order(n: usize, edges: &[(usize, usize)]) -> Option<Vec<usize>> {
                let mut adj = vec![Vec::new(); n];
                let mut indeg = vec![0u32; n];
                for &(a, b) in edges {
                    adj[a].push(b);
                    indeg[b] += 1;
                }
                let mut ready: Vec<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
                let mut order = Vec::new();
                while let Some(u) = ready.pop() {
                    order.push(u);
                    for &v in &adj[u] {
                        indeg[v] -= 1;
                        if indeg[v] == 0 {
                            ready.push(v);
                        }
                    }
                }
                (order.len() == n).then_some(order)
            }
        """,
        fixed_range="""
            /// Kahn's algorithm. `(a, b)` means a comes before b. Nodes are processed
            /// in the order they become ready.
            pub fn topo_order(n: usize, edges: &[(usize, usize)]) -> Option<Vec<usize>> {
                let mut adj = vec![Vec::new(); n];
                let mut indeg = vec![0u32; n];
                for &(a, b) in edges {
                    adj[a].push(b);
                    indeg[b] += 1;
                }
                let mut ready: Vec<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
                let mut order = Vec::new();
                let len = ready.len();
                for i in 0..len {
                    let u = ready[i];
                    order.push(u);
                    for &v in &adj[u] {
                        indeg[v] -= 1;
                        if indeg[v] == 0 {
                            ready.push(v);
                        }
                    }
                }
                (order.len() == n).then_some(order)
            }
        """,
        remove_from_the_front="""
            /// Kahn's algorithm. `(a, b)` means a comes before b. Nodes are processed
            /// in the order they become ready.
            pub fn topo_order(n: usize, edges: &[(usize, usize)]) -> Option<Vec<usize>> {
                let mut adj = vec![Vec::new(); n];
                let mut indeg = vec![0u32; n];
                for &(a, b) in edges {
                    adj[a].push(b);
                    indeg[b] += 1;
                }
                let mut ready: Vec<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
                let mut order = Vec::new();
                while !ready.is_empty() {
                    let u = ready.remove(0);
                    order.push(u);
                    for &v in &adj[u] {
                        indeg[v] -= 1;
                        if indeg[v] == 0 {
                            ready.push(v);
                        }
                    }
                }
                (order.len() == n).then_some(order)
            }
        """,
    ),
    hints=[("rust", "`for &u in &ready` borrows `ready` for the whole loop, so `ready.push` can't happen inside it."),
           ("approach", "Walk `ready` by index with a `while` loop; its length is re-read every time round, so pushed nodes get processed too.")],
    notes=("The index loop reads one element at a time, so no borrow spans the push. `ready` ends up equal to `order`, so one of them could go.", "O(V + E)", "O(V + E)"),
    follow_up="Which is clearer here: an index loop over a Vec, or a `VecDeque`?",
    rules=dict(methods=["clone", "to_vec"]),
    related=["L2"],
))

P.append(dict(
    slug="alien-dictionary", title="Alien dictionary", level="hard", stage="topological-sort",
    tags=["topological sort", "BTreeSet", "Blind 75"],
    teaches=["Deriving edges from adjacent pairs with `windows(2)`.", "Fixed-size arrays for a 26-letter alphabet."],
    statement="""
        `words` is sorted by an unknown order of the lowercase letters. Return an order of the letters that
        appear in `words` consistent with it. When several letters could come next, take the alphabetically
        smallest. Return `None` if no order fits (a cycle, or a word before its own prefix).
    """,
    examples=[('words = ["wrt", "wrf", "er", "ett", "rftt"]', 'Some("wertf")'), ('words = ["abc", "ab"]', "None")],
    starter="""
        pub fn alien_order(words: &[&str]) -> Option<String> {
            todo!()
        }
    """,
    solution="""
        use std::collections::BTreeSet;

        pub fn alien_order(words: &[&str]) -> Option<String> {
            let mut present = [false; 26];
            for w in words {
                for b in w.bytes() {
                    present[(b - b'a') as usize] = true;
                }
            }
            let mut before = [[false; 26]; 26];
            let mut indeg = [0u32; 26];
            for pair in words.windows(2) {
                let (a, b) = (pair[0].as_bytes(), pair[1].as_bytes());
                match a.iter().zip(b).find(|(x, y)| x != y) {
                    Some((&x, &y)) => {
                        let (x, y) = ((x - b'a') as usize, (y - b'a') as usize);
                        if !before[x][y] {
                            before[x][y] = true;
                            indeg[y] += 1;
                        }
                    }
                    None if a.len() > b.len() => return None,
                    None => {}
                }
            }
            let mut ready: BTreeSet<usize> = (0..26).filter(|&c| present[c] && indeg[c] == 0).collect();
            let mut out = String::new();
            while let Some(c) = ready.pop_first() {
                out.push((b'a' + c as u8) as char);
                for d in 0..26 {
                    if before[c][d] {
                        indeg[d] -= 1;
                        if indeg[d] == 0 {
                            ready.insert(d);
                        }
                    }
                }
            }
            (out.len() == present.iter().filter(|&&p| p).count()).then_some(out)
        }
    """,
    visible=[
        T("classic", 'words = ["wrt", "wrf", "er", "ett", "rftt"]', 'alien_order(&["wrt", "wrf", "er", "ett", "rftt"])', 'Some("wertf".to_string())'),
        T("prefix_after_word", 'words = ["abc", "ab"]', 'alien_order(&["abc", "ab"])', "None"),
        T("two_words", 'words = ["z", "x"]', 'alien_order(&["z", "x"])', 'Some("zx".to_string())'),
        T("contradiction", 'words = ["z", "x", "z"]', 'alien_order(&["z", "x", "z"])', "None"),
        T("ties_go_alphabetically", 'words = ["cb", "ca"]', 'alien_order(&["cb", "ca"])', 'Some("bac".to_string())'),
    ],
    hidden=[
        T("cycle", 'words = ["z", "x", "z"]', 'alien_order(&["z", "x", "z"])', "None"),
        T("unconstrained_letters", 'words = ["ba", "bc"]', 'alien_order(&["ba", "bc"])', 'Some("abc".to_string())'),
        T("single_word", 'words = ["zy"]', 'alien_order(&["zy"])', 'Some("yz".to_string())'),
        T("duplicate_words", 'words = ["abc", "abc"]', 'alien_order(&["abc", "abc"])', 'Some("abc".to_string())'),
        T("prefix_first_is_fine", 'words = ["ab", "abc"]', 'alien_order(&["ab", "abc"])', 'Some("abc".to_string())'),
        T("reverse_alphabet", 'words = ["z", "y", "x"]', 'alien_order(&["z", "y", "x"])', 'Some("zyx".to_string())'),
        T("prefix_later_in_the_list", 'words = ["a", "bcd", "bc"]', 'alien_order(&["a", "bcd", "bc"])', "None"),
        T("two_letter_cycle", 'words = ["ab", "ba", "aa"]', 'alien_order(&["ab", "ba", "aa"])', "None"),
        T("only_first_difference_counts", 'words = ["ca", "db", "da"]', 'alien_order(&["ca", "db", "da"])', 'Some("bacd".to_string())'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(915);
            for _ in 0..400 {
                let n = 1 + rng.below(6);
                let mut words: Vec<String> = (0..n).map(|_| { let len = 1 + rng.below(3); rng.string(len, "abcd") }).collect();
                if rng.bool() {
                    // Sort by a random alphabet so an answer exists.
                    let mut rank: Vec<u8> = (0..4).collect();
                    rng.shuffle(&mut rank);
                    words.sort_by_key(|w| w.bytes().map(|b| rank[(b - b'a') as usize]).collect::<Vec<u8>>());
                }
                // Brute force: constraints from every pair of words, not just neighbours.
                let mut present = [false; 26];
                let mut before = [[false; 26]; 26];
                let mut valid = true;
                for i in 0..n {
                    for b in words[i].bytes() {
                        present[(b - b'a') as usize] = true;
                    }
                    for j in i + 1..n {
                        let (a, b) = (words[i].as_bytes(), words[j].as_bytes());
                        match a.iter().zip(b).find(|(x, y)| x != y) {
                            Some((&x, &y)) => before[(x - b'a') as usize][(y - b'a') as usize] = true,
                            None if a.len() > b.len() => valid = false,
                            None => {}
                        }
                    }
                }
                let mut out = String::new();
                let mut done = [false; 26];
                while valid {
                    let next = (0..26).find(|&c| present[c] && !done[c] && (0..26).all(|p| !before[p][c] || done[p]));
                    match next {
                        Some(c) => {
                            done[c] = true;
                            out.push((b'a' + c as u8) as char);
                        }
                        None => break,
                    }
                }
                let want = (valid && out.len() == present.iter().filter(|&&p| p).count()).then_some(out);
                let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                check!(format!("words = {words:?}"), alien_order(&refs), want);
            }
        }

        #[test]
        fn scale_200k_words() {
            // Four-letter words counting up in an alphabet that runs z, y, x, …, a.
            let words: Vec<String> = (0..200_000u32).map(|i| (0..4).rev().map(|k| (b'z' - (i / 26u32.pow(k) % 26) as u8) as char).collect()).collect();
            let refs: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            check!("200000 words zzzz, zzzy, …, sorted by a reversed alphabet", alien_order(&refs), Some("zyxwvutsrqponmlkjihgfedcba".to_string()));
        }
        """,
    ],
    wrong=dict(
        every_pair="""
            pub fn alien_order(words: &[&str]) -> Option<String> {
                let mut present = [false; 26];
                let mut before = [[false; 26]; 26];
                for (i, w) in words.iter().enumerate() {
                    for b in w.bytes() {
                        present[(b - b'a') as usize] = true;
                    }
                    for v in &words[i + 1..] {
                        let (a, b) = (w.as_bytes(), v.as_bytes());
                        match a.iter().zip(b).find(|(x, y)| x != y) {
                            Some((&x, &y)) => before[(x - b'a') as usize][(y - b'a') as usize] = true,
                            None if a.len() > b.len() => return None,
                            None => {}
                        }
                    }
                }
                let mut out = String::new();
                let mut done = [false; 26];
                while let Some(c) = (0..26).find(|&c| present[c] && !done[c] && (0..26).all(|p| !before[p][c] || done[p])) {
                    done[c] = true;
                    out.push((b'a' + c as u8) as char);
                }
                (out.len() == present.iter().filter(|&&p| p).count()).then_some(out)
            }
        """,
        first_ready_first="""
            use std::collections::VecDeque;

            pub fn alien_order(words: &[&str]) -> Option<String> {
                let mut present = [false; 26];
                for w in words {
                    for b in w.bytes() {
                        present[(b - b'a') as usize] = true;
                    }
                }
                let mut before = [[false; 26]; 26];
                let mut indeg = [0u32; 26];
                for pair in words.windows(2) {
                    let (a, b) = (pair[0].as_bytes(), pair[1].as_bytes());
                    match a.iter().zip(b).find(|(x, y)| x != y) {
                        Some((&x, &y)) => {
                            let (x, y) = ((x - b'a') as usize, (y - b'a') as usize);
                            if !before[x][y] {
                                before[x][y] = true;
                                indeg[y] += 1;
                            }
                        }
                        None if a.len() > b.len() => return None,
                        None => {}
                    }
                }
                let mut ready: VecDeque<usize> = (0..26).filter(|&c| present[c] && indeg[c] == 0).collect();
                let mut out = String::new();
                while let Some(c) = ready.pop_front() {
                    out.push((b'a' + c as u8) as char);
                    for d in 0..26 {
                        if before[c][d] {
                            indeg[d] -= 1;
                            if indeg[d] == 0 {
                                ready.push_back(d);
                            }
                        }
                    }
                }
                (out.len() == present.iter().filter(|&&p| p).count()).then_some(out)
            }
        """,
        prefix_ignored="""
            use std::collections::BTreeSet;

            pub fn alien_order(words: &[&str]) -> Option<String> {
                let mut present = [false; 26];
                for w in words {
                    for b in w.bytes() {
                        present[(b - b'a') as usize] = true;
                    }
                }
                let mut before = [[false; 26]; 26];
                let mut indeg = [0u32; 26];
                for pair in words.windows(2) {
                    let (a, b) = (pair[0].as_bytes(), pair[1].as_bytes());
                    if let Some((&x, &y)) = a.iter().zip(b).find(|(x, y)| x != y) {
                        let (x, y) = ((x - b'a') as usize, (y - b'a') as usize);
                        if !before[x][y] {
                            before[x][y] = true;
                            indeg[y] += 1;
                        }
                    }
                }
                let mut ready: BTreeSet<usize> = (0..26).filter(|&c| present[c] && indeg[c] == 0).collect();
                let mut out = String::new();
                while let Some(c) = ready.pop_first() {
                    out.push((b'a' + c as u8) as char);
                    for d in 0..26 {
                        if before[c][d] {
                            indeg[d] -= 1;
                            if indeg[d] == 0 {
                                ready.insert(d);
                            }
                        }
                    }
                }
                (out.len() == present.iter().filter(|&&p| p).count()).then_some(out)
            }
        """,
    ),
    hints=[("approach", "Only adjacent words give information: their first differing letter says which letter comes first."),
           ("edge case", "If no letter differs and the first word is longer, the input is invalid."),
           ("rust", "`BTreeSet::pop_first` gives the smallest ready letter.")],
    notes=("Each adjacent pair adds at most one edge; a 26×26 bool matrix drops duplicates. Topological sort with the smallest ready letter makes the answer unique.", "O(total letters + 26²)", "O(26²)"),
    follow_up="How would you return every valid order instead of one?",
    related=["S2"],
))

# ---------------------------------------------------------------- shortest paths

P.append(dict(slug="network-delay-time"))  # written by hand; keeps its position

P.append(dict(
    slug="fix-heap-ordering-with-a-custom-ord", title="Fix: heap ordering with a custom Ord", mode="fix", level="medium", stage="shortest-paths",
    tags=["Ord", "PartialOrd", "BinaryHeap"],
    teaches=["`PartialOrd` must agree with `Ord`.", "Tie-breaks belong in `cmp`, or `Eq` and `Ord` disagree."],
    statement="""
        `run_order` should return job names cheapest first, ties alphabetically. It compiles but returns the
        wrong order. Fix the trait impls, not `run_order`, and don't use `Reverse`.
    """,
    starter="""
        use std::cmp::Ordering;
        use std::collections::BinaryHeap;

        #[derive(Debug, PartialEq, Eq)]
        pub struct Job {
            pub cost: u32,
            pub name: &'static str,
        }

        impl Ord for Job {
            // BinaryHeap pops the greatest, so "greater" here means "runs sooner".
            fn cmp(&self, other: &Self) -> Ordering {
                other.cost.cmp(&self.cost)
            }
        }

        impl PartialOrd for Job {
            fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                Some(self.cost.cmp(&other.cost))
            }
        }

        /// Cheapest first; ties alphabetically by name.
        pub fn run_order(jobs: Vec<Job>) -> Vec<&'static str> {
            let mut heap: BinaryHeap<Job> = jobs.into_iter().collect();
            let mut out = Vec::new();
            while let Some(job) = heap.pop() {
                out.push(job.name);
            }
            out
        }
    """,
    solution="""
        use std::cmp::Ordering;
        use std::collections::BinaryHeap;

        #[derive(Debug, PartialEq, Eq)]
        pub struct Job {
            pub cost: u32,
            pub name: &'static str,
        }

        impl Ord for Job {
            // BinaryHeap pops the greatest, so "greater" here means "runs sooner".
            fn cmp(&self, other: &Self) -> Ordering {
                other.cost.cmp(&self.cost).then_with(|| other.name.cmp(self.name))
            }
        }

        impl PartialOrd for Job {
            fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                Some(self.cmp(other))
            }
        }

        /// Cheapest first; ties alphabetically by name.
        pub fn run_order(jobs: Vec<Job>) -> Vec<&'static str> {
            let mut heap: BinaryHeap<Job> = jobs.into_iter().collect();
            let mut out = Vec::new();
            while let Some(job) = heap.pop() {
                out.push(job.name);
            }
            out
        }
    """,
    visible=[
        T("cheapest_first", "costs build 5, lint 1, test 3", 'run_order(vec![Job { cost: 5, name: "build" }, Job { cost: 1, name: "lint" }, Job { cost: 3, name: "test" }])', 'vec!["lint", "test", "build"]'),
        T("ties", "costs b 2, a 2", 'run_order(vec![Job { cost: 2, name: "b" }, Job { cost: 2, name: "a" }])', 'vec!["a", "b"]'),
        T("no_jobs", "no jobs", "run_order(vec![])", "Vec::<&str>::new()"),
        T("single_job", "costs only 4", 'run_order(vec![Job { cost: 4, name: "only" }])', 'vec!["only"]'),
        T("all_same_cost", "costs c 7, a 7, b 7", 'run_order(vec![Job { cost: 7, name: "c" }, Job { cost: 7, name: "a" }, Job { cost: 7, name: "b" }])', 'vec!["a", "b", "c"]'),
    ],
    hidden=[
        T("mixed", "costs c 1, a 2, b 1, d 0", 'run_order(vec![Job { cost: 1, name: "c" }, Job { cost: 2, name: "a" }, Job { cost: 1, name: "b" }, Job { cost: 0, name: "d" }])', 'vec!["d", "b", "c", "a"]'),
        T("consistent_with_eq", "two jobs, same cost, different names", 'Job { cost: 1, name: "a" }.cmp(&Job { cost: 1, name: "b" }) != std::cmp::Ordering::Equal', "true"),
        T("zero_and_max_cost", "costs max u32::MAX, zero 0, mid 5", 'run_order(vec![Job { cost: u32::MAX, name: "max" }, Job { cost: 0, name: "zero" }, Job { cost: 5, name: "mid" }])', 'vec!["zero", "mid", "max"]'),
        T("equal_jobs_compare_equal", "the same job twice", 'Job { cost: 3, name: "x" }.cmp(&Job { cost: 3, name: "x" })', "std::cmp::Ordering::Equal"),
        T("partial_cmp_agrees_with_cmp", "cost 1 'b' vs cost 1 'a', and cost 2 'a' vs cost 1 'z'",
          '(a.partial_cmp(&b) == Some(a.cmp(&b)), c.partial_cmp(&d) == Some(c.cmp(&d)), a.cmp(&b))', "(true, true, std::cmp::Ordering::Less)",
          setup='let (a, b) = (Job { cost: 1, name: "b" }, Job { cost: 1, name: "a" });\nlet (c, d) = (Job { cost: 2, name: "a" }, Job { cost: 1, name: "z" });'),
        T("ties_at_several_costs", "costs b 2, a 2, d 1, c 1", 'run_order(vec![Job { cost: 2, name: "b" }, Job { cost: 2, name: "a" }, Job { cost: 1, name: "d" }, Job { cost: 1, name: "c" }])', 'vec!["c", "d", "a", "b"]'),
        T("many_ties_in_reverse", "five jobs of cost 1 named e, d, c, b, a, then one of cost 0 named z",
          'run_order(vec![Job { cost: 1, name: "e" }, Job { cost: 1, name: "d" }, Job { cost: 1, name: "c" }, Job { cost: 1, name: "b" }, Job { cost: 1, name: "a" }, Job { cost: 0, name: "z" }])',
          'vec!["z", "a", "b", "c", "d", "e"]'),
        """
        #[test]
        fn random_vs_brute_force() {
            let names = ["alpha", "beta", "gamma", "delta", "eps", "zeta", "eta", "theta"];
            let mut rng = anneal_prelude::Rng::new(916);
            for _ in 0..300 {
                let n = rng.below(10);
                let jobs: Vec<(u32, &'static str)> = (0..n).map(|_| (rng.int(0, 4) as u32, *rng.pick(&names))).collect();
                let mut sorted = jobs.clone();
                sorted.sort();
                let want: Vec<&str> = sorted.iter().map(|j| j.1).collect();
                let got = run_order(jobs.iter().map(|&(cost, name)| Job { cost, name }).collect());
                check!(format!("jobs (cost, name) = {jobs:?}"), got, want);
            }
        }
        """,
    ],
    wrong=dict(
        tie_break_in_cmp_only="""
            use std::cmp::Ordering;
            use std::collections::BinaryHeap;

            #[derive(Debug, PartialEq, Eq)]
            pub struct Job {
                pub cost: u32,
                pub name: &'static str,
            }

            impl Ord for Job {
                // BinaryHeap pops the greatest, so "greater" here means "runs sooner".
                fn cmp(&self, other: &Self) -> Ordering {
                    other.cost.cmp(&self.cost).then_with(|| other.name.cmp(self.name))
                }
            }

            impl PartialOrd for Job {
                fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                    Some(other.cost.cmp(&self.cost))
                }
            }

            /// Cheapest first; ties alphabetically by name.
            pub fn run_order(jobs: Vec<Job>) -> Vec<&'static str> {
                let mut heap: BinaryHeap<Job> = jobs.into_iter().collect();
                let mut out = Vec::new();
                while let Some(job) = heap.pop() {
                    out.push(job.name);
                }
                out
            }
        """,
        tie_break_reversed="""
            use std::cmp::Ordering;
            use std::collections::BinaryHeap;

            #[derive(Debug, PartialEq, Eq)]
            pub struct Job {
                pub cost: u32,
                pub name: &'static str,
            }

            impl Ord for Job {
                // BinaryHeap pops the greatest, so "greater" here means "runs sooner".
                fn cmp(&self, other: &Self) -> Ordering {
                    other.cost.cmp(&self.cost).then_with(|| self.name.cmp(other.name))
                }
            }

            impl PartialOrd for Job {
                fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                    Some(self.cmp(other))
                }
            }

            /// Cheapest first; ties alphabetically by name.
            pub fn run_order(jobs: Vec<Job>) -> Vec<&'static str> {
                let mut heap: BinaryHeap<Job> = jobs.into_iter().collect();
                let mut out = Vec::new();
                while let Some(job) = heap.pop() {
                    out.push(job.name);
                }
                out
            }
        """,
        tie_break_in_partial_cmp_only="""
            use std::cmp::Ordering;
            use std::collections::BinaryHeap;

            #[derive(Debug, PartialEq, Eq)]
            pub struct Job {
                pub cost: u32,
                pub name: &'static str,
            }

            impl Ord for Job {
                // BinaryHeap pops the greatest, so "greater" here means "runs sooner".
                fn cmp(&self, other: &Self) -> Ordering {
                    other.cost.cmp(&self.cost)
                }
            }

            impl PartialOrd for Job {
                fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                    Some(other.cost.cmp(&self.cost).then_with(|| other.name.cmp(self.name)))
                }
            }

            /// Cheapest first; ties alphabetically by name.
            pub fn run_order(jobs: Vec<Job>) -> Vec<&'static str> {
                let mut heap: BinaryHeap<Job> = jobs.into_iter().collect();
                let mut out = Vec::new();
                while let Some(job) = heap.pop() {
                    out.push(job.name);
                }
                out
            }
        """,
    ),
    hints=[("rust", "`BinaryHeap` compares with `<` and `<=`, which come from `PartialOrd`, not `Ord`. Here the two disagree."),
           ("rust", "Implement `partial_cmp` as `Some(self.cmp(other))` so there's one source of truth."),
           ("rust", "`Eq` says two jobs with different names differ, so `cmp` must not call them `Equal`: add `.then_with(...)` on the name.")],
    notes=("The contract: `partial_cmp` agrees with `cmp`, and `cmp` returns `Equal` exactly when `==` holds. Breaking it isn't undefined behaviour, but heaps, sorts and maps give wrong answers. Clippy flags the first half with `non_canonical_partial_ord_impl`.", "O(n log n)", "O(n)"),
    follow_up="When would you reach for `Reverse` instead of a hand-written `Ord`?",
    rules=dict(types=["Reverse"]),
    related=["L4", "D7"],
))

P.append(dict(
    slug="cheapest-flights-within-k-stops", title="Cheapest flights within K stops", level="medium", stage="shortest-paths",
    tags=["Bellman–Ford", "snapshot"],
    teaches=["Bounded Bellman–Ford: one round per edge used.", "Why each round reads from a snapshot."],
    statement="""
        `flights[i] = (from, to, price)`. Return the cheapest price from `src` to `dst` using at most `k` stops
        (so at most `k + 1` flights), or `None` if there's no such route.
    """,
    examples=[("n = 3, flights = [(0,1,100), (1,2,100), (0,2,500)], src = 0, dst = 2, k = 1", "Some(200)"), ("same, k = 0", "Some(500)")],
    constraints=["1 ≤ n ≤ 100", "flights.len() ≤ n · (n − 1)", "1 ≤ price ≤ 10⁴", "0 ≤ k < n"],
    starter="""
        pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, k: usize) -> Option<u32> {
            todo!()
        }
    """,
    solution="""
        pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, k: usize) -> Option<u32> {
            let mut best = vec![u32::MAX; n];
            best[src] = 0;
            for _ in 0..=k {
                let prev = best.to_vec();
                for &(u, v, price) in flights {
                    if prev[u] != u32::MAX && prev[u] + price < best[v] {
                        best[v] = prev[u] + price;
                    }
                }
            }
            (best[dst] != u32::MAX).then_some(best[dst])
        }
    """,
    visible=[
        T("one_stop", "n = 3, flights = [(0,1,100), (1,2,100), (0,2,500)], src = 0, dst = 2, k = 1", "find_cheapest_price(3, &[(0, 1, 100), (1, 2, 100), (0, 2, 500)], 0, 2, 1)", "Some(200)"),
        T("no_stops", "same flights, k = 0", "find_cheapest_price(3, &[(0, 1, 100), (1, 2, 100), (0, 2, 500)], 0, 2, 0)", "Some(500)"),
        T("cheaper_route_needs_too_many_stops", "n = 4, flights = [(0,1,100),(1,2,100),(2,0,100),(1,3,600),(2,3,200)], src = 0, dst = 3, k = 1",
          "find_cheapest_price(4, &[(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)], 0, 3, 1)", "Some(700)"),
        T("no_route", "n = 3, flights = [(1,2,5)], src = 0, dst = 2, k = 2", "find_cheapest_price(3, &[(1, 2, 5)], 0, 2, 2)", "None"),
        T("already_there", "n = 2, flights = [(0,1,5)], src = 1, dst = 1, k = 0", "find_cheapest_price(2, &[(0, 1, 5)], 1, 1, 0)", "Some(0)"),
    ],
    hidden=[
        T("snapshot_matters", "n = 4, flights = [(0,1,100),(1,2,100),(2,0,100),(1,3,600),(2,3,200)], src = 0, dst = 3, k = 1",
          "find_cheapest_price(4, &[(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)], 0, 3, 1)", "Some(700)"),
        T("chain_order", "flights listed so one round could chain them: [(0,1,1), (1,2,1)], k = 0", "find_cheapest_price(3, &[(0, 1, 1), (1, 2, 1)], 0, 2, 0)", "None"),
        T("unreachable", "n = 2, flights = [], src = 0, dst = 1, k = 1", "find_cheapest_price(2, &[], 0, 1, 1)", "None"),
        T("more_stops_allowed_is_cheaper", "n = 4, flights = [(0,1,1),(1,2,1),(2,3,1),(0,3,10)], src = 0, dst = 3, k = 1 and k = 2",
          "(find_cheapest_price(4, &f, 0, 3, 1), find_cheapest_price(4, &f, 0, 3, 2))", "(Some(10), Some(3))",
          setup="let f = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 10)];"),
        T("parallel_flights", "n = 2, flights = [(0,1,5),(0,1,3),(0,1,4)], k = 0", "find_cheapest_price(2, &[(0, 1, 5), (0, 1, 3), (0, 1, 4)], 0, 1, 0)", "Some(3)"),
        T("long_expensive_chain", "n = 100, flights i → i+1 at 10000 each, src = 0, dst = 99, k = 98", "find_cheapest_price(100, &f, 0, 99, 98)", "Some(990_000)",
          setup="let f: Vec<(usize, usize, u32)> = (0..99).map(|i| (i, i + 1, 10_000)).collect();"),
        T("one_stop_short", "n = 100, same chain, k = 97", "find_cheapest_price(100, &f, 0, 99, 97)", "None",
          setup="let f: Vec<(usize, usize, u32)> = (0..99).map(|i| (i, i + 1, 10_000)).collect();"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn walk(flights: &[(usize, usize, u32)], at: usize, dst: usize, left: usize, cost: u32, best: &mut Option<u32>) {
                if at == dst {
                    *best = Some(best.map_or(cost, |b| b.min(cost)));
                }
                if left == 0 {
                    return;
                }
                for &(u, v, p) in flights {
                    if u == at {
                        walk(flights, v, dst, left - 1, cost + p, best);
                    }
                }
            }
            let mut rng = anneal_prelude::Rng::new(917);
            for _ in 0..300 {
                let n = 2 + rng.below(4);
                let m = rng.below(8);
                let flights: Vec<(usize, usize, u32)> = (0..m)
                    .map(|_| { let u = rng.below(n); let v = (u + 1 + rng.below(n - 1)) % n; (u, v, rng.int(1, 20) as u32) })
                    .collect();
                let (src, dst, k) = (rng.below(n), rng.below(n), rng.below(n));
                // Brute force: try every route of at most k + 1 flights.
                let mut want = None;
                walk(&flights, src, dst, k + 1, 0, &mut want);
                check!(format!("n = {n}, flights = {flights:?}, src = {src}, dst = {dst}, k = {k}"), find_cheapest_price(n, &flights, src, dst, k), want);
            }
        }

        #[test]
        fn scale_dense_100() {
            // Every pair is connected; only i → i + 1 is cheap, so each extra stop allowed saves money.
            let n = 100;
            let flights: Vec<(usize, usize, u32)> = (0..n)
                .flat_map(|i| (0..n).filter(move |&j| j != i).map(move |j| (i, j, if j == i + 1 { 1 } else { 1000 + ((i * 7919 + j * 104_729) % 997) as u32 })))
                .collect();
            let got = (find_cheapest_price(n, &flights, 0, 99, 5), find_cheapest_price(n, &flights, 0, 99, 98));
            check!("complete graph on 100 nodes, cheap chain i → i + 1; k = 5 and k = 98", got, (Some(1088), Some(99)));
        }
        """,
    ],
    wrong=dict(
        relax_in_place="""
            pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, k: usize) -> Option<u32> {
                let mut best = vec![u32::MAX; n];
                best[src] = 0;
                for _ in 0..=k {
                    for &(u, v, price) in flights {
                        if best[u] != u32::MAX && best[u] + price < best[v] {
                            best[v] = best[u] + price;
                        }
                    }
                }
                (best[dst] != u32::MAX).then_some(best[dst])
            }
        """,
        dijkstra_ignores_k="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, _k: usize) -> Option<u32> {
                let mut adj = vec![Vec::new(); n];
                for &(u, v, p) in flights {
                    adj[u].push((v, p));
                }
                let mut dist = vec![u32::MAX; n];
                dist[src] = 0;
                let mut heap = BinaryHeap::from([Reverse((0u32, src))]);
                while let Some(Reverse((d, u))) = heap.pop() {
                    if d > dist[u] {
                        continue;
                    }
                    for &(v, p) in &adj[u] {
                        if d + p < dist[v] {
                            dist[v] = d + p;
                            heap.push(Reverse((d + p, v)));
                        }
                    }
                }
                (dist[dst] != u32::MAX).then_some(dist[dst])
            }
        """,
        try_every_route="""
            pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, k: usize) -> Option<u32> {
                fn walk(adj: &[Vec<(usize, u32)>], at: usize, dst: usize, left: usize, cost: u32, best: &mut Option<u32>) {
                    if at == dst {
                        *best = Some(best.map_or(cost, |b| b.min(cost)));
                        return;
                    }
                    if left == 0 {
                        return;
                    }
                    for &(v, p) in &adj[at] {
                        walk(adj, v, dst, left - 1, cost + p, best);
                    }
                }
                let mut adj = vec![Vec::new(); n];
                for &(u, v, p) in flights {
                    adj[u].push((v, p));
                }
                let mut best = None;
                walk(&adj, src, dst, k + 1, 0, &mut best);
                best
            }
        """,
    ),
    hints=[("approach", "Dijkstra ignores the stop limit. Relax every edge once per allowed flight instead: k + 1 rounds."),
           ("edge case", "If a round reads prices it updated earlier in the same round, one round can chain several flights. Read from a copy of the previous round.")],
    notes=("After round i, `best` holds the cheapest price using at most i flights, because every relaxation reads the previous round's snapshot.", "O(k · E)", "O(n)"),
    follow_up="How would you adapt Dijkstra to this problem, and when would it beat Bellman–Ford?",
))

P.append(dict(
    slug="path-with-minimum-effort", title="Path with minimum effort", level="medium", stage="shortest-paths",
    tags=["Dijkstra", "grid", "abs_diff"],
    teaches=["Dijkstra with a max-of-edges path cost.", "`u32::abs_diff` instead of signed casts."],
    statement="""
        A route's effort is the largest height difference between consecutive cells on it. Return the least
        effort needed to go from the top-left to the bottom-right cell, moving up, down, left or right.
    """,
    examples=[("heights = [[1,2,2],[3,8,2],[5,3,5]]", "2")],
    constraints=["1 ≤ rows, cols ≤ 300", "heights ≤ 10⁶"],
    starter="""
        pub fn minimum_effort(heights: &[Vec<u32>]) -> u32 {
            todo!()
        }
    """,
    solution=f"""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub fn minimum_effort(heights: &[Vec<u32>]) -> u32 {{
            let (h, w) = (heights.len(), heights[0].len());
            let mut best = vec![vec![u32::MAX; w]; h];
            best[0][0] = 0;
            let mut heap = BinaryHeap::from([Reverse((0u32, 0usize, 0usize))]);
            while let Some(Reverse((effort, r, c))) = heap.pop() {{
                if (r, c) == (h - 1, w - 1) {{
                    return effort;
                }}
                if effort > best[r][c] {{
                    continue;
                }}
                for (nr, nc) in {NEAR} {{
                    if nr < h && nc < w {{
                        let next = effort.max(heights[r][c].abs_diff(heights[nr][nc]));
                        if next < best[nr][nc] {{
                            best[nr][nc] = next;
                            heap.push(Reverse((next, nr, nc)));
                        }}
                    }}
                }}
            }}
            unreachable!("every cell of a grid is reachable")
        }}
    """,
    visible=[
        T("two", "heights = [[1,2,2],[3,8,2],[5,3,5]]", "minimum_effort(&[vec![1, 2, 2], vec![3, 8, 2], vec![5, 3, 5]])", "2"),
        T("one", "heights = [[1,2,3],[3,8,4],[5,3,5]]", "minimum_effort(&[vec![1, 2, 3], vec![3, 8, 4], vec![5, 3, 5]])", "1"),
        T("winding_flat_path", "heights = [[1,2,1,1,1],[1,2,1,2,1],[1,2,1,2,1],[1,2,1,2,1],[1,1,1,2,1]]",
          "minimum_effort(&[vec![1, 2, 1, 1, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 1, 1, 2, 1]])", "0"),
        T("largest_step_not_sum", "heights = [[1,3,2]]", "minimum_effort(&[vec![1, 3, 2]])", "2"),
        T("path_may_turn_back", "heights = [[1,1,1],[9,9,1],[1,1,1],[1,9,9],[1,1,1]]",
          "minimum_effort(&[vec![1, 1, 1], vec![9, 9, 1], vec![1, 1, 1], vec![1, 9, 9], vec![1, 1, 1]])", "0"),
    ],
    hidden=[
        T("flat_route", "a 5×5 grid with a flat winding path", "minimum_effort(&[vec![1, 2, 1, 1, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 2, 1, 2, 1], vec![1, 1, 1, 2, 1]])", "0"),
        T("single_cell", "heights = [[7]]", "minimum_effort(&[vec![7]])", "0"),
        T("big_drop", "heights = [[0, 1000000]]", "minimum_effort(&[vec![0, 1_000_000]])", "1_000_000"),
        T("column", "heights = [[4],[1],[9]]", "minimum_effort(&[vec![4], vec![1], vec![9]])", "8"),
        T("one_row_max_step", "heights = [[1,10,6,7,9,10,4,9]]", "minimum_effort(&[vec![1, 10, 6, 7, 9, 10, 4, 9]])", "9"),
        T("all_zero", "heights = [[0,0],[0,0]]", "minimum_effort(&[vec![0, 0], vec![0, 0]])", "0"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(918);
            for _ in 0..300 {
                let h = 1 + rng.below(4);
                let w = 1 + rng.below(4);
                let heights: Vec<Vec<u32>> = (0..h).map(|_| rng.vec(w, 0, 20)).collect();
                // Brute force: the smallest limit under which a flood fill from the start reaches the end.
                let mut want = 0;
                loop {
                    let mut seen = vec![vec![false; w]; h];
                    seen[0][0] = true;
                    let mut stack = vec![(0usize, 0usize)];
                    while let Some((r, c)) = stack.pop() {
                        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                            if nr < h && nc < w && !seen[nr][nc] && heights[r][c].abs_diff(heights[nr][nc]) <= want {
                                seen[nr][nc] = true;
                                stack.push((nr, nc));
                            }
                        }
                    }
                    if seen[h - 1][w - 1] {
                        break;
                    }
                    want += 1;
                }
                check!(format!("heights = {heights:?}"), minimum_effort(&heights), want);
            }
        }

        #[test]
        fn scale_300x300() {
            let mut x: u64 = 12_345;
            let heights: Vec<Vec<u32>> = (0..300)
                .map(|_| (0..300).map(|_| { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); ((x >> 33) % 1_000_001) as u32 }).collect())
                .collect();
            check!("300×300 pseudo-random heights up to 10⁶ (LCG seed 12345)", minimum_effort(&heights), 346_912);
        }

        #[test]
        fn scale_many_distinct_steps() {
            // Flat 0 everywhere, a wall of 10⁶ in the last column, and 22350 isolated spikes of distinct heights 1, 2, ….
            let mut next = 0;
            let heights: Vec<Vec<u32>> = (0..300)
                .map(|r| (0..300).map(|c| if c == 299 { 1_000_000 } else if r % 2 == 0 && c % 2 == 0 && c <= 296 { next += 1; next } else { 0 }).collect())
                .collect();
            check!("300×300: flat, spikes 1..=22350, last column 10⁶", minimum_effort(&heights), 1_000_000);
        }
        """,
    ],
    wrong=dict(
        right_and_down_only="""
            pub fn minimum_effort(heights: &[Vec<u32>]) -> u32 {
                let (h, w) = (heights.len(), heights[0].len());
                let mut best = vec![vec![u32::MAX; w]; h];
                best[0][0] = 0;
                for r in 0..h {
                    for c in 0..w {
                        if r > 0 {
                            best[r][c] = best[r][c].min(best[r - 1][c].max(heights[r][c].abs_diff(heights[r - 1][c])));
                        }
                        if c > 0 {
                            best[r][c] = best[r][c].min(best[r][c - 1].max(heights[r][c].abs_diff(heights[r][c - 1])));
                        }
                    }
                }
                best[h - 1][w - 1]
            }
        """,
        try_every_limit="""
            pub fn minimum_effort(heights: &[Vec<u32>]) -> u32 {
                let (h, w) = (heights.len(), heights[0].len());
                let mut limits = vec![0];
                for r in 0..h {
                    for c in 0..w {
                        if r + 1 < h {
                            limits.push(heights[r][c].abs_diff(heights[r + 1][c]));
                        }
                        if c + 1 < w {
                            limits.push(heights[r][c].abs_diff(heights[r][c + 1]));
                        }
                    }
                }
                limits.sort_unstable();
                limits.dedup();
                for limit in limits {
                    let mut seen = vec![vec![false; w]; h];
                    seen[0][0] = true;
                    let mut stack = vec![(0usize, 0usize)];
                    while let Some((r, c)) = stack.pop() {
                        for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                            if nr < h && nc < w && !seen[nr][nc] && heights[r][c].abs_diff(heights[nr][nc]) <= limit {
                                seen[nr][nc] = true;
                                stack.push((nr, nc));
                            }
                        }
                    }
                    if seen[h - 1][w - 1] {
                        return limit;
                    }
                }
                unreachable!()
            }
        """,
        sum_of_steps="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn minimum_effort(heights: &[Vec<u32>]) -> u32 {
                let (h, w) = (heights.len(), heights[0].len());
                let mut best = vec![vec![u32::MAX; w]; h];
                best[0][0] = 0;
                let mut heap = BinaryHeap::from([Reverse((0u32, 0usize, 0usize))]);
                while let Some(Reverse((effort, r, c))) = heap.pop() {
                    if effort > best[r][c] {
                        continue;
                    }
                    for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                        if nr < h && nc < w {
                            let next = effort + heights[r][c].abs_diff(heights[nr][nc]);
                            if next < best[nr][nc] {
                                best[nr][nc] = next;
                                heap.push(Reverse((next, nr, nc)));
                            }
                        }
                    }
                }
                best[h - 1][w - 1]
            }
        """,
    ),
    hints=[("approach", "It's Dijkstra where a path's cost is the max edge on it, not the sum. The max is still monotone, so Dijkstra still works."),
           ("rust", "`a.abs_diff(b)` gives the unsigned difference of two `u32`s without casting to signed.")],
    notes=("Lazy deletion skips stale heap entries, and returning when the target pops is safe because costs never decrease along a path.", "O(rc log rc)", "O(rc)"),
    follow_up="Solve it with binary search on the answer plus BFS. Which is simpler to get right?",
))

P.append(dict(
    slug="zero-one-bfs-on-a-grid", title="0-1 BFS on a grid", level="hard", stage="shortest-paths",
    tags=["0-1 BFS", "VecDeque"],
    teaches=["`push_front` for 0-cost edges, `push_back` for 1-cost edges.", "Shortest paths without a heap when weights are 0 or 1."],
    statement="""
        `grid` rows are `.` (open) and `#` (wall). Walk from the top-left to the bottom-right cell, moving up,
        down, left or right. Entering a wall means breaking it. Return the fewest walls you must break.
    """,
    examples=[('grid = [".#.", ".#.", ".#."]', "1")],
    constraints=["1 ≤ rows, cols ≤ 500", "grid[0][0] is '.'"],
    starter="""
        pub fn min_walls(grid: &[&str]) -> u32 {
            todo!()
        }
    """,
    solution=f"""
        use std::collections::VecDeque;

        pub fn min_walls(grid: &[&str]) -> u32 {{
            let g: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
            let (h, w) = (g.len(), g[0].len());
            let mut dist = vec![vec![u32::MAX; w]; h];
            dist[0][0] = 0;
            let mut deque = VecDeque::from([(0usize, 0usize)]);
            while let Some((r, c)) = deque.pop_front() {{
                let d = dist[r][c];
                for (nr, nc) in {NEAR} {{
                    if nr >= h || nc >= w {{
                        continue;
                    }}
                    let cost = u32::from(g[nr][nc] == b'#');
                    if d + cost < dist[nr][nc] {{
                        dist[nr][nc] = d + cost;
                        if cost == 0 {{
                            deque.push_front((nr, nc));
                        }} else {{
                            deque.push_back((nr, nc));
                        }}
                    }}
                }}
            }}
            dist[h - 1][w - 1]
        }}
    """,
    visible=[
        T("one_wall", 'grid = [".#.", ".#.", ".#."]', 'min_walls(&[".#.", ".#.", ".#."])', "1"),
        T("open", 'grid = ["..", ".."]', 'min_walls(&["..", ".."])', "0"),
        T("single_cell", 'grid = ["."]', 'min_walls(&["."])', "0"),
        T("two_walls_in_a_row", 'grid = [".", "#", "#", "."]', 'min_walls(&[".", "#", "#", "."])', "2"),
        T("walk_around_for_free", 'grid = ["...", "##.", "..."]', 'min_walls(&["...", "##.", "..."])', "0"),
    ],
    hidden=[
        T("wall_at_the_end_of_a_row", 'grid = ["....#"]', 'min_walls(&["....#"])', "1"),
        T("diagonal_walls", 'grid = [".##", "#.#", "##."]', 'min_walls(&[".##", "#.#", "##."])', "2"),
        T("one_wall_beats_a_dead_end", 'grid = [".#...", ".#.#.", "...##", "####."]', 'min_walls(&[".#...", ".#.#.", "...##", "####."])', "1"),
        T("alternating_row", 'grid = [".#.#.#."]', 'min_walls(&[".#.#.#."])', "3"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(919);
            for _ in 0..300 {
                let h = 1 + rng.below(5);
                let w = 1 + rng.below(5);
                let mut rows: Vec<String> = (0..h).map(|_| rng.string(w, "..#")).collect();
                rows[0].replace_range(0..1, ".");
                let grid: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
                // Brute force: relax every cell until nothing changes.
                let cost = |r: usize, c: usize| u32::from(rows[r].as_bytes()[c] == b'#');
                let mut dist = vec![vec![u32::MAX; w]; h];
                dist[0][0] = 0;
                let mut changed = true;
                while changed {
                    changed = false;
                    for r in 0..h {
                        for c in 0..w {
                            for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                                if nr < h && nc < w && dist[nr][nc] != u32::MAX && dist[nr][nc] + cost(r, c) < dist[r][c] {
                                    dist[r][c] = dist[nr][nc] + cost(r, c);
                                    changed = true;
                                }
                            }
                        }
                    }
                }
                check!(format!("grid = {rows:?}"), min_walls(&grid), dist[h - 1][w - 1]);
            }
        }
        """,
        T("walled_target", 'grid = [".#"]', 'min_walls(&[".#"])', "1"),
        T("detour_is_free", 'grid = ["..#", "##.", "..."]', 'min_walls(&["..#", "##.", "..."])', "1"),
        T("solid_rock", "500×500, all walls except the start", "min_walls(&grid)", "998",
          setup='let first = format!(".{}", "#".repeat(499));\nlet rest = "#".repeat(500);\nlet grid: Vec<&str> = (0..500).map(|i| if i == 0 { first.as_str() } else { rest.as_str() }).collect();'),
        T("maze", "499×500 snake of free corridors", "min_walls(&grid)", "0",
          setup='let rows: Vec<String> = (0..499).map(|r| if r % 2 == 0 { ".".repeat(500) } else if r % 4 == 1 { format!("{}.", "#".repeat(499)) } else { format!(".{}", "#".repeat(499)) }).collect();\nlet grid: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();'),
    ],
    wrong=dict(
        first_visit_wins="""
            use std::collections::VecDeque;

            pub fn min_walls(grid: &[&str]) -> u32 {
                let g: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
                let (h, w) = (g.len(), g[0].len());
                let mut dist = vec![vec![u32::MAX; w]; h];
                dist[0][0] = 0;
                let mut queue = VecDeque::from([(0usize, 0usize)]);
                while let Some((r, c)) = queue.pop_front() {
                    for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                        if nr < h && nc < w && dist[nr][nc] == u32::MAX {
                            dist[nr][nc] = dist[r][c] + u32::from(g[nr][nc] == b'#');
                            queue.push_back((nr, nc));
                        }
                    }
                }
                dist[h - 1][w - 1]
            }
        """,
        sweep_until_stable="""
            pub fn min_walls(grid: &[&str]) -> u32 {
                let g: Vec<&[u8]> = grid.iter().map(|r| r.as_bytes()).collect();
                let (h, w) = (g.len(), g[0].len());
                let mut dist = vec![vec![u32::MAX; w]; h];
                dist[0][0] = 0;
                let mut changed = true;
                while changed {
                    changed = false;
                    for r in 0..h {
                        for c in 0..w {
                            if dist[r][c] == u32::MAX {
                                continue;
                            }
                            for (nr, nc) in [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)] {
                                if nr < h && nc < w {
                                    let d = dist[r][c] + u32::from(g[nr][nc] == b'#');
                                    if d < dist[nr][nc] {
                                        dist[nr][nc] = d;
                                        changed = true;
                                    }
                                }
                            }
                        }
                    }
                }
                dist[h - 1][w - 1]
            }
        """,
    ),
    hints=[("approach", "Every move costs 0 or 1. Dijkstra works, but a deque does the same job in linear time."),
           ("approach", "A 0-cost move goes to the front of the deque (same distance), a 1-cost move to the back."),
           ("rust", "`u32::from(bool)` turns the wall check into the cost.")],
    notes=("The deque always holds at most two distinct distances, front ones smaller, so it behaves like Dijkstra's heap without the log factor.", "O(rows · cols)", "O(rows · cols)"),
    follow_up="How would you also return the path, not just its cost?",
))

P.append(dict(
    slug="dijkstra-over-generic-weights", title="Dijkstra over generic weights", level="hard", stage="shortest-paths",
    tags=["generics", "traits", "associated consts"], source="W42",
    teaches=["A trait bound that says exactly what Dijkstra needs: `Copy + Ord + Add`, plus a zero.", "Associated consts."],
    statement="""
        Write Dijkstra once, for any weight type that implements `Weight`. Return each node's distance from
        `src`, or `None` if it can't be reached. The hidden tests use a custom weight type of their own.
    """,
    starter="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;
        use std::ops::Add;

        /// What Dijkstra needs from a weight. Weights must never be "negative":
        /// `a + w >= a` for every weight `w`.
        pub trait Weight: Copy + Ord + Add<Output = Self> {
            const ZERO: Self;
        }

        impl Weight for u32 {
            const ZERO: u32 = 0;
        }

        impl Weight for u64 {
            const ZERO: u64 = 0;
        }

        pub fn dijkstra<W: Weight>(adj: &[Vec<(usize, W)>], src: usize) -> Vec<Option<W>> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;
        use std::ops::Add;

        /// What Dijkstra needs from a weight. Weights must never be "negative":
        /// `a + w >= a` for every weight `w`.
        pub trait Weight: Copy + Ord + Add<Output = Self> {
            const ZERO: Self;
        }

        impl Weight for u32 {
            const ZERO: u32 = 0;
        }

        impl Weight for u64 {
            const ZERO: u64 = 0;
        }

        pub fn dijkstra<W: Weight>(adj: &[Vec<(usize, W)>], src: usize) -> Vec<Option<W>> {
            let mut dist: Vec<Option<W>> = vec![None; adj.len()];
            dist[src] = Some(W::ZERO);
            let mut heap = BinaryHeap::from([Reverse((W::ZERO, src))]);
            while let Some(Reverse((d, u))) = heap.pop() {
                if dist[u].is_some_and(|best| d > best) {
                    continue;
                }
                for &(v, w) in &adj[u] {
                    let next = d + w;
                    if dist[v].is_none_or(|best| next < best) {
                        dist[v] = Some(next);
                        heap.push(Reverse((next, v)));
                    }
                }
            }
            dist
        }
    """,
    visible=[
        T("u32", "adj = [[(1,4), (2,1)], [(3,1)], [(1,2), (3,5)], []] as u32, src = 0",
          "dijkstra(&[vec![(1, 4u32), (2, 1)], vec![(3, 1)], vec![(1, 2), (3, 5)], vec![]], 0)", "vec![Some(0), Some(3), Some(1), Some(4)]"),
        T("unreachable_u64", "adj = [[(1,10)], [], []] as u64, src = 0", "dijkstra(&[vec![(1, 10u64)], vec![], vec![]], 0)", "vec![Some(0), Some(10), None]"),
        T("single_node", "adj = [[]] as u32, src = 0", "dijkstra::<u32>(&[vec![]], 0)", "vec![Some(0)]"),
        T("parallel_edges_take_the_cheaper", "adj = [[(1,5), (1,2)], []] as u32, src = 0", "dijkstra(&[vec![(1, 5u32), (1, 2)], vec![]], 0)", "vec![Some(0), Some(2)]"),
        T("edges_are_directed", "adj = [[], [(0,1)]] as u32, src = 0", "dijkstra(&[vec![], vec![(0, 1u32)]], 0)", "vec![Some(0), None]"),
    ],
    hidden=[
        """
        #[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
        struct Cost {
            money: u32,
            hops: u32,
        }

        impl std::ops::Add for Cost {
            type Output = Cost;
            fn add(self, o: Cost) -> Cost {
                Cost { money: self.money + o.money, hops: self.hops + o.hops }
            }
        }

        impl Weight for Cost {
            const ZERO: Cost = Cost { money: 0, hops: 0 };
        }

        fn c(money: u32) -> Cost {
            Cost { money, hops: 1 }
        }
        """,
        T("custom_weight_breaks_ties_on_hops", "Cost = (money, hops); 0→2 costs 5 directly or 2+3 via 1",
          "dijkstra(&[vec![(1, c(2)), (2, c(5))], vec![(2, c(3))], vec![]], 0)[2]", "Some(Cost { money: 5, hops: 1 })"),
        T("start_elsewhere", "adj = [[], [(0,7)]] as u32, src = 1", "dijkstra(&[vec![], vec![(0, 7u32)]], 1)", "vec![Some(7), Some(0)]"),
        T("zero_weights", "adj = [[(1,0)], [(2,0)], [(0,0)]] as u32, src = 0", "dijkstra(&[vec![(1, 0u32)], vec![(2, 0)], vec![(0, 0)]], 0)", "vec![Some(0), Some(0), Some(0)]"),
        T("big_u64_weights", "adj = [[(1,10¹²)], [(2,10¹²)], []] as u64, src = 0", "dijkstra(&[vec![(1, 1_000_000_000_000u64)], vec![(2, 1_000_000_000_000)], vec![]], 0)[2]", "Some(2_000_000_000_000)"),
        T("later_cheaper_path_wins", "0→3 costs 100 directly, 0→1→2→3 costs 1 each; found in that order",
          "dijkstra(&[vec![(3, 100u32), (1, 1)], vec![(2, 1)], vec![(3, 1)], vec![]], 0)", "vec![Some(0), Some(1), Some(2), Some(3)]"),
        T("cycle_back_to_source", "adj = [[(1,4)], [(0,1), (2,4)], []] as u32, src = 0", "dijkstra(&[vec![(1, 4u32)], vec![(0, 1), (2, 4)], vec![]], 0)", "vec![Some(0), Some(4), Some(8)]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(920);
            for _ in 0..300 {
                let n = 1 + rng.below(7);
                let adj: Vec<Vec<(usize, u64)>> = (0..n).map(|_| { let k = rng.below(4); (0..k).map(|_| (rng.below(n), rng.int(0, 20) as u64)).collect() }).collect();
                let src = rng.below(n);
                // Brute force: Bellman-Ford.
                let mut want: Vec<Option<u64>> = vec![None; n];
                want[src] = Some(0);
                for _ in 0..n {
                    for u in 0..n {
                        if let Some(du) = want[u] {
                            for &(v, w) in &adj[u] {
                                if want[v].map_or(true, |dv| du + w < dv) {
                                    want[v] = Some(du + w);
                                }
                            }
                        }
                    }
                }
                check!(format!("adj = {adj:?}, src = {src}"), dijkstra(&adj, src), want);
            }
        }

        #[test]
        fn scale_100k() {
            // i → i + 1 costs 1000, i → i + 2 costs 1999, and every node has a costly edge back to 0.
            let n = 100_000;
            let adj: Vec<Vec<(usize, u64)>> = (0..n).map(|i| {
                let mut out = vec![(0, 5)];
                if i + 1 < n { out.push((i + 1, 1000)); }
                if i + 2 < n { out.push((i + 2, 1999)); }
                out
            }).collect();
            let d = dijkstra(&adj, 0);
            check!("n = 100000, i → i+1 (1000), i → i+2 (1999)", (d[1], d[2], d[n - 1]), (Some(1000), Some(1999), Some(99_949_001)));
        }
        """,
    ],
    wrong=dict(
        scan_for_the_closest="""
            use std::ops::Add;

            /// What Dijkstra needs from a weight. Weights must never be "negative":
            /// `a + w >= a` for every weight `w`.
            pub trait Weight: Copy + Ord + Add<Output = Self> {
                const ZERO: Self;
            }

            impl Weight for u32 {
                const ZERO: u32 = 0;
            }

            impl Weight for u64 {
                const ZERO: u64 = 0;
            }

            pub fn dijkstra<W: Weight>(adj: &[Vec<(usize, W)>], src: usize) -> Vec<Option<W>> {
                let n = adj.len();
                let mut dist: Vec<Option<W>> = vec![None; n];
                let mut done = vec![false; n];
                dist[src] = Some(W::ZERO);
                loop {
                    let mut pick: Option<(W, usize)> = None;
                    for u in 0..n {
                        if let (false, Some(d)) = (done[u], dist[u]) {
                            if pick.map_or(true, |(best, _)| d < best) {
                                pick = Some((d, u));
                            }
                        }
                    }
                    let Some((d, u)) = pick else { break };
                    done[u] = true;
                    for &(v, w) in &adj[u] {
                        if dist[v].is_none_or(|best| d + w < best) {
                            dist[v] = Some(d + w);
                        }
                    }
                }
                dist
            }
        """,
        first_distance_is_final="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;
            use std::ops::Add;

            /// What Dijkstra needs from a weight. Weights must never be "negative":
            /// `a + w >= a` for every weight `w`.
            pub trait Weight: Copy + Ord + Add<Output = Self> {
                const ZERO: Self;
            }

            impl Weight for u32 {
                const ZERO: u32 = 0;
            }

            impl Weight for u64 {
                const ZERO: u64 = 0;
            }

            pub fn dijkstra<W: Weight>(adj: &[Vec<(usize, W)>], src: usize) -> Vec<Option<W>> {
                let mut dist: Vec<Option<W>> = vec![None; adj.len()];
                dist[src] = Some(W::ZERO);
                let mut heap = BinaryHeap::from([Reverse((W::ZERO, src))]);
                while let Some(Reverse((d, u))) = heap.pop() {
                    for &(v, w) in &adj[u] {
                        if dist[v].is_none() {
                            dist[v] = Some(d + w);
                            heap.push(Reverse((d + w, v)));
                        }
                    }
                }
                dist
            }
        """,
    ),
    hints=[("rust", "Store `Option<W>` per node: `None` means unreached, so no `MAX` sentinel is needed. That's why `Weight` doesn't ask for one."),
           ("rust", "`Reverse((W, usize))` works for any `W: Ord`; `Option::is_none_or` reads well for the relaxation check.")],
    notes=("The bound lists exactly what the algorithm uses: `Copy` to move weights around, `Ord` for the heap, `Add` to extend paths, `ZERO` for the source. With `Option` for 'unreached', any such type works, including a lexicographic (money, hops) cost.", "O(E log E)", "O(V + E)"),
    follow_up="How would you support weights that can be compared but not totally ordered, like `f64`?",
    related=["L4", "S1"],
))

# ---------------------------------------------------------------- union-find & MST

UF_ROOT = """
    fn root(parent: &mut [usize], mut x: usize) -> usize {
        while parent[x] != x {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        x
    }
"""

P.append(dict(
    slug="redundant-connection", title="Redundant connection", level="medium", stage="union-find-mst",
    tags=["union-find"],
    teaches=["Union-find in a `Vec<usize>`.", "Path halving in a loop, no recursion."],
    statement="""
        A tree with nodes `1..=n` had one extra edge added, giving `n` edges in all. Return the edge that can
        be removed to leave a tree; if several can, the one that appears last in `edges`.
    """,
    examples=[("edges = [(1,2), (1,3), (2,3)]", "Some((2, 3))")],
    constraints=["2 ≤ n ≤ 2·10⁵"],
    starter="""
        pub fn find_redundant(edges: &[(usize, usize)]) -> Option<(usize, usize)> {
            todo!()
        }
    """,
    solution="""
        pub fn find_redundant(edges: &[(usize, usize)]) -> Option<(usize, usize)> {
            fn root(parent: &mut [usize], mut x: usize) -> usize {
                while parent[x] != x {
                    parent[x] = parent[parent[x]];
                    x = parent[x];
                }
                x
            }

            let mut parent: Vec<usize> = (0..=edges.len()).collect();
            for &(a, b) in edges {
                let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
                if ra == rb {
                    return Some((a, b));
                }
                parent[ra] = rb;
            }
            None
        }
    """,
    visible=[
        T("triangle", "edges = [(1,2), (1,3), (2,3)]", "find_redundant(&[(1, 2), (1, 3), (2, 3)])", "Some((2, 3))"),
        T("longer_cycle", "edges = [(1,2), (2,3), (3,4), (1,4), (1,5)]", "find_redundant(&[(1, 2), (2, 3), (3, 4), (1, 4), (1, 5)])", "Some((1, 4))"),
        T("repeated_edge", "edges = [(1,2), (1,2)]", "find_redundant(&[(1, 2), (1, 2)])", "Some((1, 2))"),
        T("answer_is_not_the_last_edge", "edges = [(1,2), (2,3), (3,1), (1,4)]", "find_redundant(&[(1, 2), (2, 3), (3, 1), (1, 4)])", "Some((3, 1))"),
        T("pair_returned_as_given", "edges = [(3,1), (2,3), (1,2)]", "find_redundant(&[(3, 1), (2, 3), (1, 2)])", "Some((1, 2))"),
    ],
    hidden=[
        T("reversed_pairs", "edges = [(2,1), (3,1), (4,2), (1,4)]", "find_redundant(&[(2, 1), (3, 1), (4, 2), (1, 4)])", "Some((1, 4))"),
        T("double_edge", "edges = [(1,2), (2,1)]", "find_redundant(&[(1, 2), (2, 1)])", "Some((2, 1))"),
        T("cycle_after_a_tail", "edges = [(1,5), (1,2), (2,3), (3,4), (4,2)]", "find_redundant(&[(1, 5), (1, 2), (2, 3), (3, 4), (4, 2)])", "Some((4, 2))"),
        T("every_edge_on_the_cycle", "edges = [(3,4), (1,2), (2,4), (3,1)]", "find_redundant(&[(3, 4), (1, 2), (2, 4), (3, 1)])", "Some((3, 1))"),
        T("ring_1000", "ring 1-2-…-1000-1", "find_redundant(&edges)", "Some((1000, 1))",
          setup="let edges: Vec<(usize, usize)> = (1..=1000).map(|i| (i, i % 1000 + 1)).collect();"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(921);
            for _ in 0..300 {
                let n = 2 + rng.below(7);
                let mut label: Vec<usize> = (1..=n).collect();
                rng.shuffle(&mut label);
                let mut edges: Vec<(usize, usize)> = (1..n).map(|i| { let j = rng.below(i); if rng.bool() { (label[i], label[j]) } else { (label[j], label[i]) } }).collect();
                let a = rng.below(n);
                let b = (a + 1 + rng.below(n - 1)) % n;
                edges.push((label[a], label[b]));
                rng.shuffle(&mut edges);
                // Brute force: the last edge whose removal leaves every node connected.
                let connected_without = |skip: usize| {
                    let mut seen = vec![false; n + 1];
                    seen[1] = true;
                    let mut stack = vec![1];
                    while let Some(u) = stack.pop() {
                        for (i, &(x, y)) in edges.iter().enumerate() {
                            if i != skip && (x == u || y == u) {
                                let v = if x == u { y } else { x };
                                if !seen[v] {
                                    seen[v] = true;
                                    stack.push(v);
                                }
                            }
                        }
                    }
                    seen[1..].iter().all(|&s| s)
                };
                let want = (0..edges.len()).rev().find(|&i| connected_without(i)).map(|i| edges[i]);
                check!(format!("edges = {edges:?}"), find_redundant(&edges), want);
            }
        }

        #[test]
        fn scale_star_200k() {
            // 1 joined to every other node, then (2, 3) closes a triangle.
            let n = 200_000;
            let mut edges: Vec<(usize, usize)> = (2..=n).map(|i| (1, i)).collect();
            edges.push((2, 3));
            check!("n = 200000: (1, i) for every i, then (2, 3)", find_redundant(&edges), Some((2, 3)));
        }

        #[test]
        fn scale_cycle_first() {
            // The triangle 1-2-3 comes first; 99997 tree edges follow it.
            let n = 100_000;
            let mut edges = vec![(1, 2), (2, 3), (3, 1)];
            edges.extend((4..=n).map(|i| (i - 1, i)));
            check!("n = 100000: (1,2), (2,3), (3,1), then a path 3-4-…-100000", find_redundant(&edges), Some((3, 1)));
        }
        """,
    ],
    wrong=dict(
        no_path_compression="""
            pub fn find_redundant(edges: &[(usize, usize)]) -> Option<(usize, usize)> {
                fn root(parent: &[usize], mut x: usize) -> usize {
                    while parent[x] != x {
                        x = parent[x];
                    }
                    x
                }

                let mut parent: Vec<usize> = (0..=edges.len()).collect();
                for &(a, b) in edges {
                    let (ra, rb) = (root(&parent, a), root(&parent, b));
                    if ra == rb {
                        return Some((a, b));
                    }
                    parent[ra] = rb;
                }
                None
            }
        """,
        sorted_pair="""
            pub fn find_redundant(edges: &[(usize, usize)]) -> Option<(usize, usize)> {
                fn root(parent: &mut [usize], mut x: usize) -> usize {
                    while parent[x] != x {
                        parent[x] = parent[parent[x]];
                        x = parent[x];
                    }
                    x
                }

                let mut parent: Vec<usize> = (0..=edges.len()).collect();
                for &(a, b) in edges {
                    let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
                    if ra == rb {
                        return Some((a.min(b), a.max(b)));
                    }
                    parent[ra] = rb;
                }
                None
            }
        """,
        remove_each_edge_and_check="""
            pub fn find_redundant(edges: &[(usize, usize)]) -> Option<(usize, usize)> {
                let n = edges.len();
                let mut adj = vec![Vec::new(); n + 1];
                for (i, &(a, b)) in edges.iter().enumerate() {
                    adj[a].push((b, i));
                    adj[b].push((a, i));
                }
                for skip in (0..n).rev() {
                    let mut seen = vec![false; n + 1];
                    seen[1] = true;
                    let mut stack = vec![1];
                    let mut count = 1;
                    while let Some(u) = stack.pop() {
                        for &(v, i) in &adj[u] {
                            if i != skip && !seen[v] {
                                seen[v] = true;
                                count += 1;
                                stack.push(v);
                            }
                        }
                    }
                    if count == n {
                        return Some(edges[skip]);
                    }
                }
                None
            }
        """,
    ),
    hints=[("approach", "Add edges one by one. The first edge whose ends are already connected closes the cycle, and it's the last cycle edge in the list."),
           ("rust", "`parent: Vec<usize>` where `parent[x] == x` marks a root. `(0..=n).collect()` initialises it.")],
    notes=("Every cycle edge could be removed; the one that closes the cycle comes last among them. Path halving keeps trees shallow without recursion.", "O(n α(n))", "O(n)"),
    follow_up="How does the problem change if the graph is directed (a rooted tree plus one edge)?",
))

P.append(dict(
    slug="graph-valid-tree", title="Graph valid tree", level="medium", stage="union-find-mst",
    tags=["union-find", "Blind 75"],
    teaches=["A tree is connected with exactly n − 1 edges.", "Early return on the first cycle."],
    statement="Return whether the undirected graph on nodes `0..n` is a tree: connected, with no cycles.",
    examples=[("n = 5, edges = [(0,1), (0,2), (0,3), (1,4)]", "true"), ("n = 5, edges = [(0,1), (1,2), (2,3), (1,3), (1,4)]", "false")],
    constraints=["1 ≤ n ≤ 2·10⁵"],
    starter="""
        pub fn valid_tree(n: usize, edges: &[(usize, usize)]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn valid_tree(n: usize, edges: &[(usize, usize)]) -> bool {
            fn root(parent: &mut [usize], mut x: usize) -> usize {
                while parent[x] != x {
                    parent[x] = parent[parent[x]];
                    x = parent[x];
                }
                x
            }

            if edges.len() + 1 != n {
                return false;
            }
            let mut parent: Vec<usize> = (0..n).collect();
            for &(a, b) in edges {
                let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
                if ra == rb {
                    return false;
                }
                parent[ra] = rb;
            }
            true
        }
    """,
    visible=[
        T("tree", "n = 5, edges = [(0,1), (0,2), (0,3), (1,4)]", "valid_tree(5, &[(0, 1), (0, 2), (0, 3), (1, 4)])", "true"),
        T("cycle", "n = 5, edges = [(0,1), (1,2), (2,3), (1,3), (1,4)]", "valid_tree(5, &[(0, 1), (1, 2), (2, 3), (1, 3), (1, 4)])", "false"),
        T("single_edge", "n = 2, edges = [(0,1)]", "valid_tree(2, &[(0, 1)])", "true"),
        T("not_connected", "n = 2, edges = []", "valid_tree(2, &[])", "false"),
        T("triangle", "n = 3, edges = [(0,1), (1,2), (2,0)]", "valid_tree(3, &[(0, 1), (1, 2), (2, 0)])", "false"),
    ],
    hidden=[
        T("single", "n = 1, edges = []", "valid_tree(1, &[])", "true"),
        T("forest", "n = 4, edges = [(0,1), (2,3)]", "valid_tree(4, &[(0, 1), (2, 3)])", "false"),
        T("right_count_but_cycle", "n = 4, edges = [(0,1), (1,0), (2,3)]", "valid_tree(4, &[(0, 1), (1, 0), (2, 3)])", "false"),
        T("self_loop", "n = 1, edges = [(0,0)]", "valid_tree(1, &[(0, 0)])", "false"),
        T("self_loop_with_right_count", "n = 2, edges = [(0,0)]", "valid_tree(2, &[(0, 0)])", "false"),
        T("path_listed_backwards", "n = 4, edges = [(3,2), (2,1), (1,0)]", "valid_tree(4, &[(3, 2), (2, 1), (1, 0)])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(922);
            for _ in 0..300 {
                let n = 1 + rng.below(7);
                let m = if rng.bool() { n - 1 } else { rng.below(n + 1) };
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                // Brute force: n - 1 edges, and a search from 0 reaches every node.
                let mut seen = vec![false; n];
                seen[0] = true;
                let mut stack = vec![0];
                while let Some(u) = stack.pop() {
                    for &(a, b) in &edges {
                        for (x, y) in [(a, b), (b, a)] {
                            if x == u && !seen[y] {
                                seen[y] = true;
                                stack.push(y);
                            }
                        }
                    }
                }
                let want = m + 1 == n && seen.iter().all(|&s| s);
                check!(format!("n = {n}, edges = {edges:?}"), valid_tree(n, &edges), want);
            }
        }

        #[test]
        fn scale_star_200k() {
            let n = 200_000;
            let edges: Vec<(usize, usize)> = (1..n).map(|i| (0, i)).collect();
            check!("n = 200000, 0 joined to every other node", valid_tree(n, &edges), true);
        }

        #[test]
        fn scale_star_plus_one_cycle() {
            let n = 200_000;
            let mut edges: Vec<(usize, usize)> = (1..n - 1).map(|i| (0, i)).collect();
            edges.push((n - 2, 1));
            check!("n = 200000, star missing node 199999, plus (199998, 1)", valid_tree(n, &edges), false);
        }
        """,
    ],
    wrong=dict(
        count_only="""
            pub fn valid_tree(n: usize, edges: &[(usize, usize)]) -> bool {
                edges.len() + 1 == n
            }
        """,
        acyclic_only="""
            pub fn valid_tree(n: usize, edges: &[(usize, usize)]) -> bool {
                fn root(parent: &mut [usize], mut x: usize) -> usize {
                    while parent[x] != x {
                        parent[x] = parent[parent[x]];
                        x = parent[x];
                    }
                    x
                }

                let mut parent: Vec<usize> = (0..n).collect();
                for &(a, b) in edges {
                    let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
                    if ra == rb {
                        return false;
                    }
                    parent[ra] = rb;
                }
                true
            }
        """,
        no_path_compression="""
            pub fn valid_tree(n: usize, edges: &[(usize, usize)]) -> bool {
                fn root(parent: &[usize], mut x: usize) -> usize {
                    while parent[x] != x {
                        x = parent[x];
                    }
                    x
                }

                if edges.len() + 1 != n {
                    return false;
                }
                let mut parent: Vec<usize> = (0..n).collect();
                for &(a, b) in edges {
                    let (ra, rb) = (root(&parent, a), root(&parent, b));
                    if ra == rb {
                        return false;
                    }
                    parent[ra] = rb;
                }
                true
            }
        """,
    ),
    hints=[("approach", "A tree on n nodes has exactly n − 1 edges. With that many edges, no cycle implies connected."),
           ("edge case", "A repeated edge is a cycle of length 2.")],
    notes=("Checking the edge count first means only cycles need detecting: n − 1 acyclic edges always connect n nodes.", "O(n α(n))", "O(n)"),
    follow_up="Solve it with BFS instead. What does each approach need to remember?",
))

P.append(dict(
    slug="number-of-connected-components", title="Number of connected components", level="medium", stage="union-find-mst",
    tags=["union-find", "Blind 75"],
    teaches=["Counting sets by counting successful unions."],
    statement="Return the number of connected components in the undirected graph on nodes `0..n`.",
    examples=[("n = 5, edges = [(0,1), (1,2), (3,4)]", "2")],
    constraints=["1 ≤ n ≤ 10⁶"],
    starter="""
        pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
            fn root(parent: &mut [usize], mut x: usize) -> usize {
                while parent[x] != x {
                    parent[x] = parent[parent[x]];
                    x = parent[x];
                }
                x
            }

            let mut parent: Vec<usize> = (0..n).collect();
            let mut components = n;
            for &(a, b) in edges {
                let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
                if ra != rb {
                    parent[ra] = rb;
                    components -= 1;
                }
            }
            components
        }
    """,
    visible=[
        T("two", "n = 5, edges = [(0,1), (1,2), (3,4)]", "count_components(5, &[(0, 1), (1, 2), (3, 4)])", "2"),
        T("one", "n = 5, edges = [(0,1), (1,2), (2,3), (3,4)]", "count_components(5, &[(0, 1), (1, 2), (2, 3), (3, 4)])", "1"),
        T("single_node", "n = 1, edges = []", "count_components(1, &[])", "1"),
        T("no_edges", "n = 4, edges = []", "count_components(4, &[])", "4"),
        T("repeated_and_cyclic_edges", "n = 4, edges = [(0,1), (1,0), (1,2), (2,0)]", "count_components(4, &[(0, 1), (1, 0), (1, 2), (2, 0)])", "2"),
    ],
    hidden=[
        T("pairs_joined_later", "n = 6, edges = [(0,1), (2,3), (4,5), (1,2)]", "count_components(6, &[(0, 1), (2, 3), (4, 5), (1, 2)])", "2"),
        T("self_loop", "n = 3, edges = [(0,0), (1,2), (2,1)]", "count_components(3, &[(0, 0), (1, 2), (2, 1)])", "2"),
        T("star", "n = 6, edges = [(0,1), (0,2), (0,3), (0,4), (0,5)]", "count_components(6, &[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)])", "1"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(923);
            for _ in 0..300 {
                let n = 1 + rng.below(8);
                let m = rng.below(10);
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                // Brute force: label propagation.
                let mut label: Vec<usize> = (0..n).collect();
                loop {
                    let mut changed = false;
                    for &(a, b) in &edges {
                        let low = label[a].min(label[b]);
                        if label[a] != low || label[b] != low {
                            label[a] = low;
                            label[b] = low;
                            changed = true;
                        }
                    }
                    if !changed {
                        break;
                    }
                }
                let want = (0..n).filter(|&u| label[u] == u).count();
                check!(format!("n = {n}, edges = {edges:?}"), count_components(n, &edges), want);
            }
        }

        #[test]
        fn scale_star_200k() {
            let n = 200_000;
            let edges: Vec<(usize, usize)> = (1..n).map(|i| (0, i)).collect();
            check!("n = 200000, 0 joined to every other node", count_components(n, &edges), 1);
        }
        """,
        T("isolated", "n = 3, edges = []", "count_components(3, &[])", "3"),
        T("million", "n = 10⁶, edges pair up neighbours (0-1, 2-3, …)", "count_components(1_000_000, &edges)", "500_000",
          setup="let edges: Vec<(usize, usize)> = (0..500_000).map(|i| (2 * i, 2 * i + 1)).collect();"),
        T("long_chain", "n = 10⁶, chain", "count_components(1_000_000, &edges)", "1",
          setup="let edges: Vec<(usize, usize)> = (1..1_000_000).map(|i| (i, i - 1)).collect();"),
    ],
    wrong=dict(
        nodes_minus_edges="""
            pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
                n.saturating_sub(edges.len()).max(1)
            }
        """,
        no_path_compression="""
            pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
                fn root(parent: &[usize], mut x: usize) -> usize {
                    while parent[x] != x {
                        x = parent[x];
                    }
                    x
                }

                let mut parent: Vec<usize> = (0..n).collect();
                let mut components = n;
                for &(a, b) in edges {
                    let (ra, rb) = (root(&parent, a), root(&parent, b));
                    if ra != rb {
                        parent[ra] = rb;
                        components -= 1;
                    }
                }
                components
            }
        """,
        recursive_dfs="""
            pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
                fn visit(u: usize, adj: &[Vec<usize>], seen: &mut [bool]) {
                    seen[u] = true;
                    for &v in &adj[u] {
                        if !seen[v] {
                            visit(v, adj, seen);
                        }
                    }
                }
                let mut adj = vec![Vec::new(); n];
                for &(a, b) in edges {
                    adj[a].push(b);
                    adj[b].push(a);
                }
                let mut seen = vec![false; n];
                let mut count = 0;
                for u in 0..n {
                    if !seen[u] {
                        count += 1;
                        visit(u, &adj, &mut seen);
                    }
                }
                count
            }
        """,
    ),
    hints=[("approach", "Start with n components. Each union of two different sets removes one.")],
    notes=("A successful union always merges two components into one, so the count falls by exactly one per merge.", "O((n + E) α(n))", "O(n)"),
    follow_up="Edges arrive as a stream and you must report the count after each. Does anything change?",
))

P.append(dict(
    slug="kruskals-mst", title="Kruskal's MST", level="medium", stage="union-find-mst",
    tags=["MST", "sort_unstable_by_key"],
    teaches=["Sort edges, keep those that join two components.", "`Option` for 'no spanning tree'."],
    statement="""
        Return the total weight of a minimum spanning tree of the undirected graph on nodes `0..n`, or `None`
        if the graph isn't connected.
    """,
    examples=[("n = 4, edges = [(0,1,1), (1,2,2), (0,2,3), (2,3,4), (1,3,5)]", "Some(7)")],
    constraints=["1 ≤ n ≤ 10⁵", "edges.len() ≤ 2·10⁵", "weights ≤ 10¹²"],
    starter="""
        pub fn mst_weight(n: usize, edges: &[(usize, usize, u64)]) -> Option<u64> {
            todo!()
        }
    """,
    solution="""
        pub fn mst_weight(n: usize, edges: &[(usize, usize, u64)]) -> Option<u64> {
            fn root(parent: &mut [usize], mut x: usize) -> usize {
                while parent[x] != x {
                    parent[x] = parent[parent[x]];
                    x = parent[x];
                }
                x
            }

            let mut sorted = edges.to_vec();
            sorted.sort_unstable_by_key(|&(_, _, w)| w);
            let mut parent: Vec<usize> = (0..n).collect();
            let (mut total, mut used) = (0, 0);
            for (a, b, w) in sorted {
                let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
                if ra != rb {
                    parent[ra] = rb;
                    total += w;
                    used += 1;
                }
            }
            (used + 1 == n).then_some(total)
        }
    """,
    visible=[
        T("seven", "n = 4, edges = [(0,1,1), (1,2,2), (0,2,3), (2,3,4), (1,3,5)]", "mst_weight(4, &[(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4), (1, 3, 5)])", "Some(7)"),
        T("disconnected", "n = 3, edges = [(0,1,1)]", "mst_weight(3, &[(0, 1, 1)])", "None"),
        T("skip_the_heaviest_triangle_edge", "n = 3, edges = [(0,1,5), (1,2,1), (0,2,2)]", "mst_weight(3, &[(0, 1, 5), (1, 2, 1), (0, 2, 2)])", "Some(3)"),
        T("self_loop_ignored", "n = 2, edges = [(0,0,1), (0,1,7)]", "mst_weight(2, &[(0, 0, 1), (0, 1, 7)])", "Some(7)"),
        T("equal_weights", "n = 3, edges = [(0,1,2), (1,2,2), (0,2,2)]", "mst_weight(3, &[(0, 1, 2), (1, 2, 2), (0, 2, 2)])", "Some(4)"),
    ],
    hidden=[
        T("single", "n = 1, edges = []", "mst_weight(1, &[])", "Some(0)"),
        T("parallel_edges", "n = 2, edges = [(0,1,9), (1,0,4)]", "mst_weight(2, &[(0, 1, 9), (1, 0, 4)])", "Some(4)"),
        T("big_weights", "n = 3, edges with weight 10¹²", "mst_weight(3, &[(0, 1, 1_000_000_000_000), (1, 2, 1_000_000_000_000)])", "Some(2_000_000_000_000)"),
        T("zero_weights", "n = 3, edges = [(0,1,0), (1,2,0), (0,2,0)]", "mst_weight(3, &[(0, 1, 0), (1, 2, 0), (0, 2, 0)])", "Some(0)"),
        T("two_islands", "n = 4, edges = [(0,1,1), (2,3,1), (0,1,2)]", "mst_weight(4, &[(0, 1, 1), (2, 3, 1), (0, 1, 2)])", "None"),
        T("cheap_edges_listed_last", "n = 4, edges = [(0,1,10), (1,2,10), (2,3,10), (0,3,1), (0,2,1), (1,3,1)]",
          "mst_weight(4, &[(0, 1, 10), (1, 2, 10), (2, 3, 10), (0, 3, 1), (0, 2, 1), (1, 3, 1)])", "Some(3)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(924);
            for _ in 0..300 {
                let n = 1 + rng.below(7);
                let m = rng.below(12);
                let edges: Vec<(usize, usize, u64)> = (0..m).map(|_| (rng.below(n), rng.below(n), rng.int(0, 20) as u64)).collect();
                // Brute force: Prim's algorithm on a weight matrix.
                let mut w = vec![vec![u64::MAX; n]; n];
                for &(a, b, c) in &edges {
                    if a != b {
                        w[a][b] = w[a][b].min(c);
                        w[b][a] = w[b][a].min(c);
                    }
                }
                let mut inside = vec![false; n];
                inside[0] = true;
                let mut total = 0;
                let mut want = Some(0);
                for _ in 1..n {
                    let best = (0..n).filter(|&u| inside[u]).flat_map(|u| (0..n).filter(|&v| !inside[v]).map(move |v| (u, v))).min_by_key(|&(u, v)| w[u][v]);
                    match best {
                        Some((u, v)) if w[u][v] != u64::MAX => {
                            inside[v] = true;
                            total += w[u][v];
                            want = Some(total);
                        }
                        _ => {
                            want = None;
                            break;
                        }
                    }
                }
                check!(format!("n = {n}, edges = {edges:?}"), mst_weight(n, &edges), want);
            }
        }

        #[test]
        fn scale_100k_nodes() {
            // A random spanning tree plus 100000 random extra edges, weights below 10⁶ (LCG seed 7).
            let n = 100_000;
            let mut x: u64 = 7;
            let mut next = || { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); x >> 33 };
            let mut edges: Vec<(usize, usize, u64)> = Vec::new();
            for i in 1..n {
                let j = (next() % i as u64) as usize;
                let w = next() % 1_000_000;
                edges.push((i, j, w));
            }
            for _ in 0..100_000 {
                let a = (next() % n as u64) as usize;
                let b = (next() % n as u64) as usize;
                let w = next() % 1_000_000;
                edges.push((a, b, w));
            }
            check!("n = 100000, 199999 pseudo-random edges", mst_weight(n, &edges), Some(28_601_926_593));
        }
        """,
    ],
    wrong=dict(
        input_order="""
            pub fn mst_weight(n: usize, edges: &[(usize, usize, u64)]) -> Option<u64> {
                fn root(parent: &mut [usize], mut x: usize) -> usize {
                    while parent[x] != x {
                        parent[x] = parent[parent[x]];
                        x = parent[x];
                    }
                    x
                }

                let mut parent: Vec<usize> = (0..n).collect();
                let (mut total, mut used) = (0, 0);
                for &(a, b, w) in edges {
                    let (ra, rb) = (root(&mut parent, a), root(&mut parent, b));
                    if ra != rb {
                        parent[ra] = rb;
                        total += w;
                        used += 1;
                    }
                }
                (used + 1 == n).then_some(total)
            }
        """,
        prim_on_a_matrix="""
            pub fn mst_weight(n: usize, edges: &[(usize, usize, u64)]) -> Option<u64> {
                let mut adj = vec![Vec::new(); n];
                for &(a, b, w) in edges {
                    adj[a].push((b, w));
                    adj[b].push((a, w));
                }
                let mut best = vec![u64::MAX; n];
                let mut inside = vec![false; n];
                best[0] = 0;
                let mut total = 0;
                for _ in 0..n {
                    let u = (0..n).filter(|&u| !inside[u]).min_by_key(|&u| best[u])?;
                    if best[u] == u64::MAX {
                        return None;
                    }
                    inside[u] = true;
                    total += best[u];
                    for &(v, w) in &adj[u] {
                        if !inside[v] && w < best[v] {
                            best[v] = w;
                        }
                    }
                }
                Some(total)
            }
        """,
    ),
    hints=[("approach", "Take edges cheapest first; keep one only if it joins two different components."),
           ("rust", "`edges.to_vec()` then `sort_unstable_by_key(|&(_, _, w)| w)`; the input stays untouched.")],
    notes=("The cut property makes the greedy choice safe. A spanning tree has exactly n − 1 edges, so counting merges also detects a disconnected graph.", "O(E log E)", "O(E + n)"),
    follow_up="When is Prim's algorithm a better choice than Kruskal's?",
    related=["D8"],
))

P.append(dict(
    slug="union-find-as-a-reusable-struct", title="Union-find as a reusable struct", level="medium", stage="union-find-mst",
    tags=["union by size", "API design"], source="W20",
    teaches=["Why `find` takes `&mut self` (path compression writes).", "Union by size plus path compression."],
    statement="""
        Implement a disjoint-set union over `0..n` with union by size and path compression. `union` returns
        whether it merged two different sets. The hidden tests use 10⁶ elements.
    """,
    starter="""
        pub struct UnionFind {
            parent: Vec<usize>,
            size: Vec<usize>,
            sets: usize,
        }

        impl UnionFind {
            pub fn new(n: usize) -> Self {
                todo!()
            }

            pub fn find(&mut self, x: usize) -> usize {
                todo!()
            }

            pub fn union(&mut self, a: usize, b: usize) -> bool {
                todo!()
            }

            pub fn connected(&mut self, a: usize, b: usize) -> bool {
                todo!()
            }

            pub fn set_size(&mut self, x: usize) -> usize {
                todo!()
            }

            pub fn set_count(&self) -> usize {
                todo!()
            }
        }
    """,
    solution="""
        pub struct UnionFind {
            parent: Vec<usize>,
            size: Vec<usize>,
            sets: usize,
        }

        impl UnionFind {
            pub fn new(n: usize) -> Self {
                UnionFind { parent: (0..n).collect(), size: vec![1; n], sets: n }
            }

            pub fn find(&mut self, x: usize) -> usize {
                let mut root = x;
                while self.parent[root] != root {
                    root = self.parent[root];
                }
                let mut x = x;
                while self.parent[x] != root {
                    let next = self.parent[x];
                    self.parent[x] = root;
                    x = next;
                }
                root
            }

            pub fn union(&mut self, a: usize, b: usize) -> bool {
                let (mut ra, mut rb) = (self.find(a), self.find(b));
                if ra == rb {
                    return false;
                }
                if self.size[ra] < self.size[rb] {
                    std::mem::swap(&mut ra, &mut rb);
                }
                self.parent[rb] = ra;
                self.size[ra] += self.size[rb];
                self.sets -= 1;
                true
            }

            pub fn connected(&mut self, a: usize, b: usize) -> bool {
                self.find(a) == self.find(b)
            }

            pub fn set_size(&mut self, x: usize) -> usize {
                let r = self.find(x);
                self.size[r]
            }

            pub fn set_count(&self) -> usize {
                self.sets
            }
        }
    """,
    visible=[
        T("merges", "n = 5; union(0,1), union(1,2), union(0,2)", "(first, again, uf.connected(0, 2), uf.connected(0, 3), uf.set_count(), uf.set_size(2))", "(true, false, true, false, 3, 3)",
          setup="let mut uf = UnionFind::new(5);\nlet first = uf.union(0, 1);\nuf.union(1, 2);\nlet again = uf.union(0, 2);"),
        T("fresh", "n = 3", "(uf.set_count(), uf.set_size(1), uf.find(2))", "(3, 1, 2)", setup="let mut uf = UnionFind::new(3);"),
        T("pairs_then_join", "n = 5; union(0,1), union(2,3), union(1,3)", "(uf.set_size(0), uf.set_count(), uf.connected(0, 3), uf.connected(0, 4))", "(4, 2, true, false)",
          setup="let mut uf = UnionFind::new(5);\nuf.union(0, 1);\nuf.union(2, 3);\nuf.union(1, 3);"),
        T("union_with_itself", "n = 2; union(1, 1)", "(uf.union(1, 1), uf.set_count(), uf.set_size(1))", "(false, 2, 1)", setup="let mut uf = UnionFind::new(2);"),
        T("connected_to_itself", "n = 4; connected(3, 3)", "(uf.connected(3, 3), uf.find(3))", "(true, 3)", setup="let mut uf = UnionFind::new(4);"),
    ],
    hidden=[
        T("million_chain", "n = 10⁶; union(i, i + 1) for all i", "(uf.set_count(), uf.connected(0, 999_999), uf.set_size(500_000))", "(1, true, 1_000_000)",
          setup="let mut uf = UnionFind::new(1_000_000);\nfor i in 0..999_999 {\n    uf.union(i, i + 1);\n}"),
        T("self_union", "union(2, 2)", "(uf.union(2, 2), uf.set_count())", "(false, 4)", setup="let mut uf = UnionFind::new(4);"),
        T("repeated_union", "n = 3; union(0,1) twice, then union(1,0)", "(a, b, c, uf.set_count(), uf.set_size(1))", "(true, false, false, 2, 2)",
          setup="let mut uf = UnionFind::new(3);\nlet (a, b, c) = (uf.union(0, 1), uf.union(0, 1), uf.union(1, 0));"),
        T("same_root_for_the_whole_set", "n = 6; union(0,1), union(2,3), union(4,5), union(1,2), union(3,4)", "(1..6).all(|i| uf.find(i) == r)", "true",
          setup="let mut uf = UnionFind::new(6);\nfor (a, b) in [(0, 1), (2, 3), (4, 5), (1, 2), (3, 4)] {\n    uf.union(a, b);\n}\nlet r = uf.find(0);"),
        T("small_into_big_keeps_sizes", "n = 6; build {0,1,2,3}, then union(5, 0)", "(uf.set_size(5), uf.set_size(3), uf.set_size(4), uf.set_count())", "(5, 5, 1, 2)",
          setup="let mut uf = UnionFind::new(6);\nuf.union(0, 1);\nuf.union(2, 3);\nuf.union(0, 2);\nuf.union(5, 0);"),
        T("empty", "n = 0", "uf.set_count()", "0", setup="let uf = UnionFind::new(0);"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(925);
            for _ in 0..200 {
                let n = 1 + rng.below(8);
                let mut uf = UnionFind::new(n);
                let mut label: Vec<usize> = (0..n).collect();
                let mut log = Vec::new();
                for _ in 0..12 {
                    let (a, b) = (rng.below(n), rng.below(n));
                    log.push((a, b));
                    let (la, lb) = (label[a], label[b]);
                    let merged = la != lb;
                    for l in label.iter_mut() {
                        if *l == lb {
                            *l = la;
                        }
                    }
                    let x = rng.below(n);
                    let sets = {
                        let mut ls = label.clone();
                        ls.sort_unstable();
                        ls.dedup();
                        ls.len()
                    };
                    let got = (uf.union(a, b), uf.connected(a, x), uf.set_size(x), uf.set_count());
                    let want = (merged, label[a] == label[x], label.iter().filter(|&&l| l == label[x]).count(), sets);
                    check!(format!("n = {n}, unions so far = {log:?}; then union({a}, {b}), connected({a}, {x}), set_size({x}), set_count()"), got, want);
                }
            }
        }

        #[test]
        fn scale_union_onto_a_growing_root() {
            // union(0, i) for every i: without size or compression, the path from 0 grows by one each time.
            let n = 200_000;
            let mut uf = UnionFind::new(n);
            for i in 1..n {
                uf.union(0, i);
            }
            check!("n = 200000; union(0, i) for every i", (uf.set_count(), uf.set_size(0), uf.connected(0, n - 1)), (1, n, true));
        }
        """,
    ],
    wrong=dict(
        no_size_no_compression="""
            pub struct UnionFind {
                parent: Vec<usize>,
                size: Vec<usize>,
                sets: usize,
            }

            impl UnionFind {
                pub fn new(n: usize) -> Self {
                    UnionFind { parent: (0..n).collect(), size: vec![1; n], sets: n }
                }

                pub fn find(&mut self, mut x: usize) -> usize {
                    while self.parent[x] != x {
                        x = self.parent[x];
                    }
                    x
                }

                pub fn union(&mut self, a: usize, b: usize) -> bool {
                    let (ra, rb) = (self.find(a), self.find(b));
                    if ra == rb {
                        return false;
                    }
                    self.parent[ra] = rb;
                    self.size[rb] += self.size[ra];
                    self.sets -= 1;
                    true
                }

                pub fn connected(&mut self, a: usize, b: usize) -> bool {
                    self.find(a) == self.find(b)
                }

                pub fn set_size(&mut self, x: usize) -> usize {
                    let r = self.find(x);
                    self.size[r]
                }

                pub fn set_count(&self) -> usize {
                    self.sets
                }
            }
        """,
        recursive_find_without_size="""
            pub struct UnionFind {
                parent: Vec<usize>,
                size: Vec<usize>,
                sets: usize,
            }

            impl UnionFind {
                pub fn new(n: usize) -> Self {
                    UnionFind { parent: (0..n).collect(), size: vec![1; n], sets: n }
                }

                pub fn find(&mut self, x: usize) -> usize {
                    let p = self.parent[x];
                    if p != x {
                        self.parent[x] = self.find(p);
                    }
                    self.parent[x]
                }

                pub fn union(&mut self, a: usize, b: usize) -> bool {
                    let (ra, rb) = (self.find(a), self.find(b));
                    if ra == rb {
                        return false;
                    }
                    self.parent[ra] = rb;
                    self.size[rb] += self.size[ra];
                    self.sets -= 1;
                    true
                }

                pub fn connected(&mut self, a: usize, b: usize) -> bool {
                    self.find(a) == self.find(b)
                }

                pub fn set_size(&mut self, x: usize) -> usize {
                    let r = self.find(x);
                    self.size[r]
                }

                pub fn set_count(&self) -> usize {
                    self.sets
                }
            }
        """,
        size_added_to_the_child="""
            pub struct UnionFind {
                parent: Vec<usize>,
                size: Vec<usize>,
                sets: usize,
            }

            impl UnionFind {
                pub fn new(n: usize) -> Self {
                    UnionFind { parent: (0..n).collect(), size: vec![1; n], sets: n }
                }

                pub fn find(&mut self, x: usize) -> usize {
                    let mut root = x;
                    while self.parent[root] != root {
                        root = self.parent[root];
                    }
                    let mut x = x;
                    while self.parent[x] != root {
                        let next = self.parent[x];
                        self.parent[x] = root;
                        x = next;
                    }
                    root
                }

                pub fn union(&mut self, a: usize, b: usize) -> bool {
                    let (mut ra, mut rb) = (self.find(a), self.find(b));
                    if ra == rb {
                        return false;
                    }
                    if self.size[ra] < self.size[rb] {
                        std::mem::swap(&mut ra, &mut rb);
                    }
                    self.parent[rb] = ra;
                    self.size[rb] += self.size[ra];
                    self.sets -= 1;
                    true
                }

                pub fn connected(&mut self, a: usize, b: usize) -> bool {
                    self.find(a) == self.find(b)
                }

                pub fn set_size(&mut self, x: usize) -> usize {
                    let r = self.find(x);
                    self.size[r]
                }

                pub fn set_count(&self) -> usize {
                    self.sets
                }
            }
        """,
    ),
    hints=[("rust", "`find` compresses paths, which writes to `parent`, so it needs `&mut self`; `connected` inherits that."),
           ("approach", "Hang the smaller tree under the larger root, and keep sizes only at roots."),
           ("approach", "Find the root with one loop, then point every node on the path straight at it with a second loop. No recursion.")],
    notes=("Union by size keeps trees O(log n) tall even before compression; together they give near-constant amortised time. The two-pass `find` avoids recursion on long chains.", "O(α(n)) amortised", "O(n)"),
    follow_up="How would you support undoing the last union (rollback), and what does that cost?",
))

P.append(dict(
    slug="fix-two-mut-into-one-parent-vec", title="Fix: two &mut into one parent Vec", mode="fix", level="hard", stage="union-find-mst",
    tags=["E0499", "recursion"],
    teaches=["A `&mut` into a Vec element blocks every other use of the Vec.", "Copy the index out, recurse, then write back."],
    statement="`find` should return the root and point every node on the way directly at it. It doesn't compile.",
    starter="""
        /// Root of `x`, pointing every node on the way straight at the root.
        pub fn find(parent: &mut [usize], x: usize) -> usize {
            let p = &mut parent[x];
            if *p != x {
                *p = find(parent, *p);
            }
            *p
        }

        /// Merges the sets holding `a` and `b`. Returns false if they were already together.
        pub fn union(parent: &mut [usize], a: usize, b: usize) -> bool {
            let (ra, rb) = (find(parent, a), find(parent, b));
            if ra == rb {
                return false;
            }
            parent[ra] = rb;
            true
        }
    """,
    solution="""
        /// Root of `x`, pointing every node on the way straight at the root.
        pub fn find(parent: &mut [usize], x: usize) -> usize {
            let p = parent[x];
            if p != x {
                parent[x] = find(parent, p);
            }
            parent[x]
        }

        /// Merges the sets holding `a` and `b`. Returns false if they were already together.
        pub fn union(parent: &mut [usize], a: usize, b: usize) -> bool {
            let (ra, rb) = (find(parent, a), find(parent, b));
            if ra == rb {
                return false;
            }
            parent[ra] = rb;
            true
        }
    """,
    visible=[
        T("compresses", "parent = [1, 2, 3, 3]; find(0)", "(root, p)", "(3, vec![3, 3, 3, 3])", setup="let mut p = vec![1, 2, 3, 3];\nlet root = find(&mut p, 0);"),
        T("unions", "4 singletons; union(0,1), union(2,3), union(1,3), union(0,2)", "(a, b, c, d)", "(true, true, true, false)",
          setup="let mut p: Vec<usize> = (0..4).collect();\nlet (a, b, c, d) = (union(&mut p, 0, 1), union(&mut p, 2, 3), union(&mut p, 1, 3), union(&mut p, 0, 2));"),
        T("already_flat", "parent = [0, 0, 0]; find(2)", "(root, p)", "(0, vec![0, 0, 0])", setup="let mut p = vec![0, 0, 0];\nlet root = find(&mut p, 2);"),
        T("union_hangs_first_root_under_second", "parent = [0, 1, 2]; union(0, 2)", "(merged, p)", "(true, vec![2, 1, 2])",
          setup="let mut p = vec![0, 1, 2];\nlet merged = union(&mut p, 0, 2);"),
        T("only_the_path_is_rewritten", "parent = [1, 2, 3, 3, 0]; find(1)", "(root, p)", "(3, vec![1, 3, 3, 3, 0])",
          setup="let mut p = vec![1, 2, 3, 3, 0];\nlet root = find(&mut p, 1);"),
    ],
    hidden=[
        T("root_itself", "parent = [0]; find(0)", "find(&mut [0], 0)", "0"),
        T("mid_path", "parent = [1, 2, 2, 0]; find(3)", "(root, p)", "(2, vec![2, 2, 2, 2])", setup="let mut p = vec![1, 2, 2, 0];\nlet root = find(&mut p, 3);"),
        T("union_sequence", "5 singletons; union(0,1), union(1,2), union(0,2), union(3,4), union(4,0)", "(r, (0..5).all(|i| find(&mut p, i) == find(&mut p, 0)))", "(vec![true, true, false, true, true], true)",
          setup="let mut p: Vec<usize> = (0..5).collect();\nlet r: Vec<bool> = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 0)].into_iter().map(|(a, b)| union(&mut p, a, b)).collect();"),
        T("same_set_union_is_false", "parent = [1, 1]; union(0, 1)", "(union(&mut p, 0, 1), p)", "(false, vec![1, 1])", setup="let mut p = vec![1, 1];"),
        T("union_links_roots_not_nodes", "parent = [1, 1, 3, 3]; union(0, 2)", "(merged, p)", "(true, vec![1, 3, 3, 3])",
          setup="let mut p = vec![1, 1, 3, 3];\nlet merged = union(&mut p, 0, 2);"),
        T("chain_1000", "parent[i] = i - 1 for 1000 nodes; find(999)", "(root, p.iter().all(|&x| x == 0))", "(0, true)",
          setup="let mut p: Vec<usize> = (0..1000).map(|i: usize| i.saturating_sub(1)).collect();\nlet root = find(&mut p, 999);"),
        T("deep_node_then_its_ancestor", "parent = [0, 0, 1, 2, 3]; find(4), then find(2)", "(a, b, p)", "(0, 0, vec![0, 0, 0, 0, 0])",
          setup="let mut p = vec![0, 0, 1, 2, 3];\nlet a = find(&mut p, 4);\nlet b = find(&mut p, 2);"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(926);
            for _ in 0..300 {
                let n = 1 + rng.below(9);
                // A random forest: each node points at itself or at a smaller node.
                let parent: Vec<usize> = (0..n).map(|i| if i == 0 || rng.below(4) == 0 { i } else { rng.below(i) }).collect();
                let x = rng.below(n);
                let mut want = parent.clone();
                let mut root = x;
                while want[root] != root {
                    root = want[root];
                }
                let mut y = x;
                while want[y] != root {
                    let next = want[y];
                    want[y] = root;
                    y = next;
                }
                let mut got = parent.clone();
                let r = find(&mut got, x);
                check!(format!("parent = {parent:?}; find({x})"), (r, got), (root, want));
            }
        }
        """,
    ],
    wrong=dict(
        no_write_back="""
            /// Root of `x`, pointing every node on the way straight at the root.
            pub fn find(parent: &mut [usize], x: usize) -> usize {
                let p = parent[x];
                if p != x {
                    return find(parent, p);
                }
                x
            }

            /// Merges the sets holding `a` and `b`. Returns false if they were already together.
            pub fn union(parent: &mut [usize], a: usize, b: usize) -> bool {
                let (ra, rb) = (find(parent, a), find(parent, b));
                if ra == rb {
                    return false;
                }
                parent[ra] = rb;
                true
            }
        """,
        writes_the_parents_slot="""
            /// Root of `x`, pointing every node on the way straight at the root.
            pub fn find(parent: &mut [usize], x: usize) -> usize {
                let p = parent[x];
                if p != x {
                    parent[p] = find(parent, p);
                }
                parent[x]
            }

            /// Merges the sets holding `a` and `b`. Returns false if they were already together.
            pub fn union(parent: &mut [usize], a: usize, b: usize) -> bool {
                let (ra, rb) = (find(parent, a), find(parent, b));
                if ra == rb {
                    return false;
                }
                parent[ra] = rb;
                true
            }
        """,
    ),
    hints=[("rust", "`p` is a `&mut` into `parent`, and the recursive call needs all of `parent` while `p` is still alive."),
           ("approach", "Read the parent index as a plain `usize`, recurse, then write the result back with a fresh index.")],
    notes=("Copying the `usize` out ends the borrow before the recursive call; the write afterwards is a new, short borrow. Recursion depth is the path length, fine once union keeps trees shallow.", "O(α(n)) amortised", "O(depth) stack"),
    follow_up="Rewrite `find` without recursion. Which version would you ship?",
    rules=dict(methods=["clone", "to_vec"]),
    related=["L2"],
))

# ---------------------------------------------------------------- SCC, bridges & arenas

P.append(dict(
    slug="tarjans-scc", title="Tarjan's SCC", level="hard", stage="scc-bridges-arenas",
    tags=["SCC", "lowlink", "state struct"],
    teaches=["Recursive algorithms with lots of state: a struct and a `&mut self` method.", "Copying a `&'a` field out of `self` before looping over it."],
    statement="""
        Return the strongly connected components of a directed graph. Sort each component ascending, and the
        list of components by their smallest node.
    """,
    examples=[("adj = [[1], [2], [0, 3], [4], [5], [3]]", "[[0, 1, 2], [3, 4, 5]]")],
    constraints=["n ≤ 5000"],
    starter="""
        pub fn strongly_connected(adj: &[Vec<usize>]) -> Vec<Vec<usize>> {
            todo!()
        }
    """,
    solution="""
        struct Tarjan<'a> {
            adj: &'a [Vec<usize>],
            index: Vec<Option<usize>>,
            low: Vec<usize>,
            on_stack: Vec<bool>,
            stack: Vec<usize>,
            next: usize,
            out: Vec<Vec<usize>>,
        }

        impl Tarjan<'_> {
            fn visit(&mut self, u: usize) {
                self.index[u] = Some(self.next);
                self.low[u] = self.next;
                self.next += 1;
                self.stack.push(u);
                self.on_stack[u] = true;

                // Copy the shared reference out so the loop doesn't borrow `self`.
                let adj = self.adj;
                for &v in &adj[u] {
                    match self.index[v] {
                        None => {
                            self.visit(v);
                            self.low[u] = self.low[u].min(self.low[v]);
                        }
                        Some(iv) if self.on_stack[v] => self.low[u] = self.low[u].min(iv),
                        Some(_) => {}
                    }
                }

                if self.index[u] == Some(self.low[u]) {
                    let mut component = Vec::new();
                    loop {
                        let w = self.stack.pop().expect("u is still on the stack");
                        self.on_stack[w] = false;
                        component.push(w);
                        if w == u {
                            break;
                        }
                    }
                    component.sort_unstable();
                    self.out.push(component);
                }
            }
        }

        pub fn strongly_connected(adj: &[Vec<usize>]) -> Vec<Vec<usize>> {
            let n = adj.len();
            let mut t = Tarjan {
                adj,
                index: vec![None; n],
                low: vec![0; n],
                on_stack: vec![false; n],
                stack: Vec::new(),
                next: 0,
                out: Vec::new(),
            };
            for u in 0..n {
                if t.index[u].is_none() {
                    t.visit(u);
                }
            }
            let mut out = t.out;
            out.sort_unstable();
            out
        }
    """,
    visible=[
        T("two_cycles", "adj = [[1], [2], [0, 3], [4], [5], [3]]", "strongly_connected(&[vec![1], vec![2], vec![0, 3], vec![4], vec![5], vec![3]])", "vec![vec![0, 1, 2], vec![3, 4, 5]]"),
        T("dag", "adj = [[1], [2], []]", "strongly_connected(&[vec![1], vec![2], vec![]])", "vec![vec![0], vec![1], vec![2]]"),
        T("single_node", "adj = [[]]", "strongly_connected(&[vec![]])", "vec![vec![0]]"),
        T("mutual_pair", "adj = [[1], [0]]", "strongly_connected(&[vec![1], vec![0]])", "vec![vec![0, 1]]"),
        T("components_sorted_by_smallest_node", "adj = [[3], [2], [1], [0]]", "strongly_connected(&[vec![3], vec![2], vec![1], vec![0]])", "vec![vec![0, 3], vec![1, 2]]"),
    ],
    hidden=[
        T("self_loop", "adj = [[0]]", "strongly_connected(&[vec![0]])", "vec![vec![0]]"),
        T("back_to_earlier_scc", "adj = [[1], [0], [0, 3], [2]]", "strongly_connected(&[vec![1], vec![0], vec![0, 3], vec![2]])", "vec![vec![0, 1], vec![2, 3]]"),
        T("big_cycle", "one cycle of 5000 nodes", "(out.len(), out[0].len())", "(1, 5000)",
          setup="let adj: Vec<Vec<usize>> = (0..5000).map(|i| vec![(i + 1) % 5000]).collect();\nlet out = strongly_connected(&adj);"),
        T("empty_graph", "adj = []", "strongly_connected(&[])", "Vec::<Vec<usize>>::new()"),
        T("cross_edge_to_a_finished_component", "adj = [[1, 2], [], [1]]", "strongly_connected(&[vec![1, 2], vec![], vec![1]])", "vec![vec![0], vec![1], vec![2]]"),
        T("repeated_edges", "adj = [[1, 1], [0, 0, 2], [2]]", "strongly_connected(&[vec![1, 1], vec![0, 0, 2], vec![2]])", "vec![vec![0, 1], vec![2]]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(927);
            for _ in 0..300 {
                let n = 1 + rng.below(8);
                let adj: Vec<Vec<usize>> = (0..n).map(|_| { let k = rng.below(3); (0..k).map(|_| rng.below(n)).collect() }).collect();
                // Brute force: transitive closure, then group nodes that reach each other.
                let mut reach = vec![vec![false; n]; n];
                for u in 0..n {
                    reach[u][u] = true;
                    for &v in &adj[u] {
                        reach[u][v] = true;
                    }
                }
                for k in 0..n {
                    for i in 0..n {
                        for j in 0..n {
                            if reach[i][k] && reach[k][j] {
                                reach[i][j] = true;
                            }
                        }
                    }
                }
                let mut want: Vec<Vec<usize>> = Vec::new();
                for u in 0..n {
                    if (0..u).all(|v| !(reach[u][v] && reach[v][u])) {
                        want.push((u..n).filter(|&v| reach[u][v] && reach[v][u]).collect());
                    }
                }
                check!(format!("adj = {adj:?}"), strongly_connected(&adj), want);
            }
        }

        #[test]
        fn chain_of_pairs_5000() {
            // 2i ↔ 2i+1, and 2i+1 → 2i+2: 2500 components of two.
            let adj: Vec<Vec<usize>> = (0..5000).map(|u| if u % 2 == 0 { vec![u + 1] } else if u + 1 < 5000 { vec![u - 1, u + 1] } else { vec![u - 1] }).collect();
            let out = strongly_connected(&adj);
            check!("2500 two-cycles joined in a chain", (out.len(), out[0].clone(), out[2499].clone()), (2500, vec![0, 1], vec![4998, 4999]));
        }
        """,
    ],
    wrong=dict(
        ignores_on_stack="""
            struct Tarjan<'a> {
                adj: &'a [Vec<usize>],
                index: Vec<Option<usize>>,
                low: Vec<usize>,
                stack: Vec<usize>,
                next: usize,
                out: Vec<Vec<usize>>,
            }

            impl Tarjan<'_> {
                fn visit(&mut self, u: usize) {
                    self.index[u] = Some(self.next);
                    self.low[u] = self.next;
                    self.next += 1;
                    self.stack.push(u);
                    let adj = self.adj;
                    for &v in &adj[u] {
                        match self.index[v] {
                            None => {
                                self.visit(v);
                                self.low[u] = self.low[u].min(self.low[v]);
                            }
                            Some(iv) => self.low[u] = self.low[u].min(iv),
                        }
                    }
                    if self.index[u] == Some(self.low[u]) {
                        let mut component = Vec::new();
                        loop {
                            let w = self.stack.pop().unwrap();
                            component.push(w);
                            if w == u {
                                break;
                            }
                        }
                        component.sort_unstable();
                        self.out.push(component);
                    }
                }
            }

            pub fn strongly_connected(adj: &[Vec<usize>]) -> Vec<Vec<usize>> {
                let n = adj.len();
                let mut t = Tarjan { adj, index: vec![None; n], low: vec![0; n], stack: Vec::new(), next: 0, out: Vec::new() };
                for u in 0..n {
                    if t.index[u].is_none() {
                        t.visit(u);
                    }
                }
                let mut out = t.out;
                out.sort_unstable();
                out
            }
        """,
        components_left_unsorted="""
            struct Tarjan<'a> {
                adj: &'a [Vec<usize>],
                index: Vec<Option<usize>>,
                low: Vec<usize>,
                on_stack: Vec<bool>,
                stack: Vec<usize>,
                next: usize,
                out: Vec<Vec<usize>>,
            }

            impl Tarjan<'_> {
                fn visit(&mut self, u: usize) {
                    self.index[u] = Some(self.next);
                    self.low[u] = self.next;
                    self.next += 1;
                    self.stack.push(u);
                    self.on_stack[u] = true;
                    let adj = self.adj;
                    for &v in &adj[u] {
                        match self.index[v] {
                            None => {
                                self.visit(v);
                                self.low[u] = self.low[u].min(self.low[v]);
                            }
                            Some(iv) if self.on_stack[v] => self.low[u] = self.low[u].min(iv),
                            Some(_) => {}
                        }
                    }
                    if self.index[u] == Some(self.low[u]) {
                        let mut component = Vec::new();
                        loop {
                            let w = self.stack.pop().unwrap();
                            self.on_stack[w] = false;
                            component.push(w);
                            if w == u {
                                break;
                            }
                        }
                        self.out.push(component);
                    }
                }
            }

            pub fn strongly_connected(adj: &[Vec<usize>]) -> Vec<Vec<usize>> {
                let n = adj.len();
                let mut t = Tarjan { adj, index: vec![None; n], low: vec![0; n], on_stack: vec![false; n], stack: Vec::new(), next: 0, out: Vec::new() };
                for u in 0..n {
                    if t.index[u].is_none() {
                        t.visit(u);
                    }
                }
                t.out
            }
        """,
    ),
    hints=[("approach", "Tarjan: number nodes in DFS order and track the lowest number reachable (`low`). A node whose `low` equals its own number roots a component; pop the stack down to it."),
           ("rust", "Put the state in a struct and write `fn visit(&mut self, u)`. Six parameters threaded through a free function is the alternative."),
           ("rust", "`for &v in &self.adj[u]` borrows `self` across `self.visit(v)`. `let adj = self.adj;` copies the `&[_]` out first.")],
    notes=("Each node is pushed and popped once, and each edge is examined once. Only nodes still on the stack can lower `low`; the rest belong to components already emitted.", "O(V + E)", "O(V)"),
    follow_up="Rewrite this without recursion so a 10⁶-node path doesn't overflow the stack.",
    related=["L2"],
))

P.append(dict(
    slug="critical-connections", title="Critical connections", level="hard", stage="scc-bridges-arenas",
    tags=["bridges", "lowlink", "edge ids"],
    teaches=["Skipping the parent edge by id, so parallel edges count.", "Reusing the state-struct pattern."],
    statement="""
        Return every edge of the undirected graph on nodes `0..n` whose removal disconnects the graph (the
        bridges). Write each as `(smaller, larger)` and sort the list.
    """,
    examples=[("n = 4, edges = [(0,1), (1,2), (2,0), (1,3)]", "[(1, 3)]")],
    constraints=["n ≤ 5000"],
    starter="""
        pub fn critical_connections(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
            todo!()
        }
    """,
    solution="""
        struct Bridges<'a> {
            adj: &'a [Vec<(usize, usize)>],
            edges: &'a [(usize, usize)],
            disc: Vec<Option<usize>>,
            low: Vec<usize>,
            time: usize,
            out: Vec<(usize, usize)>,
        }

        impl Bridges<'_> {
            /// `via` is the id of the edge used to reach `u`.
            fn visit(&mut self, u: usize, via: Option<usize>) {
                let du = self.time;
                self.disc[u] = Some(du);
                self.low[u] = du;
                self.time += 1;
                let adj = self.adj;
                for &(v, id) in &adj[u] {
                    if Some(id) == via {
                        continue;
                    }
                    match self.disc[v] {
                        Some(dv) => self.low[u] = self.low[u].min(dv),
                        None => {
                            self.visit(v, Some(id));
                            self.low[u] = self.low[u].min(self.low[v]);
                            if self.low[v] > du {
                                let (a, b) = self.edges[id];
                                self.out.push((a.min(b), a.max(b)));
                            }
                        }
                    }
                }
            }
        }

        pub fn critical_connections(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
            let mut adj = vec![Vec::new(); n];
            for (id, &(a, b)) in edges.iter().enumerate() {
                adj[a].push((b, id));
                adj[b].push((a, id));
            }
            let mut state = Bridges { adj: &adj, edges, disc: vec![None; n], low: vec![0; n], time: 0, out: Vec::new() };
            for u in 0..n {
                if state.disc[u].is_none() {
                    state.visit(u, None);
                }
            }
            let mut out = state.out;
            out.sort_unstable();
            out
        }
    """,
    visible=[
        T("one_bridge", "n = 4, edges = [(0,1), (1,2), (2,0), (1,3)]", "critical_connections(4, &[(0, 1), (1, 2), (2, 0), (1, 3)])", "vec![(1, 3)]"),
        T("single_edge", "n = 2, edges = [(1,0)]", "critical_connections(2, &[(1, 0)])", "vec![(0, 1)]"),
        T("cycle_has_no_bridges", "n = 3, edges = [(0,1), (1,2), (2,0)]", "critical_connections(3, &[(0, 1), (1, 2), (2, 0)])", "Vec::<(usize, usize)>::new()"),
        T("sorted_smaller_first", "n = 3, edges = [(2,1), (1,0)]", "critical_connections(3, &[(2, 1), (1, 0)])", "vec![(0, 1), (1, 2)]"),
        T("doubled_edge_is_not_a_bridge", "n = 3, edges = [(0,1), (1,0), (1,2)]", "critical_connections(3, &[(0, 1), (1, 0), (1, 2)])", "vec![(1, 2)]"),
    ],
    hidden=[
        T("parallel_edges", "n = 2, edges = [(0,1), (1,0)]", "critical_connections(2, &[(0, 1), (1, 0)])", "Vec::<(usize, usize)>::new()"),
        T("two_triangles", "triangles 0-1-2 and 3-4-5 joined by 2-3", "critical_connections(6, &[(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3)])", "vec![(2, 3)]"),
        T("path", "n = 4, path 0-1-2-3", "critical_connections(4, &[(0, 1), (1, 2), (2, 3)])", "vec![(0, 1), (1, 2), (2, 3)]"),
        T("no_edges", "n = 1, edges = []", "critical_connections(1, &[])", "Vec::<(usize, usize)>::new()"),
        T("several_components", "n = 5, edges = [(0,1), (2,3), (3,4), (4,2)]", "critical_connections(5, &[(0, 1), (2, 3), (3, 4), (4, 2)])", "vec![(0, 1)]"),
        T("self_loop", "n = 2, edges = [(0,0), (0,1)]", "critical_connections(2, &[(0, 0), (0, 1)])", "vec![(0, 1)]"),
        T("star", "n = 4, edges = [(3,0), (0,1), (2,0)]", "critical_connections(4, &[(3, 0), (0, 1), (2, 0)])", "vec![(0, 1), (0, 2), (0, 3)]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(928);
            for _ in 0..300 {
                let n = 1 + rng.below(7);
                let m = rng.below(9);
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                // Brute force: an edge is a bridge if removing it leaves its ends disconnected.
                let joined_without = |skip: usize| {
                    let (a, b) = edges[skip];
                    let mut seen = vec![false; n];
                    seen[a] = true;
                    let mut stack = vec![a];
                    while let Some(u) = stack.pop() {
                        for (i, &(x, y)) in edges.iter().enumerate() {
                            for (p, q) in [(x, y), (y, x)] {
                                if i != skip && p == u && !seen[q] {
                                    seen[q] = true;
                                    stack.push(q);
                                }
                            }
                        }
                    }
                    seen[b]
                };
                let mut want: Vec<(usize, usize)> = (0..m).filter(|&i| !joined_without(i)).map(|i| (edges[i].0.min(edges[i].1), edges[i].0.max(edges[i].1))).collect();
                want.sort_unstable();
                check!(format!("n = {n}, edges = {edges:?}"), critical_connections(n, &edges), want);
            }
        }

        #[test]
        fn cycle_then_path_5000() {
            // A cycle through 0..2500, then a path 2499-2500-…-4999.
            let mut edges: Vec<(usize, usize)> = (0..2500).map(|i| (i, (i + 1) % 2500)).collect();
            edges.extend((2499..4999).map(|i| (i, i + 1)));
            let out = critical_connections(5000, &edges);
            check!("n = 5000, cycle on 0..2500 plus a path to 4999", (out.len(), out[0], out[2499]), (2500, (2499, 2500), (4998, 4999)));
        }
        """,
    ],
    wrong=dict(
        skips_the_parent_node="""
            struct Bridges<'a> {
                adj: &'a [Vec<usize>],
                disc: Vec<Option<usize>>,
                low: Vec<usize>,
                time: usize,
                out: Vec<(usize, usize)>,
            }

            impl Bridges<'_> {
                fn visit(&mut self, u: usize, parent: Option<usize>) {
                    let du = self.time;
                    self.disc[u] = Some(du);
                    self.low[u] = du;
                    self.time += 1;
                    let adj = self.adj;
                    for &v in &adj[u] {
                        if Some(v) == parent {
                            continue;
                        }
                        match self.disc[v] {
                            Some(dv) => self.low[u] = self.low[u].min(dv),
                            None => {
                                self.visit(v, Some(u));
                                self.low[u] = self.low[u].min(self.low[v]);
                                if self.low[v] > du {
                                    self.out.push((u.min(v), u.max(v)));
                                }
                            }
                        }
                    }
                }
            }

            pub fn critical_connections(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
                let mut adj = vec![Vec::new(); n];
                for &(a, b) in edges {
                    adj[a].push(b);
                    adj[b].push(a);
                }
                let mut state = Bridges { adj: &adj, disc: vec![None; n], low: vec![0; n], time: 0, out: Vec::new() };
                for u in 0..n {
                    if state.disc[u].is_none() {
                        state.visit(u, None);
                    }
                }
                let mut out = state.out;
                out.sort_unstable();
                out
            }
        """,
        greater_or_equal="""
            struct Bridges<'a> {
                adj: &'a [Vec<(usize, usize)>],
                edges: &'a [(usize, usize)],
                disc: Vec<Option<usize>>,
                low: Vec<usize>,
                time: usize,
                out: Vec<(usize, usize)>,
            }

            impl Bridges<'_> {
                fn visit(&mut self, u: usize, via: Option<usize>) {
                    let du = self.time;
                    self.disc[u] = Some(du);
                    self.low[u] = du;
                    self.time += 1;
                    let adj = self.adj;
                    for &(v, id) in &adj[u] {
                        if Some(id) == via {
                            continue;
                        }
                        match self.disc[v] {
                            Some(dv) => self.low[u] = self.low[u].min(dv),
                            None => {
                                self.visit(v, Some(id));
                                self.low[u] = self.low[u].min(self.low[v]);
                                if self.low[v] >= du {
                                    let (a, b) = self.edges[id];
                                    self.out.push((a.min(b), a.max(b)));
                                }
                            }
                        }
                    }
                }
            }

            pub fn critical_connections(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
                let mut adj = vec![Vec::new(); n];
                for (id, &(a, b)) in edges.iter().enumerate() {
                    adj[a].push((b, id));
                    adj[b].push((a, id));
                }
                let mut state = Bridges { adj: &adj, edges, disc: vec![None; n], low: vec![0; n], time: 0, out: Vec::new() };
                for u in 0..n {
                    if state.disc[u].is_none() {
                        state.visit(u, None);
                    }
                }
                let mut out = state.out;
                out.sort_unstable();
                out
            }
        """,
        pairs_as_given="""
            struct Bridges<'a> {
                adj: &'a [Vec<(usize, usize)>],
                edges: &'a [(usize, usize)],
                disc: Vec<Option<usize>>,
                low: Vec<usize>,
                time: usize,
                out: Vec<(usize, usize)>,
            }

            impl Bridges<'_> {
                fn visit(&mut self, u: usize, via: Option<usize>) {
                    let du = self.time;
                    self.disc[u] = Some(du);
                    self.low[u] = du;
                    self.time += 1;
                    let adj = self.adj;
                    for &(v, id) in &adj[u] {
                        if Some(id) == via {
                            continue;
                        }
                        match self.disc[v] {
                            Some(dv) => self.low[u] = self.low[u].min(dv),
                            None => {
                                self.visit(v, Some(id));
                                self.low[u] = self.low[u].min(self.low[v]);
                                if self.low[v] > du {
                                    self.out.push(self.edges[id]);
                                }
                            }
                        }
                    }
                }
            }

            pub fn critical_connections(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
                let mut adj = vec![Vec::new(); n];
                for (id, &(a, b)) in edges.iter().enumerate() {
                    adj[a].push((b, id));
                    adj[b].push((a, id));
                }
                let mut state = Bridges { adj: &adj, edges, disc: vec![None; n], low: vec![0; n], time: 0, out: Vec::new() };
                for u in 0..n {
                    if state.disc[u].is_none() {
                        state.visit(u, None);
                    }
                }
                let mut out = state.out;
                out.sort_unstable();
                out
            }
        """,
    ),
    hints=[("approach", "Edge (u, v) to a DFS child v is a bridge when nothing in v's subtree reaches u or above: `low[v] > disc[u]`."),
           ("edge case", "Skip the edge you arrived by, not the parent node. Otherwise a doubled edge looks like a bridge."),
           ("rust", "Store `(neighbour, edge_id)` in the adjacency list so the edge can be identified.")],
    notes=("Same lowlink idea as Tarjan's SCC, on undirected edges. Skipping by edge id handles parallel edges, which skipping by parent node gets wrong.", "O(V + E)", "O(V + E)"),
    follow_up="How would you find articulation points (critical nodes) instead?",
))

P.append(dict(
    slug="arena-allocated-graph", title="Arena-allocated graph", level="hard", stage="scc-bridges-arenas",
    tags=["arena", "newtype ids", "generics"],
    teaches=["A `NodeId` newtype that only the graph can create.", "Mutating one node while holding ids to others."],
    statement="""
        Build a generic graph that owns every node's value in one `Vec` and hands out `NodeId`s. Edges are
        directed. `reachable` returns the nodes reachable from `from` (itself first) in BFS order, trying
        neighbours in the order their edges were added.
    """,
    starter="""
        #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
        pub struct NodeId(usize);

        pub struct Graph<T> {
            values: Vec<T>,
            edges: Vec<Vec<NodeId>>,
        }

        impl<T> Default for Graph<T> {
            fn default() -> Self {
                Graph { values: Vec::new(), edges: Vec::new() }
            }
        }

        impl<T> Graph<T> {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn add_node(&mut self, value: T) -> NodeId {
                todo!()
            }

            pub fn add_edge(&mut self, from: NodeId, to: NodeId) {
                todo!()
            }

            pub fn value(&self, id: NodeId) -> &T {
                todo!()
            }

            pub fn value_mut(&mut self, id: NodeId) -> &mut T {
                todo!()
            }

            pub fn neighbors(&self, id: NodeId) -> &[NodeId] {
                todo!()
            }

            pub fn reachable(&self, from: NodeId) -> Vec<NodeId> {
                todo!()
            }
        }
    """,
    solution="""
        use std::collections::VecDeque;

        #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
        pub struct NodeId(usize);

        pub struct Graph<T> {
            values: Vec<T>,
            edges: Vec<Vec<NodeId>>,
        }

        impl<T> Default for Graph<T> {
            fn default() -> Self {
                Graph { values: Vec::new(), edges: Vec::new() }
            }
        }

        impl<T> Graph<T> {
            pub fn new() -> Self {
                Self::default()
            }

            pub fn add_node(&mut self, value: T) -> NodeId {
                self.values.push(value);
                self.edges.push(Vec::new());
                NodeId(self.values.len() - 1)
            }

            pub fn add_edge(&mut self, from: NodeId, to: NodeId) {
                self.edges[from.0].push(to);
            }

            pub fn value(&self, id: NodeId) -> &T {
                &self.values[id.0]
            }

            pub fn value_mut(&mut self, id: NodeId) -> &mut T {
                &mut self.values[id.0]
            }

            pub fn neighbors(&self, id: NodeId) -> &[NodeId] {
                &self.edges[id.0]
            }

            pub fn reachable(&self, from: NodeId) -> Vec<NodeId> {
                let mut seen = vec![false; self.values.len()];
                seen[from.0] = true;
                let mut order = Vec::new();
                let mut queue = VecDeque::from([from]);
                while let Some(u) = queue.pop_front() {
                    order.push(u);
                    for &v in self.neighbors(u) {
                        if !seen[v.0] {
                            seen[v.0] = true;
                            queue.push_back(v);
                        }
                    }
                }
                order
            }
        }
    """,
    visible=[
        T("cycle_and_edit", "a → b → c → a; append \"!\" to b; values reachable from a", "names", 'vec!["a", "b!", "c"]',
          setup="""
            let mut g = Graph::new();
            let a = g.add_node("a".to_string());
            let b = g.add_node("b".to_string());
            let c = g.add_node("c".to_string());
            g.add_edge(a, b);
            g.add_edge(b, c);
            g.add_edge(c, a);
            g.value_mut(b).push('!');
            let names: Vec<String> = g.reachable(a).into_iter().map(|id| g.value(id).to_string()).collect();
          """),
        T("neighbours", "a → c, a → b", "(g.neighbors(a) == [c, b], g.neighbors(b).is_empty())", "(true, true)",
          setup="let mut g = Graph::new();\nlet a = g.add_node(1);\nlet b = g.add_node(2);\nlet c = g.add_node(3);\ng.add_edge(a, c);\ng.add_edge(a, b);"),
        T("lone_node_reaches_itself", "a single node a", "(g.reachable(a) == [a], *g.value(a))", '(true, "a")',
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");'),
        T("edges_are_directed", "a → b; reachable from b", "g.reachable(b) == [b]", "true",
          setup='let mut g = Graph::new();\nlet a = g.add_node("a");\nlet b = g.add_node("b");\ng.add_edge(a, b);'),
        T("breadth_first", "a → b, a → c, b → d, c → e; values reachable from a", "vals", 'vec!["a", "b", "c", "d", "e"]',
          setup='let mut g = Graph::new();\nlet ids: Vec<NodeId> = ["a", "b", "c", "d", "e"].into_iter().map(|v| g.add_node(v)).collect();\nfor (x, y) in [(0, 1), (0, 2), (1, 3), (2, 4)] {\n    g.add_edge(ids[x], ids[y]);\n}\nlet vals: Vec<&str> = g.reachable(ids[0]).into_iter().map(|id| *g.value(id)).collect();'),
    ],
    hidden=[
        T("self_edge", "a → a, a → b", "(g.reachable(a) == [a, b], g.neighbors(a) == [a, b])", "(true, true)",
          setup="let mut g = Graph::new();\nlet a = g.add_node(());\nlet b = g.add_node(());\ng.add_edge(a, a);\ng.add_edge(a, b);"),
        T("duplicate_edge", "a → b twice", "(g.neighbors(a).len(), g.reachable(a).len())", "(2, 2)",
          setup="let mut g = Graph::new();\nlet a = g.add_node('a');\nlet b = g.add_node('b');\ng.add_edge(a, b);\ng.add_edge(a, b);"),
        T("value_mut_edits_in_place", "three nodes 1, 2, 3; add 10 to each through value_mut", "(*g.value(a), *g.value(b), *g.value(c))", "(11, 12, 13)",
          setup="let mut g = Graph::new();\nlet (a, b, c) = (g.add_node(1), g.add_node(2), g.add_node(3));\nfor id in [a, b, c] {\n    *g.value_mut(id) += 10;\n}"),
        T("ids_are_distinct", "add three nodes with the same value", "(a != b, b != c, a != c)", "(true, true, true)",
          setup="let mut g = Graph::new();\nlet (a, b, c) = (g.add_node(0), g.add_node(0), g.add_node(0));"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(929);
            for _ in 0..300 {
                let n = 1 + rng.below(8);
                let m = rng.below(12);
                let mut g = Graph::new();
                let ids: Vec<NodeId> = (0..n).map(|i| g.add_node(i)).collect();
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
                for &(u, v) in &edges {
                    g.add_edge(ids[u], ids[v]);
                }
                let start = rng.below(n);
                // Brute force: BFS over the edge list, in the order edges were added.
                let mut want = vec![start];
                let mut i = 0;
                while i < want.len() {
                    let u = want[i];
                    i += 1;
                    for &(a, b) in &edges {
                        if a == u && !want.contains(&b) {
                            want.push(b);
                        }
                    }
                }
                let got: Vec<usize> = g.reachable(ids[start]).into_iter().map(|id| *g.value(id)).collect();
                check!(format!("n = {n}, edges = {edges:?}, from {start}"), got, want);
            }
        }

        #[test]
        fn scale_chain_200k() {
            let mut g = Graph::new();
            let ids: Vec<NodeId> = (0..200_000u32).map(|i| g.add_node(i)).collect();
            for w in ids.windows(2) {
                g.add_edge(w[0], w[1]);
            }
            let r = g.reachable(ids[0]);
            check!("chain of 200000 nodes; reachable from the first", (r.len(), *g.value(r[199_999])), (200_000, 199_999));
        }
        """,
        T("unreachable", "a → b, c alone; reachable from a", "(r.len(), r.contains(&c))", "(2, false)",
          setup="let mut g = Graph::new();\nlet a = g.add_node(0u8);\nlet b = g.add_node(1);\nlet c = g.add_node(2);\ng.add_edge(a, b);\nlet r = g.reachable(a);"),
        T("bfs_order", "a → b, a → c, b → d; values reachable from a", "vals", "vec![10, 20, 30, 40]",
          setup="let mut g = Graph::new();\nlet a = g.add_node(10);\nlet b = g.add_node(20);\nlet c = g.add_node(30);\nlet d = g.add_node(40);\ng.add_edge(a, b);\ng.add_edge(a, c);\ng.add_edge(b, d);\nlet vals: Vec<i32> = g.reachable(a).into_iter().map(|id| *g.value(id)).collect();"),
    ],
    wrong=dict(
        depth_first="""
            #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
            pub struct NodeId(usize);

            pub struct Graph<T> {
                values: Vec<T>,
                edges: Vec<Vec<NodeId>>,
            }

            impl<T> Default for Graph<T> {
                fn default() -> Self {
                    Graph { values: Vec::new(), edges: Vec::new() }
                }
            }

            impl<T> Graph<T> {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn add_node(&mut self, value: T) -> NodeId {
                    self.values.push(value);
                    self.edges.push(Vec::new());
                    NodeId(self.values.len() - 1)
                }

                pub fn add_edge(&mut self, from: NodeId, to: NodeId) {
                    self.edges[from.0].push(to);
                }

                pub fn value(&self, id: NodeId) -> &T {
                    &self.values[id.0]
                }

                pub fn value_mut(&mut self, id: NodeId) -> &mut T {
                    &mut self.values[id.0]
                }

                pub fn neighbors(&self, id: NodeId) -> &[NodeId] {
                    &self.edges[id.0]
                }

                pub fn reachable(&self, from: NodeId) -> Vec<NodeId> {
                    let mut seen = vec![false; self.values.len()];
                    let mut order = Vec::new();
                    let mut stack = vec![from];
                    while let Some(u) = stack.pop() {
                        if seen[u.0] {
                            continue;
                        }
                        seen[u.0] = true;
                        order.push(u);
                        stack.extend(self.neighbors(u).iter().rev());
                    }
                    order
                }
            }
        """,
        order_doubles_as_seen="""
            #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
            pub struct NodeId(usize);

            pub struct Graph<T> {
                values: Vec<T>,
                edges: Vec<Vec<NodeId>>,
            }

            impl<T> Default for Graph<T> {
                fn default() -> Self {
                    Graph { values: Vec::new(), edges: Vec::new() }
                }
            }

            impl<T> Graph<T> {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn add_node(&mut self, value: T) -> NodeId {
                    self.values.push(value);
                    self.edges.push(Vec::new());
                    NodeId(self.values.len() - 1)
                }

                pub fn add_edge(&mut self, from: NodeId, to: NodeId) {
                    self.edges[from.0].push(to);
                }

                pub fn value(&self, id: NodeId) -> &T {
                    &self.values[id.0]
                }

                pub fn value_mut(&mut self, id: NodeId) -> &mut T {
                    &mut self.values[id.0]
                }

                pub fn neighbors(&self, id: NodeId) -> &[NodeId] {
                    &self.edges[id.0]
                }

                pub fn reachable(&self, from: NodeId) -> Vec<NodeId> {
                    let mut order = vec![from];
                    let mut i = 0;
                    while i < order.len() {
                        let u = order[i];
                        i += 1;
                        for &v in self.neighbors(u) {
                            if !order.contains(&v) {
                                order.push(v);
                            }
                        }
                    }
                    order
                }
            }
        """,
    ),
    hints=[("rust", "`NodeId(usize)` with a private field: only this module can make one, so every id came from `add_node`."),
           ("approach", "Keep values and edge lists in two Vecs indexed by the same id.")],
    notes=("The arena owns everything, ids are `Copy`, and cycles cost nothing: no `Rc`, no `RefCell`, no leaks. `value_mut` borrows the graph only for one call, so editing a node while holding ids is fine.", "O(1) per operation · O(V + E) for reachable", "O(V + E)"),
    follow_up="How would you support removing nodes without invalidating other ids (generational indices)?",
    related=["L7", "C2"],
))

P.append(dict(
    slug="fix-rc-refcell-node-cycle-leak", title="Fix: Rc<RefCell<Node>> cycle leak", mode="fix", level="hard", stage="scc-bridges-arenas",
    tags=["Rc", "Weak", "leaks"],
    teaches=["Parent ↔ child `Rc` cycles never drop.", "`Weak` for back-pointers; `upgrade()` when you need it."],
    statement="""
        A tree where each child points back at its parent. It works, but dropping the tree frees nothing,
        because parent and child keep each other alive. Fix it so dropping the last outside handle frees
        the tree. Keep the public methods.
    """,
    starter="""
        use std::cell::RefCell;
        use std::rc::Rc;

        pub struct Node {
            pub name: String,
            parent: Option<Rc<Node>>,
            children: RefCell<Vec<Rc<Node>>>,
        }

        impl Node {
            pub fn root(name: &str) -> Rc<Node> {
                Rc::new(Node { name: name.to_string(), parent: None, children: RefCell::new(Vec::new()) })
            }

            pub fn add_child(self: &Rc<Self>, name: &str) -> Rc<Node> {
                let child = Rc::new(Node {
                    name: name.to_string(),
                    parent: Some(Rc::clone(self)),
                    children: RefCell::new(Vec::new()),
                });
                self.children.borrow_mut().push(Rc::clone(&child));
                child
            }

            pub fn parent_name(&self) -> Option<String> {
                self.parent.as_ref().map(|p| p.name.to_string())
            }

            pub fn child_names(&self) -> Vec<String> {
                self.children.borrow().iter().map(|c| c.name.to_string()).collect()
            }
        }
    """,
    solution="""
        use std::cell::RefCell;
        use std::rc::{Rc, Weak};

        pub struct Node {
            pub name: String,
            parent: Weak<Node>,
            children: RefCell<Vec<Rc<Node>>>,
        }

        impl Node {
            pub fn root(name: &str) -> Rc<Node> {
                Rc::new(Node { name: name.to_string(), parent: Weak::new(), children: RefCell::new(Vec::new()) })
            }

            pub fn add_child(self: &Rc<Self>, name: &str) -> Rc<Node> {
                let child = Rc::new(Node {
                    name: name.to_string(),
                    parent: Rc::downgrade(self),
                    children: RefCell::new(Vec::new()),
                });
                self.children.borrow_mut().push(Rc::clone(&child));
                child
            }

            pub fn parent_name(&self) -> Option<String> {
                self.parent.upgrade().map(|p| p.name.to_string())
            }

            pub fn child_names(&self) -> Vec<String> {
                self.children.borrow().iter().map(|c| c.name.to_string()).collect()
            }
        }
    """,
    visible=[
        T("links", "root r with child c", "(c.parent_name(), r.child_names())", '(Some("r".to_string()), vec!["c".to_string()])',
          setup='let r = Node::root("r");\nlet c = r.add_child("c");'),
        T("freed", "drop the root and its child; is the root gone?", "w.upgrade().is_none()", "true",
          setup='let r = Node::root("r");\nlet c = r.add_child("c");\nlet w = std::rc::Rc::downgrade(&r);\ndrop(c);\ndrop(r);'),
        T("root_has_no_parent", "a lone root r", "(r.parent_name(), r.child_names())", "(None, Vec::<String>::new())", setup='let r = Node::root("r");'),
        T("children_in_order", "root r with children a, then b", "r.child_names()", 'vec!["a".to_string(), "b".to_string()]',
          setup='let r = Node::root("r");\nr.add_child("a");\nr.add_child("b");'),
        T("parent_keeps_children_alive", "root r with child c; drop the handle to c", "(r.child_names(), w.upgrade().is_some())", '(vec!["c".to_string()], true)',
          setup='let r = Node::root("r");\nlet c = r.add_child("c");\nlet w = std::rc::Rc::downgrade(&c);\ndrop(c);'),
    ],
    hidden=[
        T("grandchild_freed", "r → c → g; drop every handle", "(wr.upgrade().is_none(), wg.upgrade().is_none())", "(true, true)",
          setup='let r = Node::root("r");\nlet c = r.add_child("c");\nlet g = c.add_child("g");\nlet (wr, wg) = (std::rc::Rc::downgrade(&r), std::rc::Rc::downgrade(&g));\ndrop(g);\ndrop(c);\ndrop(r);'),
        T("orphan", "keep the child, drop the root", "c.parent_name()", "None",
          setup='let r = Node::root("r");\nlet c = r.add_child("c");\ndrop(r);'),
        T("only_one_strong_handle_to_the_root", "root r with three children", "std::rc::Rc::strong_count(&r)", "1",
          setup='let r = Node::root("r");\nlet _kids: Vec<_> = ["a", "b", "c"].into_iter().map(|n| r.add_child(n)).collect();'),
        T("grandchild_sees_its_parent", "r → c → g", "(g.parent_name(), c.parent_name(), c.child_names())", '(Some("c".to_string()), Some("r".to_string()), vec!["g".to_string()])',
          setup='let r = Node::root("r");\nlet c = r.add_child("c");\nlet g = c.add_child("g");'),
        T("unicode_names", 'root "根" with child "é"', "(c.parent_name(), r.child_names())", '(Some("根".to_string()), vec!["é".to_string()])',
          setup='let r = Node::root("根");\nlet c = r.add_child("é");'),
        T("deep_chain_freed", "a chain 100 levels deep; drop every handle", "(wr.upgrade().is_none(), wleaf.upgrade().is_none())", "(true, true)",
          setup='let r = Node::root("0");\nlet mut cur = std::rc::Rc::clone(&r);\nfor i in 1..100 {\n    let next = cur.add_child(&i.to_string());\n    cur = next;\n}\nlet (wr, wleaf) = (std::rc::Rc::downgrade(&r), std::rc::Rc::downgrade(&cur));\ndrop(cur);\ndrop(r);'),
        T("many_children_freed", "root with 1000 children; drop every handle", "weak.iter().all(|w| w.upgrade().is_none())", "true",
          setup='let r = Node::root("r");\nlet weak: Vec<_> = (0..1000).map(|i| std::rc::Rc::downgrade(&r.add_child(&i.to_string()))).collect();\ndrop(r);'),
        T("child_kept_while_root_lives", "keep the root, drop the child handle, then ask the root", "r.child_names().len()", "1",
          setup='let r = Node::root("r");\ndrop(r.add_child("c"));'),
    ],
    wrong=dict(
        weak_children="""
            use std::cell::RefCell;
            use std::rc::{Rc, Weak};

            pub struct Node {
                pub name: String,
                parent: Option<Rc<Node>>,
                children: RefCell<Vec<Weak<Node>>>,
            }

            impl Node {
                pub fn root(name: &str) -> Rc<Node> {
                    Rc::new(Node { name: name.to_string(), parent: None, children: RefCell::new(Vec::new()) })
                }

                pub fn add_child(self: &Rc<Self>, name: &str) -> Rc<Node> {
                    let child = Rc::new(Node {
                        name: name.to_string(),
                        parent: Some(Rc::clone(self)),
                        children: RefCell::new(Vec::new()),
                    });
                    self.children.borrow_mut().push(Rc::downgrade(&child));
                    child
                }

                pub fn parent_name(&self) -> Option<String> {
                    self.parent.as_ref().map(|p| p.name.to_string())
                }

                pub fn child_names(&self) -> Vec<String> {
                    self.children.borrow().iter().filter_map(|c| c.upgrade()).map(|c| c.name.to_string()).collect()
                }
            }
        """,
        everything_weak="""
            use std::cell::RefCell;
            use std::rc::{Rc, Weak};

            pub struct Node {
                pub name: String,
                parent: Weak<Node>,
                children: RefCell<Vec<Weak<Node>>>,
            }

            impl Node {
                pub fn root(name: &str) -> Rc<Node> {
                    Rc::new(Node { name: name.to_string(), parent: Weak::new(), children: RefCell::new(Vec::new()) })
                }

                pub fn add_child(self: &Rc<Self>, name: &str) -> Rc<Node> {
                    let child = Rc::new(Node {
                        name: name.to_string(),
                        parent: Rc::downgrade(self),
                        children: RefCell::new(Vec::new()),
                    });
                    self.children.borrow_mut().push(Rc::downgrade(&child));
                    child
                }

                pub fn parent_name(&self) -> Option<String> {
                    self.parent.upgrade().map(|p| p.name.to_string())
                }

                pub fn child_names(&self) -> Vec<String> {
                    self.children.borrow().iter().filter_map(|c| c.upgrade()).map(|c| c.name.to_string()).collect()
                }
            }
        """,
    ),
    hints=[("rust", "`Rc::strong_count` never reaches 0 for either node: each holds a strong reference to the other."),
           ("rust", "Parents own children; children only need to find their parent if it still exists. That's `Weak`."),
           ("rust", "`Weak::upgrade()` returns `Option<Rc<T>>`: `None` once the parent is gone.")],
    notes=("Ownership should point one way: down the tree. `Weak` back-pointers don't keep anything alive, and the `Option` from `upgrade` forces callers to handle a parent that's gone.", "O(1)", "O(n)"),
    follow_up="Compare this with the arena-allocated graph. When is `Rc`/`Weak` the better fit?",
    rules=dict(methods=["forget", "clone"]),
    related=["S7", "L7"],
))

# ---------------------------------------------------------------- flows & matching

P.append(dict(
    slug="bipartite-check", title="Bipartite check", level="medium", stage="flows-matching",
    tags=["2-colouring", "BFS", "Option<bool>"],
    teaches=["`Vec<Option<bool>>` as 'uncoloured / side A / side B'.", "Handling every component, not just node 0's."],
    statement="Return whether the undirected graph `adj` can be split into two sides with every edge crossing between them.",
    examples=[("adj = [[1, 3], [0, 2], [1, 3], [0, 2]]", "true"), ("adj = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]", "false")],
    starter="""
        pub fn is_bipartite(adj: &[Vec<usize>]) -> bool {
            todo!()
        }
    """,
    solution="""
        use std::collections::VecDeque;

        pub fn is_bipartite(adj: &[Vec<usize>]) -> bool {
            let mut side: Vec<Option<bool>> = vec![None; adj.len()];
            for start in 0..adj.len() {
                if side[start].is_some() {
                    continue;
                }
                side[start] = Some(false);
                let mut queue = VecDeque::from([start]);
                while let Some(u) = queue.pop_front() {
                    let s = side[u].expect("queued nodes are coloured");
                    for &v in &adj[u] {
                        match side[v] {
                            None => {
                                side[v] = Some(!s);
                                queue.push_back(v);
                            }
                            Some(t) if t == s => return false,
                            Some(_) => {}
                        }
                    }
                }
            }
            true
        }
    """,
    visible=[
        T("square", "adj = [[1, 3], [0, 2], [1, 3], [0, 2]]", "is_bipartite(&[vec![1, 3], vec![0, 2], vec![1, 3], vec![0, 2]])", "true"),
        T("triangle_inside", "adj = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]", "is_bipartite(&[vec![1, 2, 3], vec![0, 2], vec![0, 1, 3], vec![0, 2]])", "false"),
        T("single_edge", "adj = [[1], [0]]", "is_bipartite(&[vec![1], vec![0]])", "true"),
        T("lone_node", "adj = [[]]", "is_bipartite(&[vec![]])", "true"),
        T("odd_cycle_in_another_component", "adj = [[1], [0], [3, 4], [2, 4], [2, 3]]", "is_bipartite(&[vec![1], vec![0], vec![3, 4], vec![2, 4], vec![2, 3]])", "false"),
    ],
    hidden=[
        T("odd_cycle_elsewhere", "adj = [[], [2, 3], [1, 3], [1, 2]]", "is_bipartite(&[vec![], vec![2, 3], vec![1, 3], vec![1, 2]])", "false"),
        T("two_edges", "adj = [[1], [0], [3], [2]]", "is_bipartite(&[vec![1], vec![0], vec![3], vec![2]])", "true"),
        T("empty", "adj = []", "is_bipartite(&[])", "true"),
        T("self_loop", "adj = [[0]]", "is_bipartite(&[vec![0]])", "false"),
        T("five_cycle", "adj = [[1, 4], [0, 2], [1, 3], [2, 4], [3, 0]]", "is_bipartite(&[vec![1, 4], vec![0, 2], vec![1, 3], vec![2, 4], vec![3, 0]])", "false"),
        T("six_cycle", "cycle 0-1-2-3-4-5-0", "is_bipartite(&[vec![1, 5], vec![0, 2], vec![1, 3], vec![2, 4], vec![3, 5], vec![4, 0]])", "true"),
        T("repeated_edges", "adj = [[1, 1], [0, 0]]", "is_bipartite(&[vec![1, 1], vec![0, 0]])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(930);
            for _ in 0..300 {
                let n = 1 + rng.below(8);
                let m = rng.below(9);
                let mut adj = vec![Vec::new(); n];
                for _ in 0..m {
                    let (a, b) = (rng.below(n), rng.below(n));
                    adj[a].push(b);
                    if a != b {
                        adj[b].push(a);
                    }
                }
                // Brute force: try every 2-colouring.
                let want = (0..1u32 << n).any(|mask| (0..n).all(|u| adj[u].iter().all(|&v| (mask >> u & 1) != (mask >> v & 1))));
                check!(format!("adj = {adj:?}"), is_bipartite(&adj), want);
            }
        }

        #[test]
        fn scale_long_path() {
            let n: usize = 200_000;
            let adj: Vec<Vec<usize>> = (0..n).map(|u| [u.wrapping_sub(1), u + 1].into_iter().filter(|&v| v < n).collect()).collect();
            check!("path of 200000 nodes", is_bipartite(&adj), true);
        }

        #[test]
        fn scale_odd_cycle_far_away() {
            // A path of 199999 nodes whose last node closes a triangle with 199997.
            let n: usize = 200_000;
            let mut adj: Vec<Vec<usize>> = (0..n).map(|u| [u.wrapping_sub(1), u + 1].into_iter().filter(|&v| v < n).collect()).collect();
            adj[n - 1].push(n - 3);
            adj[n - 3].push(n - 1);
            check!("path of 200000 nodes plus the edge 199999-199997", is_bipartite(&adj), false);
        }
        """,
    ],
    wrong=dict(
        only_from_node_zero="""
            use std::collections::VecDeque;

            pub fn is_bipartite(adj: &[Vec<usize>]) -> bool {
                if adj.is_empty() {
                    return true;
                }
                let mut side: Vec<Option<bool>> = vec![None; adj.len()];
                side[0] = Some(false);
                let mut queue = VecDeque::from([0]);
                while let Some(u) = queue.pop_front() {
                    let s = side[u].unwrap();
                    for &v in &adj[u] {
                        match side[v] {
                            None => {
                                side[v] = Some(!s);
                                queue.push_back(v);
                            }
                            Some(t) if t == s => return false,
                            Some(_) => {}
                        }
                    }
                }
                true
            }
        """,
        recursive_dfs="""
            pub fn is_bipartite(adj: &[Vec<usize>]) -> bool {
                fn paint(u: usize, s: bool, adj: &[Vec<usize>], side: &mut [Option<bool>]) -> bool {
                    side[u] = Some(s);
                    for &v in &adj[u] {
                        match side[v] {
                            None => {
                                if !paint(v, !s, adj, side) {
                                    return false;
                                }
                            }
                            Some(t) if t == s => return false,
                            Some(_) => {}
                        }
                    }
                    true
                }
                let mut side = vec![None; adj.len()];
                (0..adj.len()).all(|u| side[u].is_some() || paint(u, false, adj, &mut side))
            }
        """,
    ),
    hints=[("approach", "Colour a node, give its neighbours the other colour, and look for an edge whose ends end up the same colour."),
           ("edge case", "The graph may be disconnected. Start a new search from every uncoloured node.")],
    notes=("A graph is bipartite exactly when it has no odd cycle, and BFS colouring finds one if it exists. `Option<bool>` says 'not yet coloured' without a magic number.", "O(V + E)", "O(V)"),
    follow_up="How would you return the odd cycle as evidence when the answer is false?",
    related=["S1"],
))

P.append(dict(
    slug="max-flow-with-edmonds-karp", title="Max flow with Edmonds-Karp", level="hard", stage="flows-matching",
    tags=["max flow", "residual graph", "edge arrays"],
    teaches=["Edges in flat Vecs with the reverse edge at `e ^ 1`.", "BFS augmenting paths, walked back through `via`."],
    statement="""
        Implement a flow network with directed capacities and compute the maximum flow from `s` to `t`
        (`s != t`) with Edmonds-Karp: repeatedly augment along a shortest path in the residual graph.
    """,
    examples=[("the CLRS network (6 nodes, 9 edges)", "23")],
    constraints=["n ≤ 500", "edges ≤ 5000"],
    starter="""
        pub struct FlowNetwork {
            adj: Vec<Vec<usize>>,
            to: Vec<usize>,
            cap: Vec<u64>,
        }

        impl FlowNetwork {
            pub fn new(n: usize) -> Self {
                todo!()
            }

            pub fn add_edge(&mut self, u: usize, v: usize, cap: u64) {
                todo!()
            }

            pub fn max_flow(&mut self, s: usize, t: usize) -> u64 {
                todo!()
            }
        }
    """,
    solution="""
        use std::collections::VecDeque;

        pub struct FlowNetwork {
            /// Edge ids leaving each node.
            adj: Vec<Vec<usize>>,
            to: Vec<usize>,
            /// Residual capacity. Edge `e ^ 1` is the reverse of edge `e`.
            cap: Vec<u64>,
        }

        impl FlowNetwork {
            pub fn new(n: usize) -> Self {
                FlowNetwork { adj: vec![Vec::new(); n], to: Vec::new(), cap: Vec::new() }
            }

            pub fn add_edge(&mut self, u: usize, v: usize, cap: u64) {
                self.adj[u].push(self.to.len());
                self.to.push(v);
                self.cap.push(cap);
                self.adj[v].push(self.to.len());
                self.to.push(u);
                self.cap.push(0);
            }

            pub fn max_flow(&mut self, s: usize, t: usize) -> u64 {
                let n = self.adj.len();
                let mut total = 0;
                loop {
                    let mut via: Vec<Option<usize>> = vec![None; n];
                    let mut seen = vec![false; n];
                    seen[s] = true;
                    let mut queue = VecDeque::from([s]);
                    while let Some(u) = queue.pop_front() {
                        for &e in &self.adj[u] {
                            let v = self.to[e];
                            if !seen[v] && self.cap[e] > 0 {
                                seen[v] = true;
                                via[v] = Some(e);
                                queue.push_back(v);
                            }
                        }
                    }
                    if !seen[t] {
                        return total;
                    }
                    let mut push = u64::MAX;
                    let mut v = t;
                    while let Some(e) = via[v] {
                        push = push.min(self.cap[e]);
                        v = self.to[e ^ 1];
                    }
                    let mut v = t;
                    while let Some(e) = via[v] {
                        self.cap[e] -= push;
                        self.cap[e ^ 1] += push;
                        v = self.to[e ^ 1];
                    }
                    total += push;
                }
            }
        }
    """,
    visible=[
        T("clrs", "CLRS network, s = 0, t = 5", "net.max_flow(0, 5)", "23",
          setup="let mut net = FlowNetwork::new(6);\nfor (u, v, c) in [(0, 1, 16), (0, 2, 13), (1, 3, 12), (2, 1, 4), (2, 4, 14), (3, 2, 9), (3, 5, 20), (4, 3, 7), (4, 5, 4)] {\n    net.add_edge(u, v, c);\n}"),
        T("needs_undo", "0→1 (1), 0→2 (1), 1→2 (1), 1→3 (1), 2→3 (1)", "net.max_flow(0, 3)", "2",
          setup="let mut net = FlowNetwork::new(4);\nfor (u, v, c) in [(0, 1, 1), (0, 2, 1), (1, 2, 1), (1, 3, 1), (2, 3, 1)] {\n    net.add_edge(u, v, c);\n}"),
        T("single_edge", "0→1 (5)", "net.max_flow(0, 1)", "5", setup="let mut net = FlowNetwork::new(2);\nnet.add_edge(0, 1, 5);"),
        T("bottleneck_in_series", "0→1 (10), 1→2 (3), 2→3 (10)", "net.max_flow(0, 3)", "3",
          setup="let mut net = FlowNetwork::new(4);\nnet.add_edge(0, 1, 10);\nnet.add_edge(1, 2, 3);\nnet.add_edge(2, 3, 10);"),
        T("edges_are_directed", "1→0 (5); flow from 0 to 1", "net.max_flow(0, 1)", "0", setup="let mut net = FlowNetwork::new(2);\nnet.add_edge(1, 0, 5);"),
    ],
    hidden=[
        T("shortest_path_must_be_undone", "0→1→2→3 is the shortest path, but both units need 1→4→5→3 and 0→6→7→2→3 (all capacity 1)", "net.max_flow(0, 3)", "2",
          setup="let mut net = FlowNetwork::new(8);\nfor (u, v) in [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (5, 3), (0, 6), (6, 7), (7, 2)] {\n    net.add_edge(u, v, 1);\n}"),
        T("zero_capacity", "0→1 (0), 1→2 (7)", "net.max_flow(0, 2)", "0", setup="let mut net = FlowNetwork::new(3);\nnet.add_edge(0, 1, 0);\nnet.add_edge(1, 2, 7);"),
        T("huge_capacities", "three parallel routes of 10¹⁵", "net.max_flow(0, 4)", "3_000_000_000_000_000",
          setup="let mut net = FlowNetwork::new(5);\nfor m in 1..=3 {\n    net.add_edge(0, m, 1_000_000_000_000_000);\n    net.add_edge(m, 4, 1_000_000_000_000_000);\n}"),
        T("source_after_sink", "3→1 (4), 1→0 (6), 3→0 (1); s = 3, t = 0", "net.max_flow(3, 0)", "5",
          setup="let mut net = FlowNetwork::new(4);\nnet.add_edge(3, 1, 4);\nnet.add_edge(1, 0, 6);\nnet.add_edge(3, 0, 1);"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(931);
            for _ in 0..300 {
                let n = 2 + rng.below(5);
                let m = rng.below(10);
                let edges: Vec<(usize, usize, u64)> = (0..m).map(|_| (rng.below(n), rng.below(n), rng.int(0, 9) as u64)).collect();
                let (s, t) = (0, n - 1);
                // Brute force: max flow equals the smallest cut, over every set holding s but not t.
                let want = (0..1usize << n)
                    .filter(|&mask| mask >> s & 1 == 1 && mask >> t & 1 == 0)
                    .map(|mask| edges.iter().filter(|&&(u, v, _)| mask >> u & 1 == 1 && mask >> v & 1 == 0).map(|e| e.2).sum::<u64>())
                    .min()
                    .unwrap();
                let mut net = FlowNetwork::new(n);
                for &(u, v, c) in &edges {
                    net.add_edge(u, v, c);
                }
                check!(format!("n = {n}, edges (u, v, cap) = {edges:?}, s = {s}, t = {t}"), net.max_flow(s, t), want);
            }
        }
        """,
        T("no_path", "0→1 (5), t = 2", "net.max_flow(0, 2)", "0", setup="let mut net = FlowNetwork::new(3);\nnet.add_edge(0, 1, 5);"),
        T("parallel", "two 0→1 edges (3 and 4)", "net.max_flow(0, 1)", "7", setup="let mut net = FlowNetwork::new(2);\nnet.add_edge(0, 1, 3);\nnet.add_edge(0, 1, 4);"),
        T("layered", "500 nodes in layers, capacity 1 per edge", "net.max_flow(0, 499)", "10",
          setup="let mut net = FlowNetwork::new(500);\nfor i in 0..10 {\n    net.add_edge(0, 1 + i, 1);\n    for layer in 0..48 {\n        net.add_edge(1 + layer * 10 + i, 1 + (layer + 1) * 10 + i, 1);\n    }\n    net.add_edge(1 + 48 * 10 + i, 499, 1);\n}"),
    ],
    wrong=dict(
        no_reverse_capacity="""
            use std::collections::VecDeque;

            pub struct FlowNetwork {
                /// Edge ids leaving each node.
                adj: Vec<Vec<usize>>,
                to: Vec<usize>,
                /// Residual capacity. Edge `e ^ 1` is the reverse of edge `e`.
                cap: Vec<u64>,
            }

            impl FlowNetwork {
                pub fn new(n: usize) -> Self {
                    FlowNetwork { adj: vec![Vec::new(); n], to: Vec::new(), cap: Vec::new() }
                }

                pub fn add_edge(&mut self, u: usize, v: usize, cap: u64) {
                    self.adj[u].push(self.to.len());
                    self.to.push(v);
                    self.cap.push(cap);
                    self.adj[v].push(self.to.len());
                    self.to.push(u);
                    self.cap.push(0);
                }

                pub fn max_flow(&mut self, s: usize, t: usize) -> u64 {
                    let n = self.adj.len();
                    let mut total = 0;
                    loop {
                        let mut via: Vec<Option<usize>> = vec![None; n];
                        let mut seen = vec![false; n];
                        seen[s] = true;
                        let mut queue = VecDeque::from([s]);
                        while let Some(u) = queue.pop_front() {
                            for &e in &self.adj[u] {
                                let v = self.to[e];
                                if !seen[v] && self.cap[e] > 0 {
                                    seen[v] = true;
                                    via[v] = Some(e);
                                    queue.push_back(v);
                                }
                            }
                        }
                        if !seen[t] {
                            return total;
                        }
                        let mut push = u64::MAX;
                        let mut v = t;
                        while let Some(e) = via[v] {
                            push = push.min(self.cap[e]);
                            v = self.to[e ^ 1];
                        }
                        let mut v = t;
                        while let Some(e) = via[v] {
                            self.cap[e] -= push;
                            v = self.to[e ^ 1];
                        }
                        total += push;
                    }
                }
            }
        """,
        walks_back_along_the_wrong_end="""
            use std::collections::VecDeque;

            pub struct FlowNetwork {
                /// Edge ids leaving each node.
                adj: Vec<Vec<usize>>,
                to: Vec<usize>,
                /// Residual capacity. Edge `e ^ 1` is the reverse of edge `e`.
                cap: Vec<u64>,
            }

            impl FlowNetwork {
                pub fn new(n: usize) -> Self {
                    FlowNetwork { adj: vec![Vec::new(); n], to: Vec::new(), cap: Vec::new() }
                }

                pub fn add_edge(&mut self, u: usize, v: usize, cap: u64) {
                    self.adj[u].push(self.to.len());
                    self.to.push(v);
                    self.cap.push(cap);
                    self.adj[v].push(self.to.len());
                    self.to.push(u);
                    self.cap.push(0);
                }

                pub fn max_flow(&mut self, s: usize, t: usize) -> u64 {
                    let n = self.adj.len();
                    let mut total = 0;
                    loop {
                        let mut via: Vec<Option<usize>> = vec![None; n];
                        let mut seen = vec![false; n];
                        seen[s] = true;
                        let mut queue = VecDeque::from([s]);
                        while let Some(u) = queue.pop_front() {
                            for &e in &self.adj[u] {
                                let v = self.to[e];
                                if !seen[v] && self.cap[e] > 0 {
                                    seen[v] = true;
                                    via[v] = Some(e);
                                    queue.push_back(v);
                                }
                            }
                        }
                        if !seen[t] {
                            return total;
                        }
                        let mut push = u64::MAX;
                        let mut v = t;
                        while let Some(e) = via[v] {
                            push = push.min(self.cap[e]);
                            v = self.to[e];
                        }
                        let mut v = t;
                        while let Some(e) = via[v] {
                            self.cap[e] -= push;
                            self.cap[e ^ 1] += push;
                            v = self.to[e ^ 1];
                        }
                        total += push;
                    }
                }
            }
        """,
    ),
    hints=[("approach", "Find any s→t path with spare capacity (BFS for the shortest), push its bottleneck, and repeat until none is left."),
           ("approach", "Pushing flow along u→v adds capacity to v→u, so later paths can undo earlier choices."),
           ("rust", "Keep edges in parallel Vecs and add each edge with its reverse, so the reverse of `e` is `e ^ 1`. No references between edges needed.")],
    notes=("Flat edge arrays sidestep the borrow checker: edges refer to each other by id. BFS paths bound the number of augmentations by O(VE).", "O(V · E²)", "O(V + E)"),
    follow_up="After computing the flow, how would you find the minimum cut?",
))

P.append(dict(
    slug="hopcroft-karp-matching", title="Hopcroft-Karp matching", level="hard", stage="flows-matching",
    tags=["bipartite matching", "BFS layers"],
    teaches=["BFS to layer the graph, then DFS for augmenting paths along those layers.", "A per-node edge cursor so each edge is tried once per phase."],
    statement="""
        `edges` join left nodes `0..left` to right nodes `0..right`. Return the size of a maximum matching.
        The hidden tests go up to 5000 right nodes and 505,000 left nodes, so augmenting one path at a time is too slow in the worst case.
    """,
    examples=[("left = 3, right = 3, edges = [(0,0), (0,1), (1,0), (2,1)]", "2")],
    starter="""
        pub fn max_matching(left: usize, right: usize, edges: &[(usize, usize)]) -> usize {
            todo!()
        }
    """,
    solution="""
        use std::collections::VecDeque;

        struct Matcher {
            adj: Vec<Vec<usize>>,
            match_l: Vec<Option<usize>>,
            match_r: Vec<Option<usize>>,
            dist: Vec<u32>,
            cursor: Vec<usize>,
        }

        impl Matcher {
            /// Layers the left side by BFS from free left nodes. True if some free right node is reachable.
            fn layer(&mut self) -> bool {
                let mut queue = VecDeque::new();
                for u in 0..self.adj.len() {
                    if self.match_l[u].is_none() {
                        self.dist[u] = 0;
                        queue.push_back(u);
                    } else {
                        self.dist[u] = u32::MAX;
                    }
                }
                let mut found = false;
                while let Some(u) = queue.pop_front() {
                    for &v in &self.adj[u] {
                        match self.match_r[v] {
                            None => found = true,
                            Some(w) if self.dist[w] == u32::MAX => {
                                self.dist[w] = self.dist[u] + 1;
                                queue.push_back(w);
                            }
                            Some(_) => {}
                        }
                    }
                }
                found
            }

            fn augment(&mut self, u: usize) -> bool {
                while self.cursor[u] < self.adj[u].len() {
                    let v = self.adj[u][self.cursor[u]];
                    self.cursor[u] += 1;
                    let ok = match self.match_r[v] {
                        None => true,
                        Some(w) => self.dist[w] == self.dist[u] + 1 && self.augment(w),
                    };
                    if ok {
                        self.match_l[u] = Some(v);
                        self.match_r[v] = Some(u);
                        return true;
                    }
                }
                self.dist[u] = u32::MAX;
                false
            }
        }

        pub fn max_matching(left: usize, right: usize, edges: &[(usize, usize)]) -> usize {
            let mut adj = vec![Vec::new(); left];
            for &(u, v) in edges {
                adj[u].push(v);
            }
            let mut m = Matcher { adj, match_l: vec![None; left], match_r: vec![None; right], dist: vec![0; left], cursor: vec![0; left] };
            let mut size = 0;
            while m.layer() {
                m.cursor.fill(0);
                for u in 0..left {
                    if m.match_l[u].is_none() && m.augment(u) {
                        size += 1;
                    }
                }
            }
            size
        }
    """,
    visible=[
        T("two", "left = 3, right = 3, edges = [(0,0), (0,1), (1,0), (2,1)]", "max_matching(3, 3, &[(0, 0), (0, 1), (1, 0), (2, 1)])", "2"),
        T("rematch", "left = 2, right = 2, edges = [(0,0), (0,1), (1,0)]", "max_matching(2, 2, &[(0, 0), (0, 1), (1, 0)])", "2"),
        T("one_edge", "left = 1, right = 1, edges = [(0,0)]", "max_matching(1, 1, &[(0, 0)])", "1"),
        T("many_want_the_same_right_node", "left = 3, right = 1, edges = [(0,0), (1,0), (2,0)]", "max_matching(3, 1, &[(0, 0), (1, 0), (2, 0)])", "1"),
        T("empty_left_side", "left = 0, right = 2, edges = []", "max_matching(0, 2, &[])", "0"),
    ],
    hidden=[
        T("no_edges", "left = 3, right = 2, edges = []", "max_matching(3, 2, &[])", "0"),
        T("duplicate_edges", "left = 1, right = 1, edges = [(0,0), (0,0)]", "max_matching(1, 1, &[(0, 0), (0, 0)])", "1"),
        T("long_augmenting_path", "left = 4, right = 4, edges = [(0,0), (1,0), (1,1), (2,1), (2,2), (3,2), (3,3)] listed so greedy picks badly",
          "max_matching(4, 4, &[(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 3)])", "4"),
        T("isolated_right_nodes", "left = 2, right = 5, edges = [(0,4), (1,4)]", "max_matching(2, 5, &[(0, 4), (1, 4)])", "1"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn try_kuhn(u: usize, adj: &[Vec<usize>], seen: &mut [bool], owner: &mut [Option<usize>]) -> bool {
                for &v in &adj[u] {
                    if !seen[v] {
                        seen[v] = true;
                        if owner[v].is_none_or(|w| try_kuhn(w, adj, seen, owner)) {
                            owner[v] = Some(u);
                            return true;
                        }
                    }
                }
                false
            }
            let mut rng = anneal_prelude::Rng::new(932);
            for _ in 0..300 {
                let (left, right) = (rng.below(6), 1 + rng.below(6));
                let m = if left == 0 { 0 } else { rng.below(12) };
                let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(left), rng.below(right))).collect();
                // Reference: Kuhn's algorithm, one augmenting path at a time.
                let mut adj = vec![Vec::new(); left];
                for &(u, v) in &edges {
                    adj[u].push(v);
                }
                let mut owner = vec![None; right];
                let want = (0..left).filter(|&u| try_kuhn(u, &adj, &mut vec![false; right], &mut owner)).count();
                check!(format!("left = {left}, right = {right}, edges = {edges:?}"), max_matching(left, right, &edges), want);
            }
        }

        #[test]
        fn scale_staircase_2500() {
            // Left i joins right 0..=i, lowest first: one augmenting path at a time costs O(V³).
            let n = 2500;
            let edges: Vec<(usize, usize)> = (0..n).flat_map(|i| (0..=i).map(move |j| (i, j))).collect();
            check!("left = right = 2500, left i joined to right 0..=i", max_matching(n, n, &edges), n);
        }

        #[test]
        fn scale_many_hopeless_left_nodes() {
            // Left i < 5000 joins right i and i + 1, so the first 5000 match perfectly. Then 500000 more left nodes
            // all want right 0: each one-path-at-a-time search walks the whole chain and fails.
            let k = 5000;
            let mut edges: Vec<(usize, usize)> = (0..k).flat_map(|i| if i + 1 < k { vec![(i, i), (i, i + 1)] } else { vec![(i, i)] }).collect();
            edges.extend((k..k + 500_000).map(|u| (u, 0)));
            check!("left = 505000, right = 5000: a chain of 5000, then 500000 left nodes joined only to right 0", max_matching(k + 500_000, k, &edges), k);
        }
        """,
        T("perfect_ring", "5000 × 5000, i → i and i → i + 1", "max_matching(5000, 5000, &edges)", "5000",
          setup="let edges: Vec<(usize, usize)> = (0..5000).flat_map(|i| [(i, (i + 1) % 5000), (i, i)]).collect();"),
        T("dense_block", "5000 × 5000, each left node to 20 right nodes", "max_matching(5000, 5000, &edges)", "5000",
          setup="let edges: Vec<(usize, usize)> = (0..5000).flat_map(|i| (0..20).map(move |k| (i, (i * 7 + k * 251) % 5000))).collect();"),
    ],
    wrong=dict(
        one_path_at_a_time="""
            pub fn max_matching(left: usize, right: usize, edges: &[(usize, usize)]) -> usize {
                fn augment(u: usize, adj: &[Vec<usize>], seen: &mut [bool], owner: &mut [Option<usize>]) -> bool {
                    for &v in &adj[u] {
                        if !seen[v] {
                            seen[v] = true;
                            if owner[v].is_none_or(|w| augment(w, adj, seen, owner)) {
                                owner[v] = Some(u);
                                return true;
                            }
                        }
                    }
                    false
                }
                let mut adj = vec![Vec::new(); left];
                for &(u, v) in edges {
                    adj[u].push(v);
                }
                let mut owner = vec![None; right];
                (0..left).filter(|&u| augment(u, &adj, &mut vec![false; right], &mut owner)).count()
            }
        """,
        greedy="""
            pub fn max_matching(left: usize, right: usize, edges: &[(usize, usize)]) -> usize {
                let mut used_l = vec![false; left];
                let mut used_r = vec![false; right];
                let mut size = 0;
                for &(u, v) in edges {
                    if !used_l[u] && !used_r[v] {
                        used_l[u] = true;
                        used_r[v] = true;
                        size += 1;
                    }
                }
                size
            }
        """,
    ),
    hints=[("approach", "One phase: BFS from all free left nodes to get layers, then DFS from each free left node, only stepping to the next layer."),
           ("approach", "A left node whose DFS fails gets its layer cleared (`dist = MAX`) so no one retries it this phase."),
           ("rust", "A struct with `match_l`, `match_r`, `dist` and a cursor per node keeps `augment(&mut self, u)` to one parameter.")],
    notes=("Each phase finds a maximal set of shortest augmenting paths, and there are only O(√V) phases. The cursor makes each phase's DFS O(E) in total.", "O(E √V)", "O(V + E)"),
    follow_up="How does bipartite matching reduce to max flow, and why is Hopcroft-Karp faster than Edmonds-Karp on that network?",
))

P.append(dict(
    slug="min-cost-flow", title="Min-cost flow", level="hard", stage="flows-matching",
    tags=["min-cost flow", "SPFA", "negative residual costs"],
    teaches=["Successive shortest paths on a residual graph with negative reverse costs.", "Bellman–Ford with a queue (SPFA)."],
    statement="""
        Each edge `(u, v, capacity, cost)` carries up to `capacity` units at `cost` per unit. Return the least
        total cost of sending exactly `want` units from `s` to `t`, or `None` if that much can't get through.
        Costs are non-negative.
    """,
    examples=[("n = 4, edges = [(0,1,2,1), (0,2,1,2), (1,2,1,1), (1,3,1,3), (2,3,2,1)], s = 0, t = 3, want = 2", "Some(6)")],
    constraints=["n ≤ 200", "edges ≤ 2000", "want ≤ 10⁴"],
    starter="""
        pub fn min_cost_flow(n: usize, edges: &[(usize, usize, u32, i64)], s: usize, t: usize, want: u32) -> Option<i64> {
            todo!()
        }
    """,
    solution="""
        use std::collections::VecDeque;

        pub fn min_cost_flow(n: usize, edges: &[(usize, usize, u32, i64)], s: usize, t: usize, want: u32) -> Option<i64> {
            let mut adj = vec![Vec::new(); n];
            let (mut to, mut cap, mut cost) = (Vec::new(), Vec::new(), Vec::new());
            for &(u, v, c, w) in edges {
                adj[u].push(to.len());
                to.push(v);
                cap.push(c);
                cost.push(w);
                adj[v].push(to.len());
                to.push(u);
                cap.push(0);
                cost.push(-w);
            }

            let (mut sent, mut total) = (0u32, 0i64);
            while sent < want {
                // Cheapest path in the residual graph; reverse edges have negative cost.
                let mut dist = vec![i64::MAX; n];
                let mut via: Vec<Option<usize>> = vec![None; n];
                let mut queued = vec![false; n];
                dist[s] = 0;
                let mut queue = VecDeque::from([s]);
                while let Some(u) = queue.pop_front() {
                    queued[u] = false;
                    for &e in &adj[u] {
                        let v = to[e];
                        if cap[e] > 0 && dist[u] + cost[e] < dist[v] {
                            dist[v] = dist[u] + cost[e];
                            via[v] = Some(e);
                            if !queued[v] {
                                queued[v] = true;
                                queue.push_back(v);
                            }
                        }
                    }
                }
                if dist[t] == i64::MAX {
                    return None;
                }

                let mut push = want - sent;
                let mut v = t;
                while let Some(e) = via[v] {
                    push = push.min(cap[e]);
                    v = to[e ^ 1];
                }
                let mut v = t;
                while let Some(e) = via[v] {
                    cap[e] -= push;
                    cap[e ^ 1] += push;
                    v = to[e ^ 1];
                }
                sent += push;
                total += dist[t] * i64::from(push);
            }
            Some(total)
        }
    """,
    visible=[
        T("two_units", "n = 4, edges = [(0,1,2,1), (0,2,1,2), (1,2,1,1), (1,3,1,3), (2,3,2,1)], want = 2",
          "min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 2)", "Some(6)"),
        T("too_much", "same network, want = 4", "min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 4)", "None"),
        T("one_unit", "same network, want = 1", "min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 1)", "Some(3)"),
        T("nothing_wanted", "n = 3, edges = [], want = 0", "min_cost_flow(3, &[], 0, 2, 0)", "Some(0)"),
        T("cheap_edge_fills_first", "n = 2, edges = [(0,1,1,5), (0,1,2,3)], want = 3", "min_cost_flow(2, &[(0, 1, 1, 5), (0, 1, 2, 3)], 0, 1, 3)", "Some(11)"),
    ],
    hidden=[
        T("three_units", "same network, want = 3", "min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 3)", "Some(10)"),
        T("nothing", "want = 0", "min_cost_flow(2, &[], 0, 1, 0)", "Some(0)"),
        T("reroute", "greedy first path must be partly undone",
          "min_cost_flow(4, &[(0, 1, 1, 1), (0, 2, 1, 5), (1, 2, 1, 1), (1, 3, 1, 5), (2, 3, 1, 1)], 0, 3, 2)", "Some(12)"),
        T("zero_costs", "n = 3, edges = [(0,1,5,0), (1,2,5,0)], want = 5", "min_cost_flow(3, &[(0, 1, 5, 0), (1, 2, 5, 0)], 0, 2, 5)", "Some(0)"),
        T("one_edge_full", "n = 2, edges = [(0,1,10000,7)], want = 10000", "min_cost_flow(2, &[(0, 1, 10_000, 7)], 0, 1, 10_000)", "Some(70_000)"),
        T("one_short", "n = 2, edges = [(0,1,10000,7)], want = 10001", "min_cost_flow(2, &[(0, 1, 10_000, 7)], 0, 1, 10_001)", "None"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(933);
            for _ in 0..300 {
                let n = 2 + rng.below(3);
                let m = rng.below(6);
                let edges: Vec<(usize, usize, u32, i64)> = (0..m).map(|_| (rng.below(n), rng.below(n), rng.int(0, 2) as u32, rng.int(0, 5))).collect();
                let want_units = rng.int(0, 3) as u32;
                let (s, t) = (0, n - 1);
                // Brute force: try every integer flow on every edge; keep the cheapest that balances.
                let mut want: Option<i64> = None;
                let combos: u32 = edges.iter().map(|e| e.2 + 1).product();
                for mut code in 0..combos {
                    let mut net = vec![0i64; n];
                    let mut cost = 0;
                    for &(u, v, c, w) in &edges {
                        let f = (code % (c + 1)) as i64;
                        code /= c + 1;
                        net[u] += f;
                        net[v] -= f;
                        cost += f * w;
                    }
                    let balanced = (0..n).all(|x| net[x] == if x == s { want_units as i64 } else if x == t { -(want_units as i64) } else { 0 });
                    if balanced && want.is_none_or(|b| cost < b) {
                        want = Some(cost);
                    }
                }
                check!(format!("n = {n}, edges (u, v, cap, cost) = {edges:?}, s = {s}, t = {t}, want = {want_units}"), min_cost_flow(n, &edges, s, t, want_units), want);
            }
        }

        #[test]
        fn scale_200_nodes_2000_edges() {
            let mut x: u64 = 99;
            let mut next = || { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); x >> 33 };
            let mut edges = Vec::new();
            for _ in 0..2000 {
                let u = (next() % 200) as usize;
                let v = (next() % 200) as usize;
                let cap = (1000 + next() % 3000) as u32;
                let cost = (next() % 100) as i64;
                edges.push((u, v, cap, cost));
            }
            check!("n = 200, 2000 pseudo-random edges (LCG seed 99), s = 0, t = 199, want = 10000", min_cost_flow(200, &edges, 0, 199, 10_000), Some(911_390));
        }
        """,
    ],
    wrong=dict(
        no_reverse_edges="""
            use std::collections::VecDeque;

            pub fn min_cost_flow(n: usize, edges: &[(usize, usize, u32, i64)], s: usize, t: usize, want: u32) -> Option<i64> {
                let mut adj = vec![Vec::new(); n];
                let mut cap: Vec<u32> = Vec::new();
                for (e, &(u, _, c, _)) in edges.iter().enumerate() {
                    adj[u].push(e);
                    cap.push(c);
                }
                let (mut sent, mut total) = (0u32, 0i64);
                while sent < want {
                    let mut dist = vec![i64::MAX; n];
                    let mut via: Vec<Option<usize>> = vec![None; n];
                    dist[s] = 0;
                    let mut queue = VecDeque::from([s]);
                    while let Some(u) = queue.pop_front() {
                        for &e in &adj[u] {
                            let (_, v, _, w) = edges[e];
                            if cap[e] > 0 && dist[u] + w < dist[v] {
                                dist[v] = dist[u] + w;
                                via[v] = Some(e);
                                queue.push_back(v);
                            }
                        }
                    }
                    if dist[t] == i64::MAX {
                        return None;
                    }
                    let mut push = want - sent;
                    let mut v = t;
                    while let Some(e) = via[v] {
                        push = push.min(cap[e]);
                        v = edges[e].0;
                    }
                    let mut v = t;
                    while let Some(e) = via[v] {
                        cap[e] -= push;
                        v = edges[e].0;
                    }
                    sent += push;
                    total += dist[t] * i64::from(push);
                }
                Some(total)
            }
        """,
        cost_per_path_not_per_unit="""
            use std::collections::VecDeque;

            pub fn min_cost_flow(n: usize, edges: &[(usize, usize, u32, i64)], s: usize, t: usize, want: u32) -> Option<i64> {
                let mut adj = vec![Vec::new(); n];
                let (mut to, mut cap, mut cost) = (Vec::new(), Vec::new(), Vec::new());
                for &(u, v, c, w) in edges {
                    adj[u].push(to.len());
                    to.push(v);
                    cap.push(c);
                    cost.push(w);
                    adj[v].push(to.len());
                    to.push(u);
                    cap.push(0);
                    cost.push(-w);
                }
                let (mut sent, mut total) = (0u32, 0i64);
                while sent < want {
                    let mut dist = vec![i64::MAX; n];
                    let mut via: Vec<Option<usize>> = vec![None; n];
                    let mut queued = vec![false; n];
                    dist[s] = 0;
                    let mut queue = VecDeque::from([s]);
                    while let Some(u) = queue.pop_front() {
                        queued[u] = false;
                        for &e in &adj[u] {
                            let v = to[e];
                            if cap[e] > 0 && dist[u] + cost[e] < dist[v] {
                                dist[v] = dist[u] + cost[e];
                                via[v] = Some(e);
                                if !queued[v] {
                                    queued[v] = true;
                                    queue.push_back(v);
                                }
                            }
                        }
                    }
                    if dist[t] == i64::MAX {
                        return None;
                    }
                    let mut push = want - sent;
                    let mut v = t;
                    while let Some(e) = via[v] {
                        push = push.min(cap[e]);
                        v = to[e ^ 1];
                    }
                    let mut v = t;
                    while let Some(e) = via[v] {
                        cap[e] -= push;
                        cap[e ^ 1] += push;
                        v = to[e ^ 1];
                    }
                    sent += push;
                    total += dist[t];
                }
                Some(total)
            }
        """,
    ),
    hints=[("approach", "Repeatedly send flow along the cheapest s→t path in the residual graph, as much as its bottleneck allows."),
           ("approach", "A reverse edge refunds the cost, so it has cost −w. Dijkstra can't handle that directly; Bellman–Ford (SPFA) can."),
           ("rust", "Same flat-edge layout as Edmonds-Karp: reverse of `e` is `e ^ 1`, with `cost[e ^ 1] = -cost[e]`.")],
    notes=("Successive shortest paths stays optimal because the residual graph never has a negative cycle. Johnson potentials would let you use Dijkstra instead of SPFA.", "O(F · V · E)", "O(V + E)"),
    follow_up="Add Johnson potentials so each round can use Dijkstra. What invariant makes the reduced costs non-negative?",
))

STAGES = [
    ("representation", "Representation", "easy"),
    ("traversal", "Traversal", "easy"),
    ("topological-sort", "Topological sort", "medium"),
    ("shortest-paths", "Shortest paths", "medium"),
    ("union-find-mst", "Union-find & MST", "medium"),
    ("scc-bridges-arenas", "SCC, bridges & arenas", "hard"),
    ("flows-matching", "Flows & matching", "hard"),
]

if __name__ == "__main__":
    n = write_track("d9-graphs", "D9", "Graphs", "D", "core", 7,
                    "Index-based graphs, from adjacency lists to max-flow. Nodes that point at each other can't all own each other.",
                    STAGES, P, keep={"network-delay-time"})
    print("D9", n)
