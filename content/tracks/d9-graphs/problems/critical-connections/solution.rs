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
