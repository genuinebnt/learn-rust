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
