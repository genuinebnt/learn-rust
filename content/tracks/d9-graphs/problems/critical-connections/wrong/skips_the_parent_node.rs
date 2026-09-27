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
